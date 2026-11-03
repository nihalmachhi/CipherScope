# Changelog

All notable changes to this project are documented in this file.

## [0.2.0] - 2026-11-01

### Added
- Real dataset loaders for ISCX VPN-nonVPN, CIC-IDS2017 and USTC-TFC2016 with licence gating.
- Packet-level CSV ingestion and a bidirectional flow assembler.
- Zeek conn.log reader and optional Parquet output.
- Distribution drift endpoint (PSI + KS).
- Optional 1D-CNN sequence model, isotonic calibration and permutation importance.
- React marketing site in `site/`.
- Structured JSON logging, pydantic API response models and pagination.
- Capture-grouped K-fold results, train-only isotonic calibration, permutation importance, and a seeded beacon precision/recall smoke benchmark.
- Streaming PCAP iteration with a bounded active-flow table and completion buffer.
- Restored the local dashboard with the existing project icon and matching dark palette; added its production build to CI.

### Fixed
- P0-1 FIN handling in PCAP ingestion.
- P0-2 fail-closed salt validation.
- P0-3 dataset and environment split separation.
- P1-1 import-time side effects and indexed repository.
- P1-2 admin endpoint hardening and background jobs.
- P1-3 config-driven evaluation and wired splitters.
- P1-4 robustness feature extraction cleanup.
- P1-5 multi-seed reporting with bootstrap CIs.
- P1-6 synthetic data overlap and opaque identifiers.
- P1-7 real sessions in synthetic data.
- P2-1 persisted bytes_total.
- P2-2 symmetric beacon detection with robust period estimate.
- P2-3 JSONL schema validation.
- P2-4 required secrets in compose.

### Decisions
- The local dashboard is retained alongside the marketing site: it remains the interactive API client, while the site explains the project and provides a synthetic browser demo.
