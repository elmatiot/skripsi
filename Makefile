# Shortcut commands. Jalankan `make help` utk daftar lengkap.
SHELL := /bin/bash
COMPOSE ?= docker compose

.PHONY: help up down build logs migrate seed reset-db test

help:
	@echo "Targets:"
	@echo "  make up          - Build + start semua service (detached)"
	@echo "  make down        - Stop & remove containers"
	@echo "  make logs        - Tail logs semua service"
	@echo "  make build       - (Re)build images"
	@echo "  make migrate     - Run alembic upgrade head"
	@echo "  make reset-db    - Drop & recreate database"
	@echo "  make test        - Jalankan pytest backend"

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=200

build:
	$(COMPOSE) build

migrate:
	$(COMPOSE) exec backend alembic upgrade head

reset-db:
	$(COMPOSE) exec postgres psql -U postgres -c "DROP DATABASE IF EXISTS finance;" -c "CREATE DATABASE finance;"
	$(COMPOSE) exec backend alembic upgrade head

test:
	$(COMPOSE) exec backend pytest -q
