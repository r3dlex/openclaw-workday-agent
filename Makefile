# =============================================================================
# OpenClaw Workday Agent — Developer Commands
# =============================================================================
# Usage: make <target>
# =============================================================================

.PHONY: help test test-python test-elixir test-all build up down clean lint

PYTHON_DIR  := tools/pipeline_runner
ELIXIR_DIR  := orchestrator
COMPOSE     := docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Testing
# ---------------------------------------------------------------------------

test: test-python test-elixir ## Run all tests

test-python: ## Run Python pipeline runner tests
	cd $(PYTHON_DIR) && poetry install --no-interaction && poetry run pytest -v --tb=short

test-elixir: ## Run Elixir orchestrator tests
	cd $(ELIXIR_DIR) && mix deps.get && mix test

test-docker: ## Run all tests in Docker (zero-install)
	$(COMPOSE) -f docker-compose.yml -f docker-compose.test.yml run --rm pipeline-runner-test
	$(COMPOSE) -f docker-compose.yml -f docker-compose.test.yml run --rm orchestrator-test

# ---------------------------------------------------------------------------
# Linting
# ---------------------------------------------------------------------------

lint: lint-python lint-elixir ## Run all linters

lint-python: ## Lint Python code
	cd $(PYTHON_DIR) && poetry run python -m py_compile pipeline_runner/main.py

lint-elixir: ## Check Elixir formatting
	cd $(ELIXIR_DIR) && mix format --check-formatted

# ---------------------------------------------------------------------------
# Build & Run
# ---------------------------------------------------------------------------

build: ## Build all Docker images
	$(COMPOSE) build

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

# ---------------------------------------------------------------------------
# Legacy (Node.js CDP scripts)
# ---------------------------------------------------------------------------

approve: ## Run approve script locally
	node scripts/approve-workday.js

approve-docker: ## Run approve script in Docker
	$(COMPOSE) run --rm agent node scripts/approve-workday.js

# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------

clean: ## Remove build artifacts
	rm -rf $(PYTHON_DIR)/.pytest_cache $(PYTHON_DIR)/__pycache__
	rm -rf $(PYTHON_DIR)/pipeline_runner/__pycache__
	rm -rf $(PYTHON_DIR)/tests/__pycache__
	rm -rf $(ELIXIR_DIR)/_build $(ELIXIR_DIR)/deps
	$(COMPOSE) down --rmi local --volumes 2>/dev/null || true

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

scan-secrets: ## Scan for sensitive data in tracked files
	@echo "Scanning for sensitive patterns..."
	@git ls-files | xargs grep -lnE \
		'RIB[/ ]|RZB|aveva|c5738e|0e1fd44|FYEO|redlexgilgamesh' 2>/dev/null \
		&& echo "WARNING: Sensitive data found!" && exit 1 \
		|| echo "Clean: no sensitive data in tracked files."
