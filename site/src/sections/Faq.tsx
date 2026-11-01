import { faq } from "../data/faq";
import { Disclosure } from "../components/Disclosure";

export function Faq() {
  return (
    <section id="faq" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Any questions?</h2>
        <div style={{ maxWidth: 820, margin: "30px auto 0" }}>
          {faq.map((f) => (
            <Disclosure key={f.q} question={f.q} answer={f.a} />
          ))}
        </div>
      </div>
    </section>
  );
}