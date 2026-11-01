import { content } from "../data/content";
import { Window } from "../components/Window";

export function Hero() {
  return (
    <header className="hero" id="top" style={{ textAlign: "center", padding: "30px 0 40px" }}>
      <h1 style={{ fontSize: "clamp(2.1rem,4.9vw,3.9rem)", fontWeight: 600, letterSpacing: "-0.045em", lineHeight: 1, maxWidth: "16ch", margin: "0 auto" }}>
        {content.hero.headline}
      </h1>
      <p style={{ maxWidth: "52ch", margin: "16px auto 0", color: "var(--mu)", fontSize: "1.02rem" }}>{content.hero.subcopy}</p>
      <div style={{ display: "flex", gap: 10, justifyContent: "center", marginTop: 20, flexWrap: "wrap" }}>
        <a href="#start" style={{ minHeight: 42, padding: "0 22px", borderRadius: 999, background: "var(--wh)", color: "#111", display: "inline-flex", alignItems: "center" }}>Run it locally</a>
        <a href="https://github.com/nihalmachhi/CipherScope" style={{ minHeight: 42, padding: "0 22px", borderRadius: 999, background: "var(--p2)", border: "1px solid var(--ln)", display: "inline-flex", alignItems: "center" }}>View on GitHub</a>
      </div>
      <div className="wrap">
        <Window />
      </div>
    </header>
  );
}