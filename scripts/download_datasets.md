# Downloading datasets

CipherScope never ships captures or datasets. Every real dataset is downloaded by
you, from its owner, under that owner's terms. Read the terms before you download.

All commands below are examples; check the current instructions on each owner's
site because links and licences change.

## ISCX VPN-nonVPN (Canadian Institute for Cybersecurity)

1. Open the UNB CIC dataset page and find **VPN-nonVPN** (ISCX VPN-nonVPN 2016).
2. Accept the terms and download the capture archive.
3. Extract it under `data/iscx/` (ignored by git).
4. Load an authorized capture:

```bash
uv run python -m cipherscope.cli load-dataset iscx_vpn_nonvpn data/iscx/capture.pcap \
  --capture-id iscx-2016-vpn --environment iscx-lab --label vpn \
  --i-accept-dataset-license --output data/iscx-flows.jsonl
```

## CIC-IDS2017 (Canadian Institute for Cybersecurity)

1. Open the UNB CIC dataset page and find **CIC-IDS2017**.
2. Accept the terms and download the PCAP or packet export you need.
3. Extract it under `data/cic-ids2017/` (ignored by git).
4. Load an authorized capture:

```bash
uv run python -m cipherscope.cli load-dataset cic_ids2017 data/cic-ids2017/capture.pcap \
  --capture-id cic-2017-wednesday --environment cic-lab --label benign \
  --i-accept-dataset-license --output data/cic-flows.jsonl
```

## Packet CSV exports

If you already have a packet-level export, it must contain exactly these columns:

| Column | Meaning |
| --- | --- |
| `timestamp` | seconds since the epoch, float |
| `src_ip` | source address (hashed at ingest) |
| `dst_ip` | destination address (hashed at ingest) |
| `src_port` | source port (never a feature) |
| `dst_port` | destination port (never a feature) |
| `protocol` | `tcp` or `udp` |
| `length` | frame length in bytes |
| `tcp_flags` | optional integer TCP flags |

```bash
uv run python -m cipherscope.cli ingest-csv data/export.csv \
  --capture-id lab-export --environment lab-alpha --label web \
  --output data/flows.jsonl
```

## Rules

- Do not commit captures, CSV exports or derived datasets.
- Keep `CIPHERSCOPE_HASH_SALT` private and rotate it between datasets.
- Do not upload captures anywhere. The CLI reads local files only.
- Synthetic results and real-dataset results must be reported separately.
