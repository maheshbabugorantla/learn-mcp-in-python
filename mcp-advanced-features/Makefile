# This course — run `make` to see targets.
#
# The everyday loop is one exercise at a time:
#   make test-exercise E=exercises/01.ping/01.problem.connect
# Edit that exercise's server.py, re-run, watch it go from red to green.

.DEFAULT_GOAL := help
.PHONY: help install test-exercise test clean

help: ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install: ## Install this course's dependencies (uv sync)
	@uv sync

test-exercise: ## Test one exercise: make test-exercise E=exercises/<topic>/<dir>
	@test -n "$(E)" || { \
		echo "Name the exercise you're working on, e.g.:"; \
		echo "  make test-exercise E=exercises/01.ping/01.problem.connect"; \
		exit 1; }
	@uv run pytest "$(E)"

test: ## Run every solution suite in this course (one exercise at a time)
	@fail=0; for d in $$(find exercises -type d -name '*.solution*' | sort); do \
		printf '==> %s\n' "$$d"; \
		uv run pytest "$$d" -q -p no:cacheprovider || fail=1; \
	done; \
	if [ $$fail -eq 0 ]; then echo "all solution suites passed"; else echo "some suites failed"; exit 1; fi

clean: ## Remove this course's virtualenv and caches
	@rm -rf .venv .pytest_cache
	@find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.db' -delete 2>/dev/null || true
	@echo "cleaned"
