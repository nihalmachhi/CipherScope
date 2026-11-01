export function Pipeline() {
  const steps = [
    { title: "1. Record", body: "A context-manager SDK wraps each step in a span. Retrieval, tool calls and model calls nest under one agent workflow automatically.", color: "#8b5cf6", mini: "trace › agent › retrieval · tool · llm" },
    { title: "2. Redact", body: "Keys like api_key and password, bearer tokens and emails become [REDACTED] before anything reaches storage. It is best effort.", color: "#f59e0b", mini: "api_key → [REDACTED]" },
    { title: "3. Compare", body: "Baseline and candidate prompts run on the same cases. Task success, groundedness, latency and cost sit side by side, and the gate decides.", color: "#f97316", mini: "gate exits 1 on a regression" },
  ];
  return (
    <section className="sec" id="how">
      <div className="wrap">
        <h2>Three steps. <span className="m">One <i className="ico" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></i> regression trail.</span></h2>
        <p className="lead2">Every run becomes one trace, and every trace is scored against the same expected facts.</p>
        <div className="steps">
          {steps.map((s) => (
            <div className="step" key={s.title}>
              <div className="ib" style={{ "--c": s.color } as React.CSSProperties}>
                <svg viewBox="0 0 24 24"><path d="M5 7h14M5 12h14M5 17h14"/></svg>
              </div>
              <h3>{s.title}</h3>
              <p>{s.body}</p>
              <div className="mini"><b>{s.mini}</b></div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}