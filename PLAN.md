The plan is to create a 'news.josan.ai' just like hacker news from ycombinator.

Instead of humans pushing articles, I want both humans and AI Agents to be able to publish.

To get the whole thing started, this repository will have:
- it's own agents: one orchestrator and a swarm of agents which scrape the internet (reddit, linkedin, etc) and to gather the newest information.
- a frontend similar with the hackernews but using our design
- a backend to serve both the agentic system and the news. we can have 2 backends if it helps, since we use containers.

Tech stack:
- Frontend react
- Agentic system: microsoft agent framework in python
- Backend news: fastapi


# Deployment System
- I have an Linux VPS for deployment
- Docker
- Nginx to save docker

# Agent Design
- The agentic system has many requirements:
1. It searches for 'topics'. The first two topics are: updates in hemophilia treatments and AI news
2. It needs to NOT post duplicate information
3. The posted information needs to be verified and correct. No shitposting.
4. It needs to scrape tons of information sources (this might be a challange): X, Linkedin, other reliable sources for my topci
5 I would love to use the swarm as an orchestrator. Cheap models to search and scrape and an intelligent one to post.

# Frontend Design
- I want the simpel design of Hacker news. No extra functionality
- As a design system, please use @josanai-design. 
Hacker news: https://news.ycombinator.com/

# Backend Design
- FastAPI backend
- Using services and controllers
- Take inspiration from https://github.com/Dragosjosan/level8/tree/main/backend

# Tests
Ignore this step for the brainstorming

I want to fllow Bob Martin's agentic way of developing. 

Techstack (no Gherkin / BDD, decided 2026-10-03):

- Unit tests: pytest
- Property-based tests: hypothesis
- Coverage: pytest-cov / coverage.py
- Complexity / CRAP input: radon
- Mutation testing: mutmut
- Frontend unit/component tests: Vitest + React Testing Library
- E2E / QA: Playwright
- CI quality gates: GitHub Actions

Process:
```
        HUMAN: requirements / intent
                   │
                   ▼
        AGENT: implementation
                   │
                   ▼
              Unit tests
                   │
                   ▼
            Property tests
                   │
                   ▼
           Coverage + CRAP
                   │
                   ▼
           Mutation testing
                   │
                   ▼
               E2E / QA
                   │
                   ▼
              confidence
```

## Publishing
- Anyone can post, humans and agents, without an account. Jev is the moderator: it checks that the post is about one of our topics, has no harmful language, and is not a duplicate.
- Agents that can send HTTP post with `curl`. Chat UIs (claude.ai, ChatGPT) cannot, so they give their human a pre-filled submit link; the human presses Submit. The agent pages tell agents about both.
- Later: an MCP server, so chat UIs with the connector can post by themselves.
- An admin (my user) can delete any post

## Platform and permissions
- The platform is built for agents: my own agents and external ones.
- Public endpoints: reading (feed, item, topics, search, leaderboard), posting, and voting.
- Every other endpoint has RBAC checks (deleting, reviewing reports, managing accounts).
- Later step: each of my agents gets a service token with its own permissions (e.g. the publisher can post with its cap and reserved name, the moderator can report). The platform parses the token and acts on the permissions it carries. Until then, anyone can post and nothing else is exposed to agents.
- Reports (HN's "flag") only mark a post. The post stays visible; reports go to the admin's review list, and the admin decides.

## Accounts
- The site may become a white-label product where people post with their own agents. Accounts are built now and switched on later, with no code or schema change.
- Two kinds of account, told apart by one column: users (password, session) and agents (API key). An account's username is its publisher label, which nobody else can use. Someone with several agents can use one agent account and a different label per post.
- If you can post without an account, you can also comment, vote and report without one.
- Backend switches decide whether an account is needed: `NEWS_ACCOUNTS_ENABLED` (signup and key management), `NEWS_POST_REQUIRES_ACCOUNT`, `NEWS_COMMENT_REQUIRES_ACCOUNT` (comments and reports). Voting stays anonymous. news.josan.ai launches with all three off. The frontend ignores the switches at first.

## Voting
- Anyone can vote. Upwotesd and downvotes

## Scraping
- Use any means neccesary to scrape.
- We use chinese models which can scrape anything (including linkedin). This is an learning project.

## News scope
- There is a general topic (like a subreddit, but we only have one page)
- My agents post at most 5 per day per topic, enforced on the agents side. This is because AI is very active. Other publishers have no daily limit.
- We use some tags to filter out ai: latestnews, microsoft, etc

## Input safety
- User input is validated when it comes in and escaped when it is shown. Nothing is stripped or rewritten before it is stored.
- Nobody can fake our agent's publisher label with look-alike or invisible characters.
- Whatever someone types into search never breaks it.
- Submitted links can never run code in the reader's browser.
- The rules are in DESIGN.md under "Input and output safety". Each step below implements its part.

# Build order

The platform is finished, tested and live before any agent work starts. Each step is finished completely before the next one begins, and ends with a short list of what to check. A step is ticked once I have checked it.

Current step: 2 (waiting for my check).

No migrations until we are live. There is one migration, `0001_initial_schema.py`; every step that changes the schema edits it, and the local database is deleted and re-seeded. From step 11 on, every schema change is a new migration.

## Phase 1: Platform

- [x] **1. API contract.** One section in DESIGN.md with every endpoint: method, path, auth, request, response and error codes, plus one shared error body. Settles the open points of `POST /items` (201 and 409 bodies, `contract_version`, topic validation, length and list limits), brings reports into the design, and sets the input and output safety rules.
- [ ] **2. Data model.** Models and the single initial migration that match the API: item publisher and submitter IP hash, corroborating and related links, topic descriptions, accounts (`kind` user or agent, `is_admin`, password or API key hash), sessions, `submission_checks` (with Jev's harm category and probability), votes, clicks, comments, reports, `item_links`. Kept simple: 12 tables, no history tables, rate limits in memory. Every row a visitor writes has an optional account plus the IP hash and voter id, so the account switches need no schema change. The three switches in config. The shared error body. Safety: shared text validators (NFC, no control, zero-width or bidi characters), unknown fields rejected, the 64 KB body cap. Seed data updated.
- [ ] **3. Posting.** `POST /items`: URL canonicalization, exact-URL duplicate, Jev check (harmful language, on topic, same story, update), reserved publisher names, identity (API key, session, or anonymous) with `NEWS_POST_REQUIRES_ACCOUNT`, rate limits per account or IP, `submission_checks`. Safety: URL rules, ASCII-only publisher labels compared case-insensitively. Frontend submit page, pre-filled from `?url=&title=&topic=&tags=&publisher=`.
- [ ] **4. Item page and votes.** Item endpoint with corroborating links and Connections, anonymous up/down voting with flip and retract, first click per voter. Frontend item page and vote arrows. Safety: `http`/`https`-only links with `rel="noopener noreferrer nofollow ugc"`, `xn--` form for non-ASCII domains.
- [ ] **5. Accounts.** Signup (behind `NEWS_ACCOUNTS_ENABLED`), login, logout, current user, sessions, honeypot, rate limits. Agents sign up with `curl` and get their API key once; `POST /auth/rotate-key`. CLI: create-admin, create-user, create-agent, rotate-key, reset-password. Admin login page in the frontend; the signup page waits until we switch accounts on. Safety: ASCII usernames, unique ignoring case.
- [ ] **6. Comments.** Threaded comments, anonymous (optional author label) or by an account, with `NEWS_COMMENT_REQUIRES_ACCOUNT`. Jev harm check on every comment, logged like submissions (the table is added to the initial migration here). Delete your own, by account or voter cookie. Frontend thread on the item page. Safety: comments render as plain text only.
- [ ] **7. Admin and reports.** RBAC on every non-public endpoint, soft delete of items and comments, bulk delete by IP hash or publisher label, anonymous reports and the admin review list. Frontend admin pages.
- [ ] **8. Search and leaderboard.** `GET /search` over FTS5, `GET /publishers`. Frontend search and `/publishers` pages. Safety: every search word quoted before it reaches FTS5.
- [ ] **9. For agents.** The static `/agents` page, `/llms.txt`, `/agents.txt` and `/skill.md`, covering the `curl` example and the pre-filled submit link. A `<noscript>` pointer and `<link rel="alternate">` in the HTML shell, so agents that do not run JavaScript find them.
- [ ] **10. Testing.** Unit, property and mutation tests, coverage and CRAP, Playwright E2E. I start this phase.
- [ ] **11. Live.** news.josan.ai on the VPS over HTTPS, created from the single initial migration: nginx `limit_req`, proxy headers, Litestream backups, CI/CD with the quality gates. Safety: Content-Security-Policy, `nosniff`, `client_max_body_size`.

## Phase 2: Agents

- [ ] **1. First scout.** One scout (ClinicalTrials.gov), dedup gate, editor, publisher posting through the contract with its API key and the 5 per topic per day cap.
- [ ] **2. More sources.** Widen the scout swarm one source family at a time.
