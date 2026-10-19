import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.connection import build_engine, build_session_factory, session_scope
from app.db.models import (
    ANONYMOUS_USERNAME,
    Account,
    AccountKind,
    Comment,
    Flag,
    Item,
    ItemCorroboratingUrl,
    ItemRelatedUrl,
    RelationOrigin,
    Topic,
    TopicTag,
    Vote,
    VoteEvent,
    utc_now,
)

BOT = "josan"


@dataclass(frozen=True, slots=True)
class _SeedItem:
    hours_ago: float
    topic: str
    publisher: str | None
    score: int
    title: str
    url: str
    tags: tuple[str, ...]
    corroborating: tuple[str, ...] = ()
    related: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class _SeedComment:
    item: int
    parent: int | None
    author: str
    hours_ago: float
    text: str


@dataclass(frozen=True, slots=True)
class _SeedFlag:
    item: int
    author: str
    reason: str | None


ACCOUNTS = (
    (BOT, AccountKind.AGENT),
    ("dragos", AccountKind.ADMIN),
    ("mkessler", AccountKind.HUMAN),
    ("lena_r", AccountKind.HUMAN),
    ("tbauer", AccountKind.HUMAN),
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
        "policy-watch",
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
        "policy-watch",
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

SEED_COMMENTS = (
    _SeedComment(
        1,
        None,
        "mkessler",
        0.4,
        "Checkpointing between hops was the missing piece for long scrape jobs. Does resume replay tool calls or only messages?",
    ),
    _SeedComment(
        1,
        1,
        "dragos",
        0.3,
        "Messages only, per the release notes. Tool calls need to be idempotent on your side.",
    ),
    _SeedComment(
        1,
        None,
        "lena_r",
        0.2,
        "Typed message contracts between orchestrator and workers make the swarm far easier to test.",
    ),
    _SeedComment(
        2,
        None,
        "tbauer",
        1.2,
        "Trough levels in the under-6 cohort are the number to watch. The full table is in the supplementary appendix.",
    ),
    _SeedComment(
        5,
        None,
        "lena_r",
        6,
        "Five years of stable expression is meaningful. Durability past ten years remains open.",
    ),
    _SeedComment(
        7,
        None,
        "mkessler",
        11,
        "Per-agent cost tracing is what makes the cheap-scraper / expensive-poster split measurable.",
    ),
    _SeedComment(
        8,
        None,
        "tbauer",
        13,
        "Committee vote expected next week. Briefing documents are already public.",
    ),
)

SEED_FLAGS = (_SeedFlag(20, "mkessler", "Opinion piece, not news."),)


def seed_demo(session: Session, now: datetime) -> bool:
    if session.scalar(select(func.count()).select_from(Item)):
        return False

    accounts = {name: _get_or_create_account(session, name, kind) for name, kind in ACCOUNTS}
    anonymous = session.scalars(select(Account).where(Account.username == ANONYMOUS_USERNAME)).one()
    topics = {topic.slug: topic for topic in session.scalars(select(Topic))}
    tags = {(tag.topic_id, tag.name): tag for tag in session.scalars(select(TopicTag))}

    items: list[Item] = []
    for seed in SEED_ITEMS:
        keyed = seed.publisher == BOT
        topic = topics[seed.topic]
        items.append(
            Item(
                title=seed.title,
                url=seed.url,
                canonical_url=seed.url,
                domain=_domain(seed.url),
                topic=topic,
                account=accounts[BOT] if keyed else anonymous,
                publisher=seed.publisher,
                publisher_key=seed.publisher.lower() if seed.publisher else None,
                submitter_ip_hash=None if keyed else _fake_hash(f"ip:{seed.publisher}"),
                tags=[tags[(topic.id, name)] for name in seed.tags],
                corroborating=[
                    ItemCorroboratingUrl(position=position, url=url)
                    for position, url in enumerate(seed.corroborating)
                ],
                created_at=now - timedelta(hours=seed.hours_ago),
            )
        )
    session.add_all(items)
    session.flush()

    for item, seed in zip(items, SEED_ITEMS, strict=True):
        for number in seed.related:
            earlier = items[number - 1]
            item.related.append(
                ItemRelatedUrl(
                    canonical_url=earlier.canonical_url,
                    url=earlier.url,
                    origin=RelationOrigin.SUBMITTED,
                )
            )
        _add_votes(session, item, seed.score)

    comments: list[Comment] = []
    for comment_seed in SEED_COMMENTS:
        comment = Comment(
            item_id=items[comment_seed.item - 1].id,
            parent_id=comments[comment_seed.parent - 1].id if comment_seed.parent else None,
            account_id=accounts[comment_seed.author].id,
            text=comment_seed.text,
            created_at=now - timedelta(hours=comment_seed.hours_ago),
        )
        session.add(comment)
        session.flush()
        comments.append(comment)

    for flag_seed in SEED_FLAGS:
        session.add(
            Flag(
                item_id=items[flag_seed.item - 1].id,
                account_id=accounts[flag_seed.author].id,
                reason=flag_seed.reason,
                created_at=now,
                updated_at=now,
            )
        )
    return True


def _add_votes(session: Session, item: Item, count: int) -> None:
    for number in range(count):
        voter_id = _fake_hash(f"voter:{item.id}:{number}")[:32]
        ip_hash = _fake_hash(f"ip:{voter_id}")
        voted_at = item.created_at + timedelta(minutes=number + 1)
        session.add(
            Vote(
                item_id=item.id,
                voter_id=voter_id,
                ip_hash=ip_hash,
                direction=1,
                created_at=voted_at,
                updated_at=voted_at,
            )
        )
        session.add(
            VoteEvent(
                item_id=item.id,
                voter_id=voter_id,
                ip_hash=ip_hash,
                direction=1,
                created_at=voted_at,
            )
        )
    item.upvotes = count


def _get_or_create_account(session: Session, username: str, kind: AccountKind) -> Account:
    account = session.scalar(select(Account).where(Account.username == username))
    if account is None:
        agent = kind is AccountKind.AGENT
        account = Account(
            username=username,
            username_key=username.lower(),
            kind=kind,
            publisher_name=username if agent else None,
            publisher_key=username.lower() if agent else None,
        )
        session.add(account)
        session.flush()
    return account


def _fake_hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _domain(url: str) -> str:
    host = urlsplit(url).hostname or ""
    return host.removeprefix("www.")


def main() -> None:
    engine = build_engine(settings.database_url)
    with session_scope(build_session_factory(engine)) as session:
        created = seed_demo(session, utc_now())
    engine.dispose()
    print("Seeded demo data." if created else "Items already exist; nothing seeded.")


if __name__ == "__main__":
    main()
