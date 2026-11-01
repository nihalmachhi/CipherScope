import { IconChip } from "../components/IconChip";

const cards = [
  { title: "Privacy by construction", body: "HMAC ids, no payload.", span: 2, color: "#8b5cf6" },
  { title: "Leakage-aware splits", body: "S1-S6 with assert_group_disjoint.", span: 2, color: "#f97316" },
  { title: "Beacon detector", body: "Explainable periodicity score.", span: 2, color: "#f59e0b" },
  { title: "Robustness transforms", body: "Padding, jitter, truncation.", span: 2, color: "#06b6d4" },
  { title: "Model zoo + calibration", body: "RF, HGBM, LogReg, CNN, isotonic.", span: 3, color: "#ec4899" },
  { title: "Local JSON API + WebSocket", body: "Health, flows, models, drift, jobs.", span: 3, color: "#22c55e" },
  { title: "Drift", body: "PSI and KS between time windows.", span: 2, color: "#a78bfa" },
  { title: "Reproducible reports", body: "Config hash and git SHA.", span: 2, color: "#fafafa" },
  { title: "Not in this release", body: "Live capture, TLS ClientHello parsing, model registry, production deployment.", span: 6, color: "#ef4444" },
];

export function Features() {
  return (
    <section id="features" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>A small system. Built to be inspected.</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>The SDK, redactor, store, evaluator, gate, API and dashboard each live in their own module.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", gap: 12, marginTop: 34 }}>
          {cards.map((c) => (
            <div key={c.title} style={{ gridColumn: `span ${c.span}`, background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 18, padding: 20 }}>
              <IconChip color={c.color}>
                <svg viewBox="0 0 24 24" width="17" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14" /></svg>
              </IconChip>
              <h3 style={{ fontSize: "1rem", marginBottom: 6 }}>{c.title}</h3>
              <p style={{ color: "var(--mu)", fontSize: "0.86rem" }}>{c.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}