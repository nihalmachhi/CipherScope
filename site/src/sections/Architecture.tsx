export function Architecture() {
  const stages = ["PCAP", "Headers only", "Flows", "HMAC ids", "Features", "Splits", "Models", "Report", "API + UI"];
  return (
    <section id="architecture" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Architecture.</h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 24, alignItems: "center" }}>
          {stages.map((s, i) => (
            <span key={s} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ background: "var(--p2)", border: "1px solid var(--ln)", borderRadius: 9, padding: "8px 14px", fontFamily: "var(--fm)", fontSize: "0.74rem" }}>{s}</span>
              {i < stages.length - 1 && <span style={{ color: "var(--mu)" }}>→</span>}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}