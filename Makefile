install:
	uv sync --extra dev

demo:
	uv run python -m cipherscope.datasets.synthetic --output data/demo_flows.jsonl

evaluate:
	uv run python -m cipherscope.eval.runner

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format cipherscope tests

frontend:
	cd dashboard && npm ci && npm run build
