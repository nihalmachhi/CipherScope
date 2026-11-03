import styles from "./Architecture.module.css";
import { content } from "../data/content";
import { useReducedMotion } from "../hooks/useReducedMotion";

const width = 90;
const gap = 18;

export function Architecture() {
  const reduced = useReducedMotion();
  return <section className="sec" id="architecture"><div className="wrap">
    <h2>{content.architecture.heading}</h2>
    <p className="lead2">{content.architecture.intro}</p>
    <div className={styles.scroller}><svg className={`${styles.diagram} ${reduced ? styles.static : ""}`} viewBox="0 0 954 104" role="img" aria-label={`CipherScope data flow: ${content.architecture.stages.join(" to ")}`}>
      {content.architecture.stages.slice(0, -1).map((stage, index) => { const x = index * (width + gap) + width; return <path key={stage} className={styles.connector} d={`M${x} 52h${gap}`} />; })}
      {content.architecture.stages.map((stage, index) => { const x = index * (width + gap); return <g key={stage} className={`${styles.node} ${index === content.architecture.stages.length - 1 ? styles.final : ""}`} style={{ "--delay": `${index * 0.55}s` } as React.CSSProperties}><rect x={x} y="19" width={width} height="66" rx="10"/><text x={x + width / 2} y="57" textAnchor="middle">{stage}</text></g>; })}
      <circle className={styles.packet} r="3.5"><animateMotion dur="6.3s" repeatCount="indefinite" path="M0 52H954" /></circle>
    </svg></div>
  </div></section>;
}
