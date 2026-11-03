import { faq } from "../data/faq";
import { content } from "../data/content";

export function Faq() {
  return (
    <section className="sec" id="faq">
      <div className="wrap">
        <h2>{content.faqHeading}</h2>
        <div className="faq">
          {faq.map((f) => (
            <details key={f.q}>
              <summary>{f.q}</summary>
              <p>{f.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
