.PHONY: run lint format install-dev install-prod init reset

run:
	@uv run fastapi dev app/main.py

lint:
	@uv run zuban check
	@uv run ruff check

format:
	@uv run ruff format

install-dev:
	@uv sync --group dev

install-prod:
	@uv sync --group prod

init:
	@uv run python -m scripts.init

reset:
	@uv run scripts/reset_all_modules.py

set-db:
	@uv run alembic upgrade head

downgrade-all:
	@uv run alembic downgrade base
