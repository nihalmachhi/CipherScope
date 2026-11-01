export function Cta() {
  return (
    <section style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <div style={{ marginTop: 84, background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 24, padding: "56px 20px 52px", textAlign: "center" }}>
          <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.28, maxWidth: "none", marginTop: 26 }}>Run it. Watch it get caught.</h2>
          <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 24, flexWrap: "wrap" }}>
            <a href="https://github.com/nihalmachhi/CipherScope" style={{ minHeight: 42, padding: "0 22px", borderRadius: 999, background: "var(--wh)", color: "#111", display: "inline-flex", alignItems: "center" }}>View on GitHub</a>
            <a href="#try" style={{ minHeight: 42, padding: "0 22px", borderRadius: 999, background: "var(--p2)", border: "1px solid var(--ln)", display: "inline-flex", alignItems: "center" }}>Back to the simulator</a>
          </div>
        </div>
      </div>
    </section>
  );
}