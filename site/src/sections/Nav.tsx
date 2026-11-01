import { content } from "../data/content";

export function Nav() {
  return (
    <nav style={{ display: "flex", alignItems: "center", gap: 26, height: 72 }}>
      <div className="wrap" style={{ display: "flex", alignItems: "center", gap: 26, width: "100%" }}>
        <a href="#top" style={{ display: "flex", gap: 9, alignItems: "center", fontWeight: 600, fontFamily: "var(--fd)", textDecoration: "none", letterSpacing: "-0.02em" }}>
          <img src="/readme-icon.png" alt="CipherScope" width={22} height={22} />
          {content.name}
        </a>
        <div style={{ display: "flex", gap: 24, color: "var(--mu)", fontSize: "0.92rem", marginLeft: 14 }}>
          {content.nav.links.map((l) => (
            <a key={l.href} href={l.href}>{l.label}</a>
          ))}
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <a className="pill" href="https://github.com/nihalmachhi/CipherScope" style={{ minHeight: 38, padding: "0 18px", borderRadius: 999, background: "var(--p2)", border: "1px solid var(--ln)", display: "inline-flex", alignItems: "center" }}>GitHub</a>
          <a className="pill" href="#start" style={{ minHeight: 38, padding: "0 18px", borderRadius: 999, background: "var(--wh)", color: "#111", border: "1px solid var(--wh)", display: "inline-flex", alignItems: "center" }}>Run it locally</a>
        </div>
      </div>
    </nav>
  );
}