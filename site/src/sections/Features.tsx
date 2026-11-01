import { IconChip } from "../components/IconChip";

const cards = [
  { title: "Privacy by construction", body: "HMAC ids, no payload bytes retained.", span: 2, color: "#8b5cf6", tags: ["HMAC", "metadata only"] },
  { title: "Leakage-aware splits", body: "S1-S6 with group-disjoint assertions.", span: 2, color: "#f97316", tags: ["host", "time", "capture"] },
  { title: "Beacon detector", body: "Explainable periodicity score.", span: 2, color: "#f59e0b", tags: ["median+MAD", "autocorr"] },
  { title: "Robustness transforms", body: "Padding, jitter, truncation.", span: 2, color: "#06b6d4", tags: ["0-50%", "4/8/16/32"] },
  { title: "Model zoo + calibration", body: "RF, HGBM, LogReg, CNN, isotonic.", span: 3, color: "#ec4899", tags: ["grouped CV", "ECE"] },
  { title: "Local JSON API + WebSocket", body: "Health, flows, models, drift, jobs.", span: 3, color: "#22c55e", tags: ["/drift", "/live"] },
  { title: "Drift", body: "PSI and KS between time windows.", span: 2, color: "#a78bfa", tags: ["PSI", "KS"] },
  { title: "Reproducible reports", body: "Config hash and git SHA.", span: 2, color: "#fafafa", tags: ["seeds", "bootstrap"] },
  { title: "Not in this release", body: "Live capture, TLS ClientHello parsing, model registry, production deployment, real-world detection claims.", span: 6, color: "#ef4444", tags: ["out of scope"] },
];

export function Features() {
  return (
    <section id="features" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>A small system. Built to be inspected.</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>The SDK, redactor, store, evaluator, gate, API and dashboard each live in their own module.</p>
        <div className="bento" style={{ display: "grid", gridTemplateColumns: "repeat(6,1fr)", gap: 12, marginTop: 34 }}>
          {cards.map((c) => (
            <div key={c.title} style={{ gridColumn: `span ${c.span}`, background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 18, padding: 20, display: "flex", flexDirection: "column" }}>
              <IconChip color={c.color}>
                <svg viewBox="0 0 24 24" width="17" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14" /></svg>
              </IconChip>
              <h3 style={{ fontSize: "1rem", marginBottom: 6 }}>{c.title}</h3>
              <p style={{ color: "var(--mu)", fontSize: "0.86rem", marginBottom: 12 }}>{c.body}</p>
              <div style={{ marginTop: "auto", display: "flex", flexWrap: "wrap", gap: 6 }}>
                {c.tags.map((t) => (
                  <span key={t} style={{ fontFamily: "var(--fm)", fontSize: "0.72rem", background: "#0a0a0b", border: "1px solid var(--ln)", borderRadius: 8, padding: "3px 9px", color: "var(--mu)" }}>{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}