.DEFAULT_GOAL := help

.PHONY: help install test lint lint-fix format scan ha-up ha-down ha-restart ha-logs clean push push-origin push-gitea

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ── Dependencies ──────────────────────────────────

install: ## Install dev dependencies via uv
	uv sync

# ── Quality ───────────────────────────────────────

test: ## Run tests
	uv run pytest tests/ -v

test-cov: ## Run tests with coverage
	uv run pytest tests/ -v --cov=custom_components/friendly_scene_flipper --cov-report=term-missing

lint: ## Run ruff linter (check only)
	uv run ruff check .

lint-fix: ## Run ruff linter and auto-fix
	uv run ruff check --fix .

format: ## Run ruff formatter
	uv run ruff format .

format-check: ## Check formatting without changes
	uv run ruff format --check .

scan: ## Run security scans (Bandit + Trivy)
	uv run bandit -r custom_components/
	docker run --rm -v $$(pwd):/workspace:ro aquasec/trivy:latest fs --scanners vuln,secret,misconfig /workspace

# ── Dev Container ─────────────────────────────────

ha-up: ## Start HA dev container
	DOCKER_UID=$$(id -u) DOCKER_GID=$$(id -g) docker compose up -d

ha-down: ## Stop HA dev container
	docker compose down

ha-restart: ## Restart HA dev container
	docker compose restart

ha-logs: ## Tail HA logs (filtered to integration)
	docker compose logs -f home-assistant | grep --line-buffered friendly_scene_flipper

ha-logs-all: ## Tail all HA logs
	docker compose logs -f home-assistant

# ── Git ───────────────────────────────────────────

push: ## Push to all remotes (origin first, then gitea) with tags
	git push origin --follow-tags && git push gitea --follow-tags

push-origin: ## Push to origin (GitHub) with tags
	git push origin --follow-tags

push-gitea: ## Push to gitea (git.foo.pm) with tags
	git push gitea --follow-tags

# ── Housekeeping ──────────────────────────────────

clean: ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/

check: lint format-check test ## Run all checks (lint + format + test)
