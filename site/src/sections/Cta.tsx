export function Cta() {
  return (
    <section className="cta2" aria-label="Get started">
      <div className="wrap">
        <h2>Run it.<br /><span className="m">Watch it get <i className="ico pulse" style={{ "--c": "#ef4444" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M12 8v5M12 17h.01"/></svg></i> caught.</span></h2>
        <div className="btns">
          <a className="pill w" href="https://github.com/nihalmachhi/CipherScope">View on GitHub</a>
          <a className="pill" href="#try">Back to the simulator</a>
        </div>
      </div>
    </section>
  );
}