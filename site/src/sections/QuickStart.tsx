import { useState } from "react";
import { content } from "../data/content";

type Shell = "bash" | "powershell";

export function QuickStart() {
  const [shell, setShell] = useState<Shell>("powershell");
  return <section className="sec" id="start"><div className="wrap">
    <h2>{content.quickstart.heading}</h2><p className="lead2">{content.quickstart.intro}</p>
    <div className="code-tabs" role="tablist" aria-label="Command shell">
      {(["powershell", "bash"] as const).map((item) => <button key={item} id={`shell-tab-${item}`} role="tab" aria-controls="quick-start-commands" aria-selected={shell === item} tabIndex={shell === item ? 0 : -1} onClick={() => setShell(item)}>{item === "bash" ? "Bash" : "PowerShell"}</button>)}
    </div>
    <div id="quick-start-commands" role="tabpanel" aria-labelledby={`shell-tab-${shell}`} className="steps qs">{content.quickstart.cards.map((card) => <article className="step" key={card.title}>
      <h3>{card.title}</h3><p>{card.body}</p><pre className="code"><code>{card[shell]}</code></pre>
    </article>)}</div>
    <p className="note">{content.quickstart.notice}</p>
  </div></section>;
}
