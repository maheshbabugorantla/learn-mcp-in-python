# Learn MCP in Python — developer tasks.
# Run `make` (or `make help`) to see the available targets.

COURSES := mcp-fundamentals mcp-auth mcp-ui mcp-advanced-features

.DEFAULT_GOAL := help

.PHONY: help check-uv install test test-fundamentals test-auth test-ui test-advanced demo clean

help: ## Show this help
	@echo "Learn MCP in Python — make targets:"
	@echo
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

check-uv: ## Check that uv is installed
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv is not installed."; \
		echo "Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "or see https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; }

install: check-uv ## Install every course's dependencies (uv sync)
	@for c in $(COURSES); do echo "==> $$c"; (cd $$c && uv sync) || exit 1; done

test: check-uv ## Run every course's solution test suites
	@./scripts/test.sh

test-fundamentals: check-uv ## Run the fundamentals solution suites
	@./scripts/test.sh mcp-fundamentals

test-auth: check-uv ## Run the auth solution suites
	@./scripts/test.sh mcp-auth

test-ui: check-uv ## Run the ui solution suites
	@./scripts/test.sh mcp-ui

test-advanced: check-uv ## Run the advanced-features solution suites
	@./scripts/test.sh mcp-advanced-features

demo: check-uv ## Launch the mcp-ui browser demo on http://localhost:8788 (Ctrl-C to stop)
	@cd mcp-ui && uv run python demo/app.py

clean: ## Remove virtualenvs, caches, and scratch databases
	@find . -type d -name '.venv' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.db' -delete 2>/dev/null || true
	@echo "cleaned virtualenvs, caches, and scratch databases"
