install:
	uv sync --extra dev

demo:
	uv run python -m cipherscope.datasets.synthetic --output data/demo_flows.jsonl

evaluate:
	uv run python -m cipherscope.eval.runner

reproduce: demo evaluate

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

types:
	uv run mypy src

format:
	uv run ruff format src tests

site:
	cd site && npm ci && npm run build
