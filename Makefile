.PHONY: install lint fmt test clean check help

help:
	@echo "Available commands:"
	@echo "  make install    Install dependencies"
	@echo "  make lint       Check code quality"
	@echo "  make fmt        Format code"
	@echo "  make test       Run tests"
	@echo "  make check      Run checks (lint + type)"
	@echo "  make clean      Remove build artifacts"

install:
	uv sync

lint:
	uv run ruff check ynab_import tests

fmt:
	uv run ruff format ynab_import tests
	uv run ruff check ynab_import tests --fix

test:
	uv run pytest tests/ -v

check: lint
	uv run mypy ynab_import

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
