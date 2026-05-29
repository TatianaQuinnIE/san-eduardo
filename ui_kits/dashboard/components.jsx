/* San Eduardo Dashboard — UI components + tab panels. Exported to window. */

const DIcon = ({ d, size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {d.split(" M").map((s, i) => <path key={i} d={(i ? "M" : "") + s} />)}
  </svg>
);
const ICO = {
  home:"M3 11l9-8 9 8 M5 10v10h14V10", chart:"M3 3v18h18 M7 14l4-4 3 3 5-6", check:"M20 6L9 17l-5-5",
  brain:"M12 5a3 3 0 0 0-3 3 3 3 0 0 0-3 3 3 3 0 0 0 1 5 3 3 0 0 0 5 1 3 3 0 0 0 5-1 3 3 0 0 0 1-5 3 3 0 0 0-3-3 3 3 0 0 0-3-3z",
  db:"M12 2c5 0 9 1.3 9 3s-4 3-9 3-9-1.3-9-3 4-3 9-3z M21 5v14c0 1.7-4 3-9 3s-9-1.3-9-3V5 M21 12c0 1.7-4 3-9 3s-9-1.3-9-3",
  layers:"M12 2l9 5-9 5-9-5 9-5z M3 12l9 5 9-5 M3 17l9 5 9-5", target:"M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20z M12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z M12 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2z",
  arrow:"M5 12h14M13 5l7 7-7 7",
};

/* ── METRIC CARD ──────────────────────────────────────────── */
const TONES = ['clay', 'gold', 'green', 'forest'];
function Metric({ label, value, sub, tone = 'clay' }) {
  return (
    <div className={"metric metric--" + tone}>
      <div className="metric__label">{label}</div>
      <div className="metric__value">{value}</div>
      {sub && <div className="metric__sub">{sub}</div>}
    </div>
  );
}

/* ── SECTION HEADER ───────────────────────────────────────── */
function SecHead({ icon, eyebrow, title, lead }) {
  return (
    <div className="sechead">
      <div className="eyebrow"><DIcon d={ICO[icon]} size={14} /><span>{eyebrow}</span></div>
      <h2 className="sechead__title">{title}</h2>
      {lead && <p className="sechead__lead">{lead}</p>}
    </div>
  );
}

function Note({ tone = 'ok', children }) {
  return <div className={"note note--" + tone}><span className="note__bar" />{children}</div>;
}

function Panel({ title, cap, children, dark }) {
  return (
    <div className={"panel" + (dark ? " panel--dark" : "")}>
      {title && <div className="panel__head"><span className="panel__title">{title}</span>{cap && <span className="panel__cap">{cap}</span>}</div>}
      {children}
    </div>
  );
}

/* ── TAB PANELS ───────────────────────────────────────────── */
function TabRodeo({ t }) {
  const ihm = [{k:'2022',v:0.41},{k:'2023',v:0.44},{k:'2024',v:0.43},{k:'2025',v:0.47},{k:'2026',v:0.45}];
  const recs = [{k:'2022',v:980},{k:'2023',v:1120},{k:'2024',v:1080},{k:'2025',v:1210},{k:'2026',v:875}];
  const accents = ['var(--green-500)','var(--clay-500)','var(--gold-500)','var(--ink-500)'];
  return (
    <div className="tabpanel">
      <SecHead icon="home" eyebrow={t.hero.eyebrow} title={t.rodeo.h} lead={t.rodeo.lead} />
      <div className="metric-grid metric-grid--4">
        {t.rodeo.cards.map((c, i) => <Metric key={i} label={c[0]} value={c[1]} sub={c[2]} tone={['crimson','gold','green','forest'][i]} />)}
      </div>
      <div className="two-col">
        <Panel title={t.rodeo.chart1} cap={t.rodeo.chart1cap}><LineChart data={ihm} /></Panel>
        <Panel dark title={t.rodeo.chart2} cap={t.rodeo.chart2cap}><BarChart data={recs} color="#F2C53D" /></Panel>
      </div>
      <Note tone="ok">{t.rodeo.note}</Note>
    </div>
  );
}

function TabAudit({ t }) {
  const accents = ['var(--green-500)','var(--clay-500)','var(--gold-500)'];
  return (
    <div className="tabpanel">
      <SecHead icon="check" eyebrow={t.tabs[1]} title={t.audit.h} lead={t.audit.lead} />
      <div className="metric-grid metric-grid--3">
        {t.audit.cards.map((c, i) => <Metric key={i} label={c[0]} value={c[1]} sub={c[2]} tone={['green','clay','gold'][i]} />)}
      </div>
      <Panel title={t.audit.chart} cap={t.audit.chartcap}><HBars data={t.audit.bars} max={100} colorMode="rank" /></Panel>
      <Note tone="warn">{t.audit.note}</Note>
    </div>
  );
}

function TabModel({ t }) {
  return (
    <div className="tabpanel">
      <SecHead icon="brain" eyebrow={t.tabs[2]} title={t.model.h} lead={t.model.lead} />
      <div className="metric-grid metric-grid--4">
        {t.model.cards.map((c, i) => <Metric key={i} label={c[0]} value={c[1]} sub={c[2]} tone={['forest','green','gold','crimson'][i]} />)}
      </div>
      <div className="two-col">
        <Panel dark title={t.model.shapT} cap={t.model.shapCap}><HBars data={t.model.shap} max={100} unit="" colorMode="darkshap" /></Panel>
        <Panel title={t.model.compT} cap={t.model.compCap}><HBars data={t.model.comp} max={50} colorMode="green" baselineLast /></Panel>
      </div>
      <Note tone="warn">{t.model.note}</Note>
    </div>
  );
}

function TabGaps({ t }) {
  return (
    <div className="tabpanel">
      <SecHead icon="db" eyebrow={t.tabs[3]} title={t.gaps.h} lead={t.gaps.lead} />
      <div className="metric-grid metric-grid--3">
        {t.gaps.summary.map((s, i) => <Metric key={i} label={s[1]} value={s[0]} tone={s[2]} />)}
      </div>
      <div className="table-wrap">
        <table className="dtable">
          <thead><tr>{t.gaps.cols.map((c, i) => <th key={i} className={i>0?'center':''}>{c}</th>)}</tr></thead>
          <tbody>
            {t.gaps.rows.map((r, i) => (
              <tr key={i}>
                <td className="dtable__strong">{r[0]}</td>
                <td className="center"><span className={"pill pill--" + t.gaps.statusTone[r[1]]}>{r[1]}</span></td>
                <td className="center">{r[2]}</td>
                <td className="center dtable__muted">{r[3]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function TabVision({ t }) {
  const tones = ['green', 'gold', 'clay'];
  return (
    <div className="tabpanel">
      <SecHead icon="layers" eyebrow={t.tabs[4]} title={t.vision.h} lead={t.vision.lead} />
      <div className="phase-grid">
        {t.vision.phases.map((p, i) => (
          <div className={"dphase dphase--" + tones[i]} key={i}>
            <div className="dphase__top">
              <span className="dphase__idx">{String(i + 1).padStart(2, '0')}</span>
              <span className="dphase__year">{p[0]}</span>
            </div>
            <div className="dphase__name">{p[1]}</div>
            <ul>{p[2].map((it, j) => <li key={j}>{it}</li>)}</ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function TabM2({ t }) {
  const accents = ['var(--green-500)','var(--clay-500)','var(--gold-500)','var(--ink-500)'];
  const ruleCls = (r) => r.includes('★★★') ? 'star3' : r.includes('★★') ? 'star2' : r.includes('★') ? 'star1' : 'none';
  return (
    <div className="tabpanel">
      <SecHead icon="target" eyebrow={t.tabs[5]} title={t.m2.h} lead={t.m2.lead} />
      <div className="metric-grid metric-grid--4">
        {t.m2.cards.map((c, i) => <Metric key={i} label={c[0]} value={c[1]} sub={c[2]} tone={['green','gold','crimson','forest'][i]} />)}
      </div>
      <Panel title={t.m2.tableT}>
        <div className="table-wrap">
          <table className="dtable dtable--rank">
            <thead><tr>{t.m2.cols.map((c, i) => <th key={i} className={i>1?'center':''}>{c}</th>)}</tr></thead>
            <tbody>
              {t.m2.rows.map((r, i) => (
                <tr key={i}>
                  <td className="dtable__rank">{r[0]}</td>
                  <td className="mono">{r[1]}</td>
                  <td className="center">
                    <div className="scorebar"><div className="scorebar__fill" style={{ width: (Number(r[2])/0.65*100)+'%' }} /><span>{r[2]}</span></div>
                  </td>
                  <td className="center">{r[3]==='Sí'||r[3]==='Yes' ? <span className="pill pill--ok">{r[3]}</span> : <span className="dtable__muted">—</span>}</td>
                  <td className={"center stars stars--" + ruleCls(r[4])}>{r[4]}</td>
                  <td className="center mono">{r[5]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <Note tone="ok">{t.m2.note}</Note>
    </div>
  );
}

Object.assign(window, { DIcon, ICO, Metric, SecHead, Note, Panel, TabRodeo, TabAudit, TabModel, TabGaps, TabVision, TabM2 });
