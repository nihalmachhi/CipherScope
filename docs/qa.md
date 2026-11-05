# Final QA

This is a point-in-time record, not a permanent guarantee. Re-run the commands
below on the commit you intend to show.

## Scope

- Date: 2026-11-05
- Branch: `main`
- Commit tested: `d3698cd` (`fix: make the container image runnable`)
- Local environment: Windows, Python 3.13.7, Node.js 22.19.0, npm 10.9.3
- Fresh-clone environment: `uv` resolved CPython 3.12.12

## Local checks

| Check | Command | Result |
|---|---|---|
| Python lint | `uv run ruff check .` | pass |
| Python format | `uv run ruff format --check .` | pass, 88 files |
| Python types | `uv run mypy src` | pass, 62 files |
| Python tests | `uv run pytest -q --cov=cipherscope --cov-fail-under=80` | 69 passed, 1 skipped |
| Coverage gate | same as above | 89.56% branch coverage (gate 80%) |
| Reproduction | `make reproduce` | pass, 450 synthetic flows |
| Fixture parity | `uv run python site/scripts/export_fixtures.py` | no content diff |
| Site lint | `npm run lint` | pass |
| Site types | `npm run typecheck` | pass |
| Site tests | `npm test` | 13 passed |
| Site build | `npm run build` | pass |
| Dashboard build | `npm ci && npm run build` | pass |
| Production audit | `npm audit --omit=dev` | 0 findings |
| Compose config | `docker compose config -q` | pass with CI-style secrets |

The skipped test requires the optional `deep` extra. Re-running the evaluation and
fixture exporter produced no content diff in `site/src/data/results.generated.json`
or the simulator fixtures. On Windows the working tree shows a line-ending-only
change because Python writes CRLF; the Git blob is identical, and CI on Linux sees
a clean tree.

## Fresh-clone check

A clean clone of `origin/main` at `d3698cd` was created outside the working tree
and verified without reusing local build artifacts:

```bash
git clone --depth 1 https://github.com/nihalmachhi/CipherScope.git cipherscope-fresh
cd cipherscope-fresh
uv sync --frozen --extra dev
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest -q --cov=cipherscope --cov-fail-under=80
cd site
npm ci
npm run lint
npm run typecheck
npm test
npm run build
```

All steps passed. The container smoke check also passed from the fresh clone:

```bash
docker compose build
docker compose run --rm api python -c \
  "from cipherscope.eval.runner import load_config; load_config()"
```

## Docker runtime verification

Docker Desktop's Linux engine was available on 2026-11-05. The image built, the
healthcheck reached `healthy`, and `/health` reported `flows: 450` from the
synthetic demo data generated inside the container.

The admin boundary behaved as designed: `POST /experiments/run` returned `403`
without a token. With the token it queued a job that completed and wrote
`/app/output/reports/synthetic-evaluation.json` (82 KB) into the mounted report
volume.

The first live run exposed two real packaging bugs:

- The unquoted YAML flow sequence `tmpfs: [/tmp:rw,noexec,nosuid,size=32m]` split
  the options on commas, so Docker treated `size=32m` as a mount path.
- The runtime image did not copy `configs/`, so the queued evaluation job failed
  with `FileNotFoundError` for `configs/synthetic-baseline.yaml`.

Both are fixed. `tests/test_packaging.py` now asserts that the Dockerfile ships the
config and that every compose `tmpfs` entry stays a single mount. CI also runs the
config-loading smoke check after building the image.

## Known non-blocking findings

- The optional `deep` extra is not installed locally, so one optional-feature test
  is skipped.
- `npm audit` reports moderate findings in development-only lint tooling; the
  production dependency tree reports zero findings.
- The site has Vitest and a production build, not browser automation.
- The synthetic evaluation checks the pipeline; it is not a real-world detection
  score.
