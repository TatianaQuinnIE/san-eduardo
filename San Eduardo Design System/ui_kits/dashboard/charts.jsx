/* San Eduardo Dashboard — hand-built SVG/CSS charts (no chart lib).
   Exported to window. Palette pulled from CSS custom properties. */
const CL = { clay:'#C0532E', clayDk:'#9A4620', green:'#2D6A4F', green3:'#95D5B2', gold:'#F2C53D', taupe:'#8B7355', line:'#E0D5C5', ink:'#2C1A0E', ink5:'#8B7355', cream:'#FBF8F1', crimson:'#E22A48' };

/* Line chart with area fill — IHM over time */
function LineChart({ data, w = 520, h = 240, yMin = 0.35, yMax = 0.52 }) {
  const pad = { l: 40, r: 16, t: 16, b: 30 };
  const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const x = i => pad.l + (i / (data.length - 1)) * iw;
  const y = v => pad.t + ih - ((v - yMin) / (yMax - yMin)) * ih;
  const pts = data.map((d, i) => [x(i), y(d.v)]);
  const path = pts.map((p, i) => (i ? 'L' : 'M') + p[0] + ' ' + p[1]).join(' ');
  const area = path + ` L${pts[pts.length-1][0]} ${pad.t+ih} L${pts[0][0]} ${pad.t+ih} Z`;
  const ticks = [0.35, 0.40, 0.45, 0.50];
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="chart" preserveAspectRatio="xMidYMid meet">
      {ticks.map((tk, i) => (
        <g key={i}>
          <line x1={pad.l} x2={w-pad.r} y1={y(tk)} y2={y(tk)} stroke={CL.line} strokeWidth="1" strokeDasharray="2 4" />
          <text x={pad.l-8} y={y(tk)+4} textAnchor="end" className="chart__axis">{tk.toFixed(2)}</text>
        </g>
      ))}
      <defs>
        <linearGradient id="lcfill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={CL.clay} stopOpacity="0.22" />
          <stop offset="100%" stopColor={CL.clay} stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill="url(#lcfill)" />
      <path d={path} fill="none" stroke={CL.clay} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      {pts.map((p, i) => (
        <g key={i}>
          <circle cx={p[0]} cy={p[1]} r="5" fill={CL.cream} stroke={CL.clay} strokeWidth="2.4" />
          <text x={p[0]} y={h-10} textAnchor="middle" className="chart__axis">{data[i].k}</text>
        </g>
      ))}
    </svg>
  );
}

/* Vertical bars — records per year */
function BarChart({ data, w = 440, h = 240, color = CL.green }) {
  const pad = { l: 16, r: 16, t: 24, b: 30 };
  const iw = w - pad.l - pad.r, ih = h - pad.t - pad.b;
  const max = Math.max(...data.map(d => d.v)) * 1.12;
  const bw = iw / data.length * 0.56;
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="chart" preserveAspectRatio="xMidYMid meet">
      {data.map((d, i) => {
        const bh = (d.v / max) * ih;
        const cx = pad.l + (i + 0.5) * (iw / data.length);
        return (
          <g key={i}>
            <rect x={cx - bw/2} y={pad.t + ih - bh} width={bw} height={bh} rx="6" fill={color} />
            <text x={cx} y={pad.t + ih - bh - 8} textAnchor="middle" className="chart__val">{d.v}</text>
            <text x={cx} y={h-10} textAnchor="middle" className="chart__axis">{d.k}</text>
          </g>
        );
      })}
    </svg>
  );
}

/* Horizontal bars with track + value — SHAP / agreement / comparison */
function HBars({ data, max = 100, unit = '%', highlightFirst = true, colorMode = 'clay', baselineLast = false }) {
  const colorFor = (i) => {
    if (colorMode === 'darkshap') return i === 0 ? CL.gold : CL.green3;
    if (colorMode === 'rank') { const c = [CL.clay, CL.gold, CL.green, CL.crimson, CL.ink5, CL.line]; return c[Math.min(i, c.length-1)]; }
    if (baselineLast && i === data.length - 1) return CL.taupe;
    return highlightFirst && i === 0 ? CL.clay : (colorMode === 'green' ? CL.green : CL.clayDk);
  };
  return (
    <div className="hbars">
      {data.map(([label, val], i) => {
        const v = Number(val);
        return (
          <div className="hbar" key={i}>
            <div className="hbar__label">{label}</div>
            <div className="hbar__track">
              <div className="hbar__fill" style={{ width: (v/max*100)+'%', background: colorFor(i) }} />
            </div>
            <div className="hbar__val">{v}{unit}</div>
          </div>
        );
      })}
    </div>
  );
}

Object.assign(window, { LineChart, BarChart, HBars, CL });
