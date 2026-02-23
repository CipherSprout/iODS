.PHONY: install-dev run test lint format

install-dev:
	pip install -e .[dev]

run:
	uvicorn iods.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest -q

lint:
	ruff check .

format:
	ruff check . --fix
