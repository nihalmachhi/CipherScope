import { Section } from "../components/Section";
import { IconChip } from "../components/IconChip";

export function Pipeline() {
  const steps = [
    { title: "1. Record", body: "A context-manager SDK wraps each step in a span. Retrieval, tool calls and model calls nest under one agent workflow automatically.", color: "#8b5cf6" },
    { title: "2. Redact", body: "Keys like api_key and password, bearer tokens and emails become [REDACTED] before anything reaches storage. It is best effort.", color: "#f59e0b" },
    { title: "3. Compare", body: "Baseline and candidate prompts run on the same cases. Task success, groundedness, latency and cost sit side by side, and the gate decides.", color: "#f97316" },
  ];
  return (
    <Section id="how">
      <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Three steps. One regression trail.</h2>
      <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>Every run becomes one trace, and every trace is scored against the same expected facts.</p>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16, marginTop: 30 }}>
        {steps.map((s) => (
          <div key={s.title} style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 22 }}>
            <IconChip color={s.color}>
              <svg viewBox="0 0 24 24" width="22" fill="none" stroke="#fff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12h14" /></svg>
            </IconChip>
            <h3 style={{ fontSize: "1.15rem", marginBottom: 8 }}>{s.title}</h3>
            <p style={{ color: "var(--mu)", fontSize: "0.93rem" }}>{s.body}</p>
          </div>
        ))}
      </div>
    </Section>
  );
}