from dataclasses import dataclass
from typing import Any

from app.clients.jev import Answer, Decision, JevClient, JevUnavailableError, Question
from app.db.repositories.search import ShortlistEntry

NO_DUPLICATE = "none"


@dataclass(frozen=True, slots=True)
class Submission:
    title: str
    summary: str | None
    source_name: str | None
    username: str | None
    label: str | None
    domain: str


@dataclass(frozen=True, slots=True)
class Verdict:
    model: str
    harm_probability: float
    duplicate_of_id: int | None
    duplicate_probability: float


def judge(
    client: JevClient,
    submission: Submission,
    shortlist: list[ShortlistEntry],
) -> Verdict:
    decision = client.decide(_state(submission, shortlist), _questions(shortlist))
    try:
        return _verdict(decision, {entry.id for entry in shortlist})
    except (KeyError, ValueError) as error:
        raise JevUnavailableError(f"Unexpected Jev answer: {error}") from error


def _verdict(decision: Decision, shortlist_ids: set[int]) -> Verdict:
    answers = decision.answers
    harm = answers["harm"].noul
    if harm is None:
        raise ValueError("harm has no probability")
    duplicate_of_id = None
    duplicate_probability = 0.0
    if shortlist_ids:
        choice, duplicate_probability = _choice(answers["duplicate"])
        if choice != NO_DUPLICATE:
            duplicate_of_id = int(choice.removeprefix("item-"))
            if duplicate_of_id not in shortlist_ids:
                raise ValueError(f"duplicate {choice} is not on the shortlist")
    return Verdict(
        model=decision.model,
        harm_probability=harm,
        duplicate_of_id=duplicate_of_id,
        duplicate_probability=duplicate_probability,
    )


def _choice(answer: Answer) -> tuple[str, float]:
    choice = answer.choice or ""
    return choice, answer.probabilities.get(choice, 0.0)


def _state(submission: Submission, shortlist: list[ShortlistEntry]) -> dict[str, Any]:
    return {
        "submission": {
            "title": submission.title,
            "summary": submission.summary,
            "source_name": submission.source_name,
            "username": submission.username,
            "label": submission.label,
            "domain": submission.domain,
        },
        "earlier_stories": [
            {"id": f"item-{entry.id}", "title": entry.title, "summary": entry.summary}
            for entry in shortlist
        ],
    }


def _questions(shortlist: list[ShortlistEntry]) -> dict[str, Question]:
    questions = {
        "harm": Question(
            type="noul",
            instructions="Does the submission contain harmful language?",
            criteria={
                "true": "Hate, harassment, threats, sexual content, self-harm or scam wording.",
                "false": "Normal news wording.",
            },
        ),
    }
    if shortlist:
        questions["duplicate"] = Question(
            type="choice",
            instructions="Which earlier story reports the same event as the submission?",
            criteria={
                **{f"item-{entry.id}": entry.title for entry in shortlist},
                NO_DUPLICATE: "None of them.",
            },
        )
    return questions
