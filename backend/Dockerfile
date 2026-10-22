FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY migrations ./migrations
COPY app ./app

RUN mkdir -p /app/data

EXPOSE 8000
CMD ["sh", "-c", "uv run --no-dev alembic upgrade head && exec uv run --no-dev fastapi run app/main.py --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips 127.0.0.1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"]
