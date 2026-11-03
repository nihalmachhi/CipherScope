# Evaluation protocol

Run `make reproduce` to generate the synthetic examples, write `output/reports/synthetic-evaluation.json`, and refresh the site’s derived results and detector fixtures. The report records the experiment configuration hash, source revision, seed list, library versions, split-level results, calibration and robustness measurements. The site reads its figures from the generated JSON; do not hand-copy metrics into prose.

## Data and splits

The bundled examples are deterministic synthetic flows. They are useful for checking the pipeline and its invariants, not for estimating real-world detection quality. `S1_random_caution_only` is deliberately shown as an optimistic caution case. `S2_grouped_host`, `S3_time_forward`, `S4_cross_dataset`, `S5_leave_one_environment_out`, and `S6_capture_kfold` evaluate progressively stronger separation assumptions. S5 and S6 report individual folds and pooled results. The configured seeds are 7, 13, and 21; summaries include mean, standard deviation and bootstrap confidence intervals.

## Metrics and calibration

Classification reports include macro-F1, accuracy, beacon PR-AUC, false-positive rate at 90% recall, and expected calibration error. Isotonic calibration is fit using grouped host folds within training data only, then compared on the configured S4 test partition. Permutation importance is computed on the held-out S4 rows. Neither process uses test labels to fit the model or calibrator.

## Stress tests and beacon benchmark

The robustness report applies packet padding, timing jitter, and packet truncation to held-out flows. The beacon benchmark injects deterministic periodic callbacks plus polling and irregular hard negatives at several jitter levels; it records precision, recall, and confusion counts. These generated timing traces are a detector smoke benchmark, not real-world evidence. Periodic NTP traffic, refresh polling and timed retries can create false positives, so a beacon candidate requires review.

## Reproduction

Set a private `CIPHERSCOPE_HASH_SALT` before generating data. Then run `make reproduce`. On Windows, run the Makefile’s commands in order: `uv run python -m cipherscope.datasets.synthetic --output data/demo_flows.jsonl`, `uv run python -m cipherscope.eval.runner`, and `uv run python site/scripts/export_fixtures.py`. The site fixture exporter runs the actual Python beacon scoring function and derives UI metrics from the report. Vitest compares the TypeScript port against those generated fixtures.

No external dataset is downloaded or included in the repository. For real-dataset experiments, see [`dataset-card.md`](dataset-card.md) and [`../scripts/download_datasets.md`](../scripts/download_datasets.md); acquire the files yourself and accept their terms before loading them.
