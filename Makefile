.PHONY: run lint format install-dev install-prod

run:
	@uv run fastapi dev app/main.py

lint:
	@uv run zuban check
	@uv run ruff check

format:
	@uv run ruff format

install-dev:
	@uv sync --no-cache --group dev

install-prod:
	@uv sync --no-cache --group prod
