const stages = ["PCAP", "Headers only", "Flows", "HMAC ids", "Features", "Splits", "Models", "Report", "API + UI"];

export function Architecture() {
  const boxWidth = 112;
  const gap = 30;
  return (
    <section id="architecture" style={{ padding: "84px 0 20px" }}>
      <div className="wrap">
        <h2 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", letterSpacing: "-0.035em", lineHeight: 1.05, maxWidth: "18ch" }}>Architecture.</h2>
        <p style={{ marginTop: 12, color: "var(--mu)", maxWidth: "60ch" }}>Stages light up in sequence.</p>
        <div style={{ overflowX: "auto", padding: "6px 4px 10px", marginTop: 24 }}>
          <svg className="flow arch" viewBox="0 0 964 90" role="img" aria-label="CipherScope pipeline" style={{ width: "100%", minWidth: 820, maxWidth: 964, height: "auto", overflow: "visible" }}>
            {stages.map((_, i) => {
              if (i === stages.length - 1) return null;
              const x1 = i * (boxWidth + gap) + boxWidth;
              const x2 = x1 + gap;
              return <path key={i} className="fl" d={`M${x1} 45H${x2}`} style={{ fill: "none", stroke: "#5a5a64", strokeWidth: 1.2, strokeDasharray: "4 4", animation: "dash 1.2s linear infinite" }} />;
            })}
            {stages.map((s, i) => {
              const x = i * (boxWidth + gap);
              const last = i === stages.length - 1;
              return (
                <g key={s} className={`gn st ${last ? "last" : ""}`} style={{ animation: `${last ? "stlb" : "stl"} 6.3s ease-in-out infinite`, animationDelay: `${i * 0.9}s` }}>
                  <rect x={x} y={12} width={boxWidth} height={66} rx={9} style={{ fill: "#19191c", stroke: "#242428" }} />
                  <text textAnchor="middle" style={{ font: "500 10px var(--fm)", fill: "#ececee" }}>
                    {s.split(" ").map((word, wi, arr) => (
                      <tspan key={wi} x={x + boxWidth / 2} y={12 + 30 + (wi - (arr.length - 1) / 2) * 13}>
                        {word}
                      </tspan>
                    ))}
                  </text>
                </g>
              );
            })}
            <circle r={3.2} fill="#f4f4f5">
              <animateMotion dur="6.3s" repeatCount="indefinite" path="M0 45H964" />
            </circle>
          </svg>
        </div>
      </div>
    </section>
  );
}