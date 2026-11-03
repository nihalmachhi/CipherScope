import { content } from "../data/content";

export function Features() {
  return <section className="sec" id="features"><div className="wrap">
    <h2>{content.features.heading}</h2><p className="lead2">{content.features.intro}</p>
    <div className="bento">{content.features.cards.map((card, index) => <article className={`bc ${index === 8 ? "f" : ""}`} key={card.title}>
      <div className="ib" style={{ "--c": "#f5c521" } as React.CSSProperties} aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M5 12h14M12 5l7 7-7 7" /></svg></div>
      <h3>{card.title}</h3><p>{card.body}</p><div className="tags">{card.tags.map((tag) => <span key={tag}>{tag}</span>)}</div>
    </article>)}</div>
  </div></section>;
}
