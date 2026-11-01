const cards = [
  { title: "Privacy by construction", body: "HMAC ids, no payload.", span: "bc w", color: "#8b5cf6", tags: ["api_key", "token", "password", "Bearer", "email"], icon: "M5 12h14" },
  { title: "Local JSON API", body: "Health, summary, traces and a demo rerun. Bound to 127.0.0.1.", span: "bc w", color: "#f97316", tags: ["GET /api/health", "GET /api/summary", "GET /api/traces"], icon: "M8 8l-4 4 4 4M16 8l4 4-4 4" },
  { title: "Best-effort redaction", body: "Sensitive-looking keys and tokens are masked before storage.", span: "bc", color: "#f59e0b", tags: ["api_key", "token", "password", "Bearer", "email"], icon: "M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z" },
  { title: "Deterministic", body: "A fixed dataset and phrase checks give the same verdict every run.", span: "bc", color: "#22c55e", tags: ["traceforge-faq-v1", "not an LLM judge"], icon: "M5 12.5l4.5 4.5L19 7.5" },
  { title: "Standard library", body: "No runtime packages to install.", span: "bc", color: "#fafafa", tags: ["Python 3.11+"], icon: "M8 8l-4 4 4 4M16 8l4 4-4 4" },
  { title: "Validated SQLite storage", body: "A trace is saved atomically, and the store refuses malformed data before writing.", span: "bc w", color: "#ec4899", tags: ["duplicate span ID", "orphan span", "trace_id mismatch"], icon: "M5 6c0-1.7 3.1-3 7-3s7 1.3 7 3-3.1 3-7 3-7-1.3-7-3zM5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6" },
  { title: "A gate for CI", body: "Compare candidate with baseline and exit with code 1 when quality drops past your limits.", span: "bc w", color: "#ef4444", tags: ["gate --max-task-drop 0.25", "exit code 1"], icon: "M7 19v-6M12 19V6M17 19v-10" },
  { title: "Not in this release", body: "Real model calls and provider pricing, an LLM judge, authentication, production load testing, OpenTelemetry export, and trace context across thread pools are out of scope.", span: "bc f", color: "#22c55e", tags: ["model calls", "LLM judge", "authentication", "load benchmark", "OpenTelemetry", "thread pools"], icon: "M5 12h14" },
];

export function Features() {
  return (
    <section className="sec" id="features">
      <div className="wrap">
        <h2>A small system. <span className="m">Built to be <i className="ico" style={{ "--c": "#8b5cf6" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M12 3l8 4.5v9L12 21l-8-4.5v-9zM12 12l8-4.5M12 12v9M12 12L4 7.5"/></svg></i> inspected.</span></h2>
        <p className="lead2">The SDK, redactor, store, evaluator, gate, API and dashboard each live in their own module.</p>
        <div className="bento">
          {cards.map((c) => (
            <div className={c.span} key={c.title}>
              <div className="ib" style={{ "--c": c.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24"><path d={c.icon} /></svg>
              </div>
              <h3>{c.title}</h3>
              <p>{c.body}</p>
              <div className="tags">
                {c.tags.map((t) => <span key={t}>{t}</span>)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}