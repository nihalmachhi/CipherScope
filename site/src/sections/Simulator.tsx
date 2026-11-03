import { useMemo, useState } from "react";
import { detectBeacons, periodicityScore } from "../features/simulator/engine";
import { content } from "../data/content";
import styles from "./Simulator.module.css";

type Traffic = "beacon" | "web" | "streaming";

function makeTimes(kind: Traffic, period: number, jitter: number, count: number): number[] {
  return Array.from({ length: count }, (_, i) => {
    const offset = kind === "beacon" ? Math.sin(i * 1.7) : kind === "web" ? Math.sin(i * 12.9) * 0.8 + (i % 3) * 0.35 : Math.sin(i * 2.1) * 5;
    return i * period + offset * period * jitter / 100;
  });
}

export function Simulator() {
  const [traffic, setTraffic] = useState<Traffic>("beacon");
  const [period, setPeriod] = useState(30);
  const [jitter, setJitter] = useState(8);
  const [padding, setPadding] = useState(0);
  const [threshold, setThreshold] = useState(0.75);
  const [count, setCount] = useState(8);
  const times = useMemo(() => makeTimes(traffic, period, jitter, count), [traffic, period, jitter, count]);
  const result = periodicityScore(times);
  const alert = detectBeacons(times.map((started_at) => ({ host_hash: "h:demo-a", peer_hash: "h:demo-b", started_at })), { threshold });
  const flows = Array.from({ length: 28 }, (_, i) => Math.max(9, Math.min(64, 14 + (i % 7) * 5 + Math.sin(i * 2) * padding)));
  return <section className="sec" id="try"><div className="wrap">
    <h2>{content.simulator.heading}</h2>
    <p className="lead2">{content.simulator.intro}</p>
    <div className={styles.lab}>
      <div className={styles.controls}>
        <label>{content.simulator.traffic}<select value={traffic} onChange={(e) => setTraffic(e.target.value as Traffic)}><option value="web">{content.simulator.web}</option><option value="streaming">{content.simulator.streaming}</option><option value="beacon">{content.simulator.beacon}</option></select></label>
        <label>{content.simulator.period} <output>{period} s</output><input type="range" min="5" max="120" value={period} onChange={(e) => setPeriod(+e.target.value)} /></label>
        <label>{content.simulator.jitter} <output>{jitter}%</output><input type="range" min="0" max="60" value={jitter} onChange={(e) => setJitter(+e.target.value)} /></label>
        <label>{content.simulator.padding} <output>{padding}%</output><input type="range" min="0" max="50" value={padding} onChange={(e) => setPadding(+e.target.value)} /></label>
        <label>{content.simulator.connections} <output>{count}</output><input type="range" min="4" max="20" value={count} onChange={(e) => setCount(+e.target.value)} /></label>
        <label>{content.simulator.threshold} <output>{threshold.toFixed(2)}</output><input type="range" min="0.5" max="0.95" step="0.05" value={threshold} onChange={(e) => setThreshold(+e.target.value)} /></label>
        <button className="pill" type="button" onClick={() => { setTraffic("beacon"); setJitter(60); }}>{content.simulator.evade}</button>
      </div>
      <div className={styles.output}>
        <div className={styles.result} aria-live="polite"><span className={alert.length ? styles.flagged : ""}>{alert.length ? content.simulator.candidate : content.simulator.noCandidate}</span><b>{result.score.toFixed(3)}</b><small>{content.simulator.score} · {content.simulator.interval} {result.period_s.toFixed(1)} s</small><p>{content.simulator.explanation}</p></div>
        <div className={styles.chart} aria-label={content.simulator.shape}><div className={styles.bars}>{flows.map((height, i) => <i key={i} style={{ "--bar-height": `${height}px`, "--bar-align": i % 2 ? "flex-end" : "flex-start" } as React.CSSProperties} />)}</div><small>{content.simulator.shape}</small></div>
        <div className={styles.intervals}><small>{content.simulator.observed}</small><div>{times.slice(1).map((time, i) => <span key={i} style={{ "--interval-width": `${Math.max(4, Math.min(100, ((time - times[i]) / period) * 50))}%` } as React.CSSProperties} />)}</div></div>
      </div>
    </div>
  </div></section>;
}
