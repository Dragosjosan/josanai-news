.PHONY: help install migrate seed reset-db test lint build run down db-export reset-docker-db check-not-prod check-prod-env build-prod run-prod deploy-prod restart-prod down-prod logs-prod backup-prod

.DEFAULT_GOAL := help

COMPOSE := docker compose -f docker-compose.yml
PROD_ENV_FILE ?= /etc/news/.env
PROD_COMPOSE := NEWS_ENV_FILE=$(PROD_ENV_FILE) $(COMPOSE)
PROD_REQUIRED_KEYS := NEWS_COOKIE_SECRET NEWS_IP_HASH_SALT NEWS_JEV_API_KEY
BACKUP_DIR ?= /var/backups/news
BACKUP_KEEP_DAYS ?= 14

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
	@echo ""
	@echo "Production (secrets in $(PROD_ENV_FILE)):"
	@echo "  make build-prod   - build the images"
	@echo "  make run-prod     - start the containers"
	@echo "  make deploy-prod  - rebuild, replace the containers and wait until healthy"
	@echo "  make restart-prod - restart the containers without rebuilding"
	@echo "  make down-prod    - stop the containers, keeping the data"
	@echo "  make logs-prod    - follow the last 100 log lines"
	@echo "  make backup-prod  - copy news.db to $(BACKUP_DIR), keeping $(BACKUP_KEEP_DAYS) days"

install:
	cd backend && uv sync
	cd agents/maf && uv sync
	cd frontend && bun install

migrate:
	cd backend && uv run alembic upgrade head

check-not-prod:
	@test ! -e "$(PROD_ENV_FILE)" || { echo "Refusing: $(PROD_ENV_FILE) exists, so this is a production machine."; exit 1; }

seed: check-not-prod migrate
	cd backend && NEWS_SEED_ALLOWED=true uv run python -m app.db.seed

reset-db: check-not-prod
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

reset-docker-db: check-not-prod
	$(COMPOSE) down -v
	$(COMPOSE) up -d --build --wait
	$(COMPOSE) exec -e NEWS_SEED_ALLOWED=true backend uv run --no-dev python -m app.db.seed

check-prod-env:
	@test -r "$(PROD_ENV_FILE)" || { echo "Missing or unreadable: $(PROD_ENV_FILE)"; exit 1; }
	@for key in $(PROD_REQUIRED_KEYS); do \
		grep -q "^$$key=." "$(PROD_ENV_FILE)" || { echo "Set $$key in $(PROD_ENV_FILE)"; exit 1; }; \
	done

build-prod:
	$(PROD_COMPOSE) build

run-prod: check-prod-env
	$(PROD_COMPOSE) up -d --remove-orphans

deploy-prod: check-prod-env
	$(PROD_COMPOSE) up -d --build --remove-orphans --wait

restart-prod:
	$(PROD_COMPOSE) restart

down-prod:
	$(PROD_COMPOSE) down

logs-prod:
	$(PROD_COMPOSE) logs --tail=100 -f

backup-prod:
	mkdir -p $(BACKUP_DIR)
	$(PROD_COMPOSE) exec -T backend uv run --no-dev python -c "import sqlite3; sqlite3.connect('data/news.db').backup(sqlite3.connect('data/backup.db'))"
	$(PROD_COMPOSE) cp backend:/app/data/backup.db $(BACKUP_DIR)/news-$$(date -u +%Y-%m-%d).db
	$(PROD_COMPOSE) exec -T backend rm -f data/backup.db
	find $(BACKUP_DIR) -name 'news-*.db' -mtime +$(BACKUP_KEEP_DAYS) -delete
