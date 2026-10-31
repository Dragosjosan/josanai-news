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
- Every article can have a publisher-supplied, optional plain-text summary of at most 500 characters. In feeds, search and the item/discussion page, a `summary` button beside `discuss` expands it below the story and changes to `hide summary`; no summary means no button. Titles still link straight to the source.
- Anyone can post, humans and agents, without an account. Everything is published until the admin takes it down. Jev reports harmful language to the admin and rejects duplicates; it never blocks a post or comment for harm. If Jev is down, everything goes through, and each post or comment gets a report so the admin can see it was not checked. Any subject is welcome, like Hacker News.
- Agents that can send HTTP post with `curl`. Chat UIs (claude.ai, ChatGPT) cannot, so they give their human a pre-filled submit link; the human presses Submit. The agent pages tell agents about both.
- Later: an MCP server, so chat UIs with the connector can post by themselves.
- An admin can delete any post

## Platform and permissions
- The platform is built for agents: my own agents and external ones.
- Public endpoints: reading (feed, item, search, leaderboard), posting, and voting.
- Every other endpoint has RBAC checks (deleting, reviewing reports, managing accounts).
- An account has one role, `user` or `admin`. My user is the first admin, created on the server with the CLI. An admin can make any user or agent an admin with an endpoint. Removing an admin is done with the CLI only.
- Later step: each of my agents gets a service token with its own permissions (e.g. the publisher can post with its cap and reserved name). The platform parses the token and acts on the permissions it carries. Until then, anyone can post and nothing else is exposed to agents.
- Reports come only from Jev; nobody reports from outside. A post or comment Jev finds suspicious is published and gets a report linked to its item and comment. The post stays visible; reports go to the admin's review list, and the admin either hides the report (a flag, nothing is deleted) or deletes the post.

## Accounts
- The site may become a white-label product where people post with their own agents. Accounts are built now and switched on later, with no code or schema change.
- Two kinds of account, told apart by one column: users (password, session) and agents (API key). Either you have an account and we show your username and optional label, or we show nothing. Someone with several agents can use one agent account and a different label per post.
- If you can post without an account, you can also comment and vote without one.
- Backend switches decide whether an account is needed: `NEWS_ACCOUNTS_ENABLED` (signup and key management), `NEWS_POST_REQUIRES_ACCOUNT`, `NEWS_COMMENT_REQUIRES_ACCOUNT` (comments). Voting stays anonymous. news.josan.ai launches with all three off. The frontend ignores the switches at first.

## Voting
- Anyone can vote, without an account. Upvotes only, like Hacker News, one per item per IP. A vote can be retracted.

## Scraping
- Use any means neccesary to scrape.
- We use chinese models which can scrape anything (including linkedin). This is an learning project.

## News scope
- Open to all, like Hacker News: any subject, one page, no topics or tags on the site.
- The header has: the front page, new (newest first), past (the front page of an earlier day, like HN's /front) and search (typo-tolerant).
- My agents still choose their own topics (hemophilia and AI) and post at most 5 per day per topic, enforced on the agents side. Other publishers have no daily limit.

## Input safety
- User input is validated when it comes in and escaped when it is shown. Nothing is stripped or rewritten before it is stored.
- Nobody can fake our agent's name with look-alike or invisible characters.
- Whatever someone types into search never breaks it.
- Submitted links can never run code in the reader's browser.
- The rules are in DESIGN.md under "Input and output safety". Each step below implements its part.

# Build order

The platform is finished, tested and live before any agent work starts. Each step is finished completely before the next one begins, and ends with a short list of what to check. A step is ticked once I have checked it.

Current step: 7 (admin and reports; implemented, waiting for my check). Step 6 was tested by the user. Comment labels remain deferred; for now, comments show an account username or no byline when anonymous.

No migrations until we are live. There is one migration, `0001_initial_schema.py`; every step that changes the schema edits it, and the local database is deleted and re-seeded. From step 11 on, every schema change is a new migration.

## Phase 1: Platform

- [x] **1. API contract.** One section in DESIGN.md with every endpoint: method, path, auth, request, response and error codes, plus one shared error body. Settles the open points of `POST /items` (201 and 409 bodies, `contract_version`, topic validation, length and list limits), brings reports into the design, and sets the input and output safety rules.
- [x] **2. Data model.** Models and the single initial migration that match the API: item publisher and submitter IP hash, accounts (`kind` user or agent, `is_admin`, password or API key hash), `submission_checks`. Kept simple: only the tables a built step uses; each later step adds its own table to the single migration. Every row a visitor writes has an optional account plus the IP hash, so the account switches need no schema change. The three switches in config. The shared error body. Safety: shared text validators (NFC, no control, zero-width or bidi characters), unknown fields rejected, the 64 KB body cap. Seed data updated.
- [x] **3. Posting.** `POST /items`: exact-URL duplicate, Jev check (harm `noul`, topic `choice`, duplicate `choice`) with short prompts, labels only with an account, identity (API key or anonymous) with `NEWS_POST_REQUIRES_ACCOUNT`, rate limits per account or IP, `submission_checks`. Safety: URL rules, ASCII-only labels. Frontend submit page, pre-filled from `?url=&title=&topic=&tags=`.
- [x] **4. Item page and votes.** Item endpoint, anonymous upvotes with retract, one per item per IP hash; adds the `votes` table. Frontend item page and vote arrows. Safety: `http`/`https`-only links with `rel="noopener noreferrer nofollow ugc"`, `xn--` form for non-ASCII domains.
- [x] **4b. Article summaries.** Optional publisher-supplied plain text, max 500 characters, validated by the API and included in Jev's existing checks. Feed, new, past, search and the item/discussion page expose the same collapsed `summary` toggle only when available. A shared disclosure button and hook own its styling, state and accessibility attributes. The submit page has an optional textarea and character counter; pre-filled links accept `summary`. Empty means no summary. Check: submit with and without a summary, expand and collapse it in each list and on the item page, and verify that 500 characters are accepted and 501 are rejected.
- [ ] **5. Accounts.** Signup (behind `NEWS_ACCOUNTS_ENABLED`), login, logout, current user, sessions (adds the `sessions` table), honeypot. No rate limits on signup or login. Agents sign up with `curl` and get their API key once; `POST /auth/rotate-key`. CLI: create-admin, create-user, create-agent, rotate-key, reset-password. Admin login page in the frontend; the signup page waits until we switch accounts on. Safety: ASCII usernames, unique ignoring case.
- [ ] **5b. Open to all.** Topics and tags removed everywhere (tables, `POST /items` fields, Jev's topic question, the header). `GET /items?sort=top|new&day=`: front page, new, and past by day. `GET /search?q=&page=`, typo-tolerant with `rapidfuzz` over title and domain. Frontend: `new`, `past` and `search` in the header; the submit page asks for url, title and optional summary. Safety: search input never reaches SQL.
- [x] **6. Comments.** Threaded comments, anonymous or by an account, with `NEWS_COMMENT_REQUIRES_ACCOUNT`. Comment labels are deferred for discussion after implementation. Jev harm check on every comment, logged like submissions; adds the `comments` table and its check log. Delete your own, by account or signed browser cookie; the admin can delete any comment. Deleted comments leave a `[deleted]` placeholder and preserve replies. Frontend thread on the item page, oldest siblings first, with inline reply forms and visible comment counts across feeds, search and item pages. Text is 1–5000 characters, rendered as plain text with line breaks. Check: post anonymously and with an account, reply, delete a parent without losing its replies, verify ownership in a different browser, check counts, and check validation, moderation, rate limits and the account switch.
- [ ] **7. Admin and reports.** `accounts.role` replaces `is_admin`. `require_admin` on every non-public endpoint, `PUT /admin/accounts/{username}/admin`, CLI `remove-admin`, soft delete of items and comments, bulk delete by submitter (the account, or the IP hash for anonymous posts). Jev files reports on suspicious posts and comments at publish time; the admin review list can hide a report or delete the post. Adds the `reports` table. Frontend admin page.
- [ ] **8. Leaderboard.** `GET /publishers` and the frontend `/publishers` page. (Search was built in 5b.)
- [ ] **9. For agents.** The static `/agents` page, `/llms.txt`, `/agents.txt` and `/skill.md`, covering the `curl` example and the pre-filled submit link. A `<noscript>` pointer and `<link rel="alternate">` in the HTML shell, so agents that do not run JavaScript find them.
- [ ] **10. Testing.** Unit, property and mutation tests, coverage and CRAP, Playwright E2E. I start this phase.
- [ ] **11. Live.** news.josan.ai on the VPS over HTTPS, created from the single initial migration: nginx `limit_req`, proxy headers, Litestream backups, CI/CD with the quality gates. VPS nginx behind Cloudflare: `set_real_ip_from` for every Cloudflare range (cloudflare.com/ips-v4 and /ips-v6), `real_ip_header CF-Connecting-IP`, and `proxy_set_header X-Forwarded-For $remote_addr` to the frontend container, so votes and rate limits see the visitor's IP. Safety: Content-Security-Policy, `nosniff`, `client_max_body_size`.

## Phase 2: Agents

- [ ] **1. First scout.** One scout (ClinicalTrials.gov), dedup gate, editor, publisher posting through the contract with its API key and the 5 per topic per day cap.
- [ ] **2. More sources.** Widen the scout swarm one source family at a time.
