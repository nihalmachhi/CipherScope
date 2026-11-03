import { useRef, useState } from "react";
import { useTour } from "../features/tour/useTour";
import { content } from "../data/content";
import styles from "./Window.module.css";

const tabs = content.tour;

export function Window() {
  const [held, setHeld] = useState(false);
  const { index, setIndex, paused, setPaused } = useTour(tabs.length, 7000, held);
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const active = tabs[index];
  return <div className={`${styles.window} ${held || paused ? styles.held : ""}`} onMouseEnter={() => setHeld(true)} onMouseLeave={() => setHeld(false)} onFocus={() => setHeld(true)} onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setHeld(false); }}>
    <aside className={styles.sidebar}><div className={styles.dots} aria-hidden="true"><i/><i/><i/></div><div className={styles.tabs} role="tablist" aria-label={content.tourControls.label}>
      {tabs.map((tab, i) => <button ref={(node) => { tabRefs.current[i] = node; }} id={`tour-tab-${i}`} aria-controls="tour-panel" aria-selected={i === index} tabIndex={i === index ? 0 : -1} role="tab" key={tab.name} onClick={() => setIndex(i)} onKeyDown={(event) => { if (event.key === "ArrowRight" || event.key === "ArrowLeft") { event.preventDefault(); const next = event.key === "ArrowRight" ? (index + 1) % tabs.length : (index - 1 + tabs.length) % tabs.length; setIndex(next); tabRefs.current[next]?.focus(); } }}><span>{tab.name}</span>{i === index && <i className={styles.progress}/>}</button>)}
    </div><div className={styles.local}>{content.tourControls.offlineLabel}</div></aside>
    <section className={styles.panel} role="tabpanel" id="tour-panel" aria-labelledby={`tour-tab-${index}`}>
      <div key={index} className={styles.main}><div className={styles.kicker}>CIPHERSCOPE / {String(index + 1).padStart(2,"0")}</div><h3>{active.name}</h3><p>{active.copy}</p><pre>{active.code}</pre></div>
      <aside className={styles.side}><span className={styles.sideTitle}>{content.tourControls.privacyLabel}</span><b>{active.label}</b><span>{active.value}</span><hr/><span>{active.detail}</span></aside>
      <button className={styles.pause} type="button" onClick={() => setPaused(!paused)} aria-label={paused ? content.tourControls.resume : content.tourControls.pause}>{paused ? "▶" : "Ⅱ"}</button>
    </section>
  </div>;
}
