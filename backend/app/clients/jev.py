import logging
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

QuestionType = Literal["noul", "choice", "score"]


class JevUnavailableError(Exception):
    pass


class Question(BaseModel):
    type: QuestionType
    instructions: str
    criteria: dict[str, str]


class Answer(BaseModel):
    type: QuestionType
    noul: float | None = None
    choice: str | None = None
    probabilities: dict[str, float] = {}
    confidence: float | None = None


class Decision(BaseModel):
    model: str
    answers: dict[str, Answer]


class JevClient:
    def __init__(
        self, api_key: str | None, base_url: str, model: str, timeout_seconds: float
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._http = httpx.Client(base_url=base_url, timeout=timeout_seconds)

    def decide(self, state: dict[str, Any], questions: dict[str, Question]) -> Decision:
        if not self._api_key:
            raise JevUnavailableError("NEWS_JEV_API_KEY is not set")
        body = {
            "model": self._model,
            "state": state,
            "questions": {name: question.model_dump() for name, question in questions.items()},
        }
        try:
            response = self._http.post(
                "/v1/systemone",
                json=body,
                headers={"Authorization": f"Bearer {self._api_key}"},
            )
            response.raise_for_status()
            decision = Decision.model_validate(response.json())
        except (httpx.HTTPError, ValueError, ValidationError) as error:
            logger.warning("Jev call failed: %s", error)
            raise JevUnavailableError(str(error)) from error
        missing = questions.keys() - decision.answers.keys()
        if missing:
            raise JevUnavailableError(f"Jev did not answer {sorted(missing)}")
        return decision

    def close(self) -> None:
        self._http.close()
