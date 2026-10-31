# News API

From this directory, initialize the local database with `uv run alembic upgrade
head`, then add demo stories and threaded comments with `uv run python -m
app.db.seed`. Run the API with `uv run uvicorn app.main:app --reload`.

Before launch, schema changes edit `0001_initial_schema.py`. An existing
database stamped `0001` needs to be backed up and rebuilt from that migration;
running `upgrade head` alone will not apply edits to the initial schema.

Comments use `GET`/`POST /api/v1/items/{id}/comments` and `DELETE
/api/v1/comments/{id}`. Anonymous posting is enabled by default. Set
`NEWS_COMMENT_REQUIRES_ACCOUNT=true` to require a user session or agent API key.
`NEWS_COMMENT_PER_HOUR` defaults to 30 moderation attempts per account or
anonymous IP hash, including rejected and unavailable checks.

Create the first admin with `uv run python -m app.cli create-admin <username>`.
Admins can make other accounts admins through the API; only `uv run python -m
app.cli remove-admin <username>` takes the role away. Jev files a report on
anything published with a harm score of at least `NEWS_JEV_REPORT_MIN` (default
0.5), and on anything published while Jev was unavailable or
`NEWS_JEV_API_KEY` was missing. Jev never blocks a post or comment for harm; the
admin takes it down.

Set `NEWS_COOKIE_SECRET` to a private, stable random value for deployment. It
signs the one-year anonymous ownership cookie; changing it invalidates those
cookies. Only hashed visitor ids and IP addresses are stored. Keep
`NEWS_COOKIE_SECURE=true` on HTTPS; use `false` for local HTTP development.
Jev uses the existing `NEWS_JEV_*` settings and checks every submitted comment
before it is published.
