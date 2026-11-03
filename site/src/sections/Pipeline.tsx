import { content } from "../data/content";

export function Pipeline() {
  return <section className="sec" id="how"><div className="wrap">
    <h2>{content.pipeline.heading}</h2><p className="lead2">{content.pipeline.intro}</p>
    <div className="steps">{content.pipeline.steps.map((step) => <article className="step" key={step.title}>
      <div className="ib" style={{ "--c": "#f5c521" } as React.CSSProperties} aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7" /></svg></div>
      <h3>{step.title}</h3><p>{step.body}</p><div className="mini"><b>{step.mini}</b></div>
    </article>)}</div>
  </div></section>;
}
