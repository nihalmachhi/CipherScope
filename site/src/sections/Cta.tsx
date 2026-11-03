import { useInView } from "../hooks/useInView";
import { content } from "../data/content";

export function Cta() {
  const { ref, inView } = useInView(0.25, true);
  return <section className="cta2" aria-label="Get started"><div className="wrap">
    <div ref={ref} className={`rv-wrap ${inView ? "arm" : ""}`}><h2 className="rv">{content.cta.heading}<br /><span className="m">{content.cta.subheading}</span></h2></div>
    <p className="lead2">{content.cta.copy}</p>
    <div className="btns"><a className="pill w" href="https://github.com/nihalmachhi/CipherScope">{content.cta.github}</a><a className="pill" href="#start">{content.cta.run}</a></div>
  </div></section>;
}
