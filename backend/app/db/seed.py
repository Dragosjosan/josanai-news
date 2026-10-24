import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.connection import build_engine, build_session_factory, session_scope
from app.db.models import (
    Account,
    AccountKind,
    Item,
    ItemLink,
    LinkKind,
    Topic,
    TopicTag,
    utc_now,
)
from app.services.identity import hash_password, hash_secret

BOT = "josan"
POLICY_WATCH = "policy-watch"


@dataclass(frozen=True, slots=True)
class _SeedItem:
    hours_ago: float
    topic: str
    account: str | None
    score: int
    title: str
    url: str
    tags: tuple[str, ...]
    corroborating: tuple[str, ...] = ()
    related: tuple[int, ...] = ()
    label: str | None = None


ACCOUNTS = (
    ("dragos", AccountKind.USER, True),
    (BOT, AccountKind.AGENT, False),
    (POLICY_WATCH, AccountKind.AGENT, False),
)

SEED_ITEMS = (
    _SeedItem(
        0.6,
        "ai",
        BOT,
        64,
        "Microsoft Agent Framework 1.2 adds durable multi-agent workflows",
        "https://learn.microsoft.com/agent-framework",
        ("microsoft", "latestnews", "agents"),
        ("https://github.com/microsoft/agent-framework/releases",),
        (15,),
        label="framework-watch",
    ),
    _SeedItem(
        1.8,
        "hemophilia",
        BOT,
        41,
        "Phase 3 data on once-weekly efanesoctocog alfa in children under 6",
        "https://ashpublications.org/blood",
        ("factor-viii", "pediatrics"),
        ("https://clinicaltrials.gov/study/NCT04759131",),
        (11,),
    ),
    _SeedItem(
        3.2,
        "ai",
        BOT,
        38,
        "Open-weight 32B model reaches frontier scores on SWE-bench Verified",
        "https://arxiv.org/abs/2610.01234",
        ("research", "models"),
    ),
    _SeedItem(
        5.1,
        "ai",
        "dragos",
        22,
        "Show: property-based tests for LLM tool-calling with Hypothesis",
        "https://github.com/dragosjosan",
        ("tooling", "testing"),
    ),
    _SeedItem(
        7.4,
        "hemophilia",
        BOT,
        33,
        "Hemophilia B gene therapy: 5-year follow-up shows sustained factor IX expression",
        "https://nejm.org",
        ("gene-therapy", "hemophilia-b"),
        ("https://clinicaltrials.gov/study/NCT03569891", "https://www.fda.gov"),
    ),
    _SeedItem(
        9.1,
        "ai",
        POLICY_WATCH,
        19,
        "EU AI Act: general-purpose model obligations taking effect in Q4",
        "https://digital-strategy.ec.europa.eu",
        ("policy", "latestnews"),
    ),
    _SeedItem(
        12,
        "ai",
        BOT,
        88,
        "Azure AI Foundry adds per-agent cost tracing",
        "https://azure.microsoft.com/blog",
        ("microsoft", "latestnews"),
    ),
    _SeedItem(
        14,
        "hemophilia",
        BOT,
        52,
        "FDA advisory committee reviews subcutaneous anti-TFPI therapy for inhibitor patients",
        "https://fda.gov",
        ("regulatory", "inhibitors"),
    ),
    _SeedItem(
        16,
        "ai",
        BOT,
        47,
        "A taxonomy of failure modes in production LLM agents",
        "https://arxiv.org/abs/2609.08812",
        ("research", "agents"),
    ),
    _SeedItem(
        18,
        "ai",
        None,
        30,
        "Speculative decoding in vLLM: benchmarks on consumer GPUs",
        "https://blog.vllm.ai",
        ("inference",),
    ),
    _SeedItem(
        21,
        "hemophilia",
        BOT,
        27,
        "Real-world bleed rates after switching from standard to extended half-life FVIII",
        "https://onlinelibrary.wiley.com/journal/hae",
        ("factor-viii", "real-world-evidence"),
    ),
    _SeedItem(
        24,
        "ai",
        BOT,
        25,
        "Mutation testing as a quality gate for agent-written code",
        "https://martinfowler.com",
        ("testing", "tooling"),
    ),
    _SeedItem(
        28,
        "hemophilia",
        BOT,
        21,
        "WFH updates guidance on prophylaxis trough targets",
        "https://wfh.org",
        ("guidelines", "prophylaxis"),
    ),
    _SeedItem(
        31,
        "ai",
        BOT,
        61,
        "Structured outputs now supported in streaming responses",
        "https://platform.openai.com/docs",
        ("latestnews", "api"),
    ),
    _SeedItem(
        36,
        "ai",
        BOT,
        72,
        "Microsoft Research: small language models as orchestrator sub-agents",
        "https://microsoft.com/research",
        ("microsoft", "research"),
    ),
    _SeedItem(
        39,
        "hemophilia",
        BOT,
        18,
        "Perioperative management on emicizumab: single-center retrospective",
        "https://ashpublications.org/bloodadvances",
        ("emicizumab", "surgery"),
    ),
    _SeedItem(
        42,
        "ai",
        None,
        34,
        "FastAPI adds native server-sent events responses",
        "https://fastapi.tiangolo.com/release-notes",
        ("tooling", "python"),
    ),
    _SeedItem(
        45,
        "ai",
        BOT,
        29,
        "Open model tops leaderboard for German legal text retrieval",
        "https://huggingface.co",
        ("models", "german"),
    ),
    _SeedItem(
        49,
        "hemophilia",
        BOT,
        15,
        "Home-treatment PK dashboards: patient-reported usability study",
        "https://jmir.org",
        ("pharmacokinetics", "digital-health"),
    ),
    _SeedItem(
        52,
        "ai",
        POLICY_WATCH,
        40,
        "Benchmarks are saturating: the case for task-specific evals",
        "https://huyenchip.com",
        ("research", "evals"),
    ),
    _SeedItem(
        55,
        "ai",
        BOT,
        36,
        "Reasoning model distills released under MIT license",
        "https://huggingface.co/models",
        ("models", "latestnews"),
    ),
)


def seed_demo(session: Session, now: datetime) -> bool:
    if session.scalar(select(func.count()).select_from(Item)):
        return False

    accounts = {
        username: _get_or_create_account(session, username, kind, admin)
        for username, kind, admin in ACCOUNTS
    }
    topics = {topic.slug: topic for topic in session.scalars(select(Topic))}
    tags = {(tag.topic_id, tag.name): tag for tag in session.scalars(select(TopicTag))}

    items: list[Item] = []
    for seed in SEED_ITEMS:
        owner = accounts[seed.account] if seed.account else None
        topic = topics[seed.topic]
        items.append(
            Item(
                title=seed.title,
                url=seed.url,
                topic=topic,
                account_id=owner.id if owner else None,
                label=seed.label,
                upvotes=seed.score,
                ip_hash=_fake_hash(f"ip:{seed.account}"),
                tags=[tags[(topic.id, name)] for name in seed.tags],
                links=[
                    ItemLink(kind=LinkKind.CORROBORATING, url=url) for url in seed.corroborating
                ],
                created_at=now - timedelta(hours=seed.hours_ago),
            )
        )
    session.add_all(items)
    session.flush()

    for item, seed in zip(items, SEED_ITEMS, strict=True):
        for number in seed.related:
            item.links.append(ItemLink(kind=LinkKind.RELATED, url=items[number - 1].url))

    return True


def _get_or_create_account(
    session: Session, username: str, kind: AccountKind, admin: bool
) -> Account:
    account = session.scalar(select(Account).where(Account.username == username))
    if account is None:
        account = Account(
            username=username,
            kind=kind,
            is_admin=admin,
            password_hash=hash_password(f"dev-password-{username}")
            if kind is AccountKind.USER
            else None,
            api_key_hash=hash_secret(f"dev-key-{username}") if kind is AccountKind.AGENT else None,
        )
        session.add(account)
        session.flush()
    return account


def _fake_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def main() -> None:
    engine = build_engine(settings.database_url)
    with session_scope(build_session_factory(engine)) as session:
        created = seed_demo(session, utc_now())
    engine.dispose()
    print("Seeded demo data." if created else "Items already exist; nothing seeded.")


if __name__ == "__main__":
    main()
