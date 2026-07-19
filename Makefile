# Learn MCP in Python — repo-wide tasks. Run `make` to see targets.
#
# For day-to-day learning, cd into a course and use ITS Makefile — that's where
# the per-exercise loop lives:
#   cd mcp-fundamentals
#   make test-exercise E=exercises/01.ping/01.problem.connect
#
# The targets here operate across all four courses (install everything, verify
# every reference solution — what CI runs, launch the demo).

COURSES := mcp-fundamentals mcp-auth mcp-ui mcp-advanced-features
MAKE_C := $(MAKE) --no-print-directory -C

.DEFAULT_GOAL := help
.PHONY: help check-uv install test test-problems test-fundamentals test-auth test-ui test-advanced demo clean

help: ## Show this help
	@echo "Learn MCP in Python — repo-wide targets:"
	@echo "(for one course, cd into it and run its own \`make help\`)"
	@echo
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

check-uv: ## Check that uv is installed
	@command -v uv >/dev/null 2>&1 || { \
		echo "uv is not installed."; \
		echo "Install it with:  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "or see https://docs.astral.sh/uv/getting-started/installation/"; \
		exit 1; }

install: check-uv ## Install every course's dependencies (uv sync)
	@for c in $(COURSES); do echo "==> $$c"; $(MAKE_C) $$c install || exit 1; done

test: check-uv ## Verify every course's reference solutions (what CI runs)
	@for c in $(COURSES); do echo "== $$c =="; $(MAKE_C) $$c test || exit 1; done

test-problems: check-uv ## Verify every course's problems start red (what CI runs)
	@for c in $(COURSES); do echo "== $$c =="; $(MAKE_C) $$c test-problems || exit 1; done

test-fundamentals: check-uv ## Verify the fundamentals reference solutions
	@$(MAKE_C) mcp-fundamentals test

test-auth: check-uv ## Verify the auth reference solutions
	@$(MAKE_C) mcp-auth test

test-ui: check-uv ## Verify the ui reference solutions
	@$(MAKE_C) mcp-ui test

test-advanced: check-uv ## Verify the advanced-features reference solutions
	@$(MAKE_C) mcp-advanced-features test

demo: check-uv ## Launch the mcp-ui browser demo (http://localhost:8788, Ctrl-C to stop)
	@cd mcp-ui && uv run python demo/app.py

clean: ## Remove every course's virtualenv and caches
	@for c in $(COURSES); do $(MAKE_C) $$c clean; done
