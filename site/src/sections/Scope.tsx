import { content } from "../data/content";

export function Scope() {
  return <section className="sec" id="scope"><div className="wrap">
    <h2>{content.scope.heading}</h2><p className="lead2">{content.scope.intro}</p>
    <div className="sc">
      <article className="scc"><div className="ib" style={{ "--c": "#4ade9a" } as React.CSSProperties} aria-hidden="true">✓</div><h3>{content.scope.inTitle}</h3><ul>{content.scope.inItems.map((item) => <li key={item}>{item}</li>)}</ul></article>
      <article className="scc"><div className="ib" style={{ "--c": "#ff7a45" } as React.CSSProperties} aria-hidden="true">×</div><h3>{content.scope.outTitle}</h3><ul>{content.scope.outItems.map((item) => <li key={item}>{item}</li>)}</ul></article>
    </div>
  </div></section>;
}
