export function Scope() {
  return (
    <section id="scope" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Built to teach.</h2>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 40 }}>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 24, padding: 30 }}>
            <h3 style={{ fontSize: "1.3rem", marginBottom: 18 }}>In scope</h3>
            <ul style={{ color: "var(--mu)", lineHeight: 2, paddingLeft: 20 }}>
              <li>Offline PCAP/Zeek ingestion</li>
              <li>Keyed-hash privacy</li>
              <li>Flow/sequence/graph features</li>
              <li>Leakage-aware splits</li>
              <li>Model zoo with calibration</li>
              <li>Beacon detection, drift</li>
              <li>Local API and dashboard</li>
            </ul>
          </div>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 24, padding: 30 }}>
            <h3 style={{ fontSize: "1.3rem", marginBottom: 18 }}>Out of scope</h3>
            <ul style={{ color: "var(--mu)", lineHeight: 2, paddingLeft: 20 }}>
              <li>Decryption or interception</li>
              <li>Payload inspection</li>
              <li>Live capture</li>
              <li>Individual browsing profiling</li>
              <li>Production deployment</li>
              <li>Real-world detection claims from synthetic data</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}