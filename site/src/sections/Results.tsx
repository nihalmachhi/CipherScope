import results from "../data/results.generated.json";

export function Results() {
  const r = results as {
    random_split: { macro_f1: number; std: number };
    cross_environment: { macro_f1: number; std: number };
    data_kind: string;
  };
  return (
    <section className="sec" id="results">
      <div className="wrap">
        <h2>Compared on the <span className="m">same <i className="ico" style={{ "--c": "#06b6d4" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M7 19v-6M12 19V6M17 19v-10"/></svg></i> four cases.</span></h2>
        <p className="lead2">Both prompts run the traceforge-faq-v1 dataset. Figures from the bundled demo run:</p>
        <div className="rg">
          <div className="rc">
            <h3>Baseline</h3>
            <p>The reference prompt every candidate is compared against.</p>
            <div className="tb">
              <div className="mr"><span>Task</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "#8c8c95" } as React.CSSProperties} /></div><b>100%</b></div>
              <div className="mr"><span>Grounded</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "#8c8c95" } as React.CSSProperties} /></div><b>100%</b></div>
              <div className="mr"><span>Relevance</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "#8c8c95" } as React.CSSProperties} /></div><b>100%</b></div>
            </div>
          </div>
          <div className="rc">
            <h3>Candidate</h3>
            <p>An intentionally regressed prompt that fails two cases.</p>
            <div className="tb">
              <div className="mr"><span>Task</span><div className="track"><div className="grow" style={{ "--w": `${r.random_split.macro_f1 * 100}%`, "--c": "var(--bad)" } as React.CSSProperties} /></div><b>{(r.random_split.macro_f1 * 100).toFixed(0)}%</b></div>
              <div className="mr"><span>Grounded</span><div className="track"><div className="grow" style={{ "--w": `${r.cross_environment.macro_f1 * 100}%`, "--c": "var(--bad)" } as React.CSSProperties} /></div><b>{(r.cross_environment.macro_f1 * 100).toFixed(0)}%</b></div>
            </div>
          </div>
          <div className="rc">
            <h3>Gate</h3>
            <p>Default limits: task success 0 points, groundedness 5 points.</p>
            <div className="tb">
              <div className="mr"><span>Task</span><div className="track"><div className="grow" style={{ "--w": "50%", "--c": "#a78bfa" } as React.CSSProperties} /></div><b>−50 pts</b></div>
              <div className="mr"><span>Result</span><div className="track"><div className="grow" style={{ "--w": "100%", "--c": "#a78bfa" } as React.CSSProperties} /></div><b>exit 1</b></div>
            </div>
          </div>
        </div>
        <p className="note">Synthetic data. These numbers show the pipeline works; they are not evidence of real-world detection.</p>
      </div>
    </section>
  );
}