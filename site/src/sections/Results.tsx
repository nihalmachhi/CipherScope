import results from "../data/results.generated.json";

export function Results() {
  const r = results as {
    random_split: { macro_f1: number; std: number };
    cross_environment: { macro_f1: number; std: number };
    data_kind: string;
  };
  const cards = [
    { title: "Random split (caution)", value: r.random_split.macro_f1 },
    { title: "Cross-environment", value: r.cross_environment.macro_f1 },
  ];
  return (
    <section id="results" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Compared on the same four cases.</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>Numbers come only from results.generated.json ({r.data_kind} data).</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginTop: 34 }}>
          {cards.map((c) => (
            <div key={c.title} style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 20, padding: 24 }}>
              <h3 style={{ fontSize: "1.15rem" }}>{c.title}</h3>
              <div style={{ marginTop: 18 }}>
                <div style={{ display: "grid", gridTemplateColumns: "78px 1fr 58px", gap: 12, alignItems: "center", fontFamily: "var(--fm)", fontSize: "0.76rem" }}>
                  <span>macro F1</span>
                  <div style={{ height: 6, borderRadius: 6, background: "var(--ln)", overflow: "hidden" }}>
                    <div style={{ height: "100%", width: `${c.value * 100}%`, background: "var(--ok)", borderRadius: 6 }} />
                  </div>
                  <b style={{ textAlign: "right" }}>{(c.value * 100).toFixed(1)}%</b>
                </div>
              </div>
            </div>
          ))}
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 20, padding: 24 }}>
            <h3 style={{ fontSize: "1.15rem" }}>Robustness</h3>
            <p style={{ color: "var(--mu)", fontSize: "0.9rem", marginTop: 6 }}>Padding, jitter and truncation curves in the report.</p>
          </div>
        </div>
        <p style={{ marginTop: 22, textAlign: "center", color: "var(--mu)", fontSize: "0.84rem", lineHeight: 1.7 }}>
          Synthetic data. These numbers show the pipeline works; they are not evidence of real-world detection.
        </p>
      </div>
    </section>
  );
}