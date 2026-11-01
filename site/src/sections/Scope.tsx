export function Scope() {
  return (
    <section className="sec" id="scope">
      <div className="wrap">
        <h2>Built to <i className="ico" style={{ "--c": "#f97316" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M9 18h6M10 21h4M12 3a6 6 0 00-3.5 10.9c.6.5 1 1.2 1 2.1h5c0-.9.4-1.6 1-2.1A6 6 0 0012 3z"/></svg></i> <span className="m">teach.</span></h2>
        <p className="lead2">CipherScope is for learning how traffic metadata and regression testing work. It is not a production detection tool.</p>
        <div className="sc">
          <div className="scc">
            <div className="ib" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
            <h3>In scope</h3>
            <ul><li>Offline PCAP/Zeek ingestion</li><li>Keyed-hash privacy</li><li>Flow/sequence/graph features</li><li>Leakage-aware splits</li><li>Model zoo with calibration</li><li>Beacon detection, drift</li><li>Local API and dashboard</li></ul>
          </div>
          <div className="scc">
            <div className="ib" style={{ "--c": "#ef4444" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></div>
            <h3>Out of scope</h3>
            <ul><li>Decryption or interception</li><li>Payload inspection</li><li>Live capture</li><li>Individual browsing profiling</li><li>Production deployment</li><li>Real-world detection claims from synthetic data</li></ul>
          </div>
        </div>
      </div>
    </section>
  );
}