.PHONY: help install migrate seed reset-db test lint build run down db-export reset-docker-db

.DEFAULT_GOAL := help

COMPOSE := docker compose -f docker-compose.yml

help:
	@echo "Development:"
	@echo "  make install   - install backend, agents and frontend dependencies"
	@echo "  make migrate   - create or upgrade backend/data/news.db"
	@echo "  make seed      - migrate, then add demo data"
	@echo "  make reset-db  - delete the local database and seed it again"
	@echo "  make test      - run the tests and build the frontend"
	@echo "  make lint      - run ruff, mypy and oxlint"
	@echo ""
	@echo "Docker:"
	@echo "  make build     - build the images"
	@echo "  make run       - start the containers"
	@echo "  make down      - stop the containers"
	@echo "  make db-export - copy the Docker database to backend/data/news-docker.db"
	@echo "  make reset-docker-db - delete the Docker database, rebuild and seed it"

install:
	cd backend && uv sync
	cd agents/maf && uv sync
	cd frontend && bun install

migrate:
	cd backend && uv run alembic upgrade head

seed: migrate
	cd backend && uv run python -m app.db.seed

reset-db:
	rm -f backend/data/news.db backend/data/news.db-wal backend/data/news.db-shm
	$(MAKE) seed

test:
	cd backend && uv run pytest
	cd agents/maf && uv run pytest
	cd frontend && bun run build

lint:
	cd backend && uv run ruff check . && uv run mypy app
	cd agents/maf && uv run ruff check . && uv run mypy src
	cd frontend && bun run lint

build:
	$(COMPOSE) build

run:
	$(COMPOSE) up -d --remove-orphans

down:
	$(COMPOSE) down

db-export:
	$(COMPOSE) exec backend uv run --no-dev python -c "import sqlite3; sqlite3.connect('data/news.db').backup(sqlite3.connect('data/export.db'))"
	mkdir -p backend/data
	$(COMPOSE) cp backend:/app/data/export.db backend/data/news-docker.db
	$(COMPOSE) exec backend rm -f data/export.db

reset-docker-db:
	$(COMPOSE) down -v
	$(COMPOSE) up -d --build --wait
	$(COMPOSE) exec backend uv run --no-dev python -m app.db.seed

