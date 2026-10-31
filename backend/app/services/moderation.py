from dataclasses import asdict, dataclass

from app.clients.jev import Decision, JevClient, JevUnavailableError, Question
from app.db.repositories.search import ShortlistEntry

NO_DUPLICATE = "none"

HARM = Question(
    type="noul",
    instructions="Does this text contain harmful language?",
    criteria={
        "true": "Threats, self-harm or scam wording. Uncensored language is allowed.",
        "false": "Normal wording, including swearing.",
    },
)


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
    duplicate_of_id: int | None = None
    duplicate_probability: float = 0.0


def judge_comment(client: JevClient, text: str) -> Verdict:
    decision = client.decide({"comment": {"text": text}}, {"harm": HARM})
    return Verdict(decision.model, _harm(decision))


def judge_post(client: JevClient, submission: Submission, earlier: list[ShortlistEntry]) -> Verdict:
    questions = {"harm": HARM}
    if earlier:
        questions["duplicate"] = _duplicate_question(earlier)
    stories = [
        {"id": f"item-{story.id}", "title": story.title, "summary": story.summary}
        for story in earlier
    ]
    state = {"submission": asdict(submission), "earlier_stories": stories}
    decision = client.decide(state, questions)
    return Verdict(decision.model, _harm(decision), *_duplicate(decision, earlier))


def _duplicate_question(earlier: list[ShortlistEntry]) -> Question:
    return Question(
        type="choice",
        instructions="Which earlier story reports the same event as the submission?",
        criteria={
            **{f"item-{story.id}": story.title for story in earlier},
            NO_DUPLICATE: "None of them.",
        },
    )


def _harm(decision: Decision) -> float:
    probability = decision.answers["harm"].noul
    if probability is None or not 0 <= probability <= 1:
        raise JevUnavailableError("Jev gave no harm probability")
    return probability


def _duplicate(decision: Decision, earlier: list[ShortlistEntry]) -> tuple[int | None, float]:
    if not earlier:
        return None, 0.0
    answer = decision.answers["duplicate"]
    choice = answer.choice or ""
    probability = answer.probabilities.get(choice, 0.0)
    if choice == NO_DUPLICATE:
        return None, probability
    ids = {f"item-{story.id}": story.id for story in earlier}
    if choice not in ids:
        raise JevUnavailableError(f"Jev picked {choice!r}, which is not on the shortlist")
    return ids[choice], probability
