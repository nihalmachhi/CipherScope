export const faq = [
  { q: "Does it decrypt traffic?", a: "No. Only headers, sizes, timing and flow structure are used." },
  { q: "What does metadata only mean?", a: "No payload bytes are read or stored." },
  { q: "Are the scores real?", a: "They come from a deterministic synthetic dataset and phrase checks, so they show the workflow rather than real model quality." },
  { q: "Why are the demo numbers so high?", a: "Synthetic classes are separable; real traffic is harder." },
  { q: "Which datasets are supported?", a: "ISCX VPN-nonVPN, CIC-IDS2017 and USTC-TFC2016 via explicit licence acceptance." },
  { q: "How are hosts anonymized?", a: "HMAC hashing with a required salt; rotate CIPHERSCOPE_HASH_SALT between datasets." },
  { q: "What is leakage-aware splitting?", a: "Splits by host, time, capture, dataset and environment with group-disjoint assertions." },
  { q: "Can it run on a live interface?", a: "No, only authorized offline captures." },
  { q: "Is it production ready?", a: "No, it is local and single-process with no authentication." },
];