import results from "../data/results.generated.json";
import { content } from "../data/content";

type Metric = { macro_f1: number; accuracy: number };
const report = results as {
  random_split: { macro_f1: number; std: number };
  cross_environment: { macro_f1: number; std: number };
  robustness: Record<string, Metric>;
  data_kind: string;
};

function Bar({ label, value }: { label: string; value: number }) {
  return <div className="result-row"><span>{label}</span><div className="track"><i style={{ "--result-width": `${Math.max(0, Math.min(100, value * 100))}%` } as React.CSSProperties} /></div><b>{(value * 100).toFixed(1)}%</b></div>;
}

export function Results() {
  const robust = report.robustness;
  return (
    <section className="sec" id="results">
      <div className="wrap">
        <h2>{content.results.heading}</h2>
        <p className="lead2">{content.results.intro.replace("synthetic", report.data_kind)}</p>
        <div className="rg">
          <article className="rc"><h3>{content.results.randomTitle}</h3><p>{content.results.randomCopy}</p><Bar label="Macro F1" value={report.random_split.macro_f1} /><small>Across configured seeds; σ {(report.random_split.std * 100).toFixed(2)} points.</small></article>
          <article className="rc"><h3>{content.results.environmentTitle}</h3><p>{content.results.environmentCopy}</p><Bar label="Macro F1" value={report.cross_environment.macro_f1} /><small>Across configured seeds; σ {(report.cross_environment.std * 100).toFixed(2)} points.</small></article>
          <article className="rc"><h3>{content.results.robustnessTitle}</h3><p>{content.results.robustnessCopy}</p><Bar label={content.results.firstPacketLabel} value={robust.first_4_packets.macro_f1} /><Bar label={content.results.cleanLabel} value={robust.clean.macro_f1} /><small>{content.results.robustnessDetail}</small></article>
        </div>
        <p className="note">{content.results.syntheticNote}</p>
      </div>
    </section>
  );
}
