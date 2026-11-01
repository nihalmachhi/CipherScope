import { CodeBlock } from "../components/CodeBlock";

export function QuickStart() {
  return (
    <section id="start" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>One minute to a dashboard.</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>Python 3.11 or newer and nothing else.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16, marginTop: 30 }}>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 22 }}>
            <h3 style={{ fontSize: "1.15rem", marginBottom: 8 }}>1. Set up</h3>
            <CodeBlock lines={["uv sync --extra dev", "cp .env.example .env"]} />
          </div>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 22 }}>
            <h3 style={{ fontSize: "1.15rem", marginBottom: 8 }}>2. Generate + evaluate</h3>
            <CodeBlock lines={["make demo", "make evaluate"]} />
          </div>
          <div style={{ background: "var(--p)", border: "1px solid var(--ln)", borderRadius: 16, padding: 22 }}>
            <h3 style={{ fontSize: "1.15rem", marginBottom: 8 }}>3. Run</h3>
            <CodeBlock lines={["uv run uvicorn cipherscope.api.main:create_app --factory", "cd dashboard && npm run dev"]} />
          </div>
        </div>
      </div>
    </section>
  );
}