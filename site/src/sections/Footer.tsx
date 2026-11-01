export function Footer() {
  return (
    <footer style={{ padding: "54px 0 60px", color: "var(--mu)", fontSize: "0.88rem" }}>
      <div className="wrap">
        <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 24, padding: "34px 34px 0", overflow: "hidden" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1.6fr 1fr 1fr 1fr", gap: 24 }}>
            <div>
              <a href="#top" style={{ fontWeight: 700, fontFamily: "var(--fd)" }}>CipherScope</a>
              <p style={{ marginTop: 10, fontSize: "0.78rem", color: "var(--mu)", maxWidth: "30ch" }}>A local, synthetic tracer and regression tester for AI agents.</p>
            </div>
            <div>
              <h5 style={{ margin: "0 0 12px", fontSize: "0.68rem", letterSpacing: "0.14em", textTransform: "uppercase", color: "#62626b" }}>Product</h5>
              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 7, fontSize: "0.88rem" }}>
                <li><a href="#top">Overview</a></li>
                <li><a href="#how">Pipeline</a></li>
                <li><a href="#try">Simulator</a></li>
                <li><a href="#results">Results</a></li>
              </ul>
            </div>
            <div>
              <h5 style={{ margin: "0 0 12px", fontSize: "0.68rem", letterSpacing: "0.14em", textTransform: "uppercase", color: "#62626b" }}>Run it</h5>
              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 7, fontSize: "0.88rem" }}>
                <li><a href="#features">Features</a></li>
                <li><a href="#start">Quick start</a></li>
                <li><a href="#faq">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h5 style={{ margin: "0 0 12px", fontSize: "0.68rem", letterSpacing: "0.14em", textTransform: "uppercase", color: "#62626b" }}>Source</h5>
              <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: 7, fontSize: "0.88rem" }}>
                <li><a href="https://github.com/nihalmachhi/CipherScope">GitHub</a></li>
                <li><a href="https://github.com/nihalmachhi/CipherScope/tree/main/docs">Docs</a></li>
                <li><a href="https://github.com/nihalmachhi/CipherScope/issues">Issues</a></li>
              </ul>
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 14, flexWrap: "wrap", marginTop: 30, paddingTop: 16, borderTop: "1px solid var(--ln)", fontSize: "0.72rem", color: "#62626b" }}>
            <span>Synthetic demo. Scores, costs and latencies are illustrative, not real model quality or provider pricing.</span>
            <span>Python · SQLite · JSON · MIT License</span>
          </div>
          <div style={{ fontFamily: "var(--fd)", fontWeight: 700, fontSize: "clamp(3.2rem,16.5vw,13rem)", lineHeight: 0.82, textAlign: "center", margin: "26px 0 -0.17em", background: "linear-gradient(180deg,#f4f4f5 15%,#2c2c31 88%)", WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", userSelect: "none" }}>CipherScope</div>
        </div>
      </div>
    </footer>
  );
}