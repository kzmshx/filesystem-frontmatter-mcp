.PHONY: lint fix test

lint:
	uv run ruff check src tests
	uv run ruff format --check src tests

fix:
	uv run ruff check --fix src tests
	uv run ruff format src tests

test:
	uv run pytest tests -v
