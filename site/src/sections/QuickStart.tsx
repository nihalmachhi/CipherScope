export function QuickStart() {
  return (
    <section className="sec" id="start">
      <div className="wrap">
        <h2>One minute <span className="m">to a <i className="ico" style={{ "--c": "#22c55e" } as React.CSSProperties}><svg viewBox="0 0 24 24"><path d="M7 19v-6M12 19V6M17 19v-10"/></svg></i> dashboard.</span></h2>
        <p className="lead2">Python 3.11 or newer and nothing else. On macOS or Linux set PYTHONPATH=src and run python -m traceforge.cli.</p>
        <div className="steps qs">
          <div className="step">
            <h3>1. Set up</h3>
            <p>Create a virtual environment and activate it.</p>
            <div className="code"><span className="c"># PowerShell</span><br />uv sync --extra dev<br />cp .env.example .env</div>
          </div>
          <div className="step">
            <h3>2. Record and serve</h3>
            <p>Record both prompt runs, then open the dashboard on loopback.</p>
            <div className="code">make demo<br />make evaluate<br /><span className="c"># 127.0.0.1:8000</span></div>
          </div>
          <div className="step">
            <h3>3. Gate the build</h3>
            <p>Exit 1 on a regression, or allow a task-success drop.</p>
            <div className="code">uv run uvicorn cipherscope.api.main:create_app --factory<br />cd site && npm run dev</div>
          </div>
        </div>
      </div>
    </section>
  );
}