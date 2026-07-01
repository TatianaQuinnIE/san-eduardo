/* San Eduardo Dashboard — app shell: topbar, hero strip, tab nav, panels */
const TAB_ICONS = ['home','check','brain','db','layers','target'];
const PANELS = [TabRodeo, TabAudit, TabModel, TabGaps, TabVision, TabM2];

function DashApp() {
  const [lang, setLang] = React.useState(() => localStorage.getItem('se_lang') || 'es');
  const [tab, setTab] = React.useState(() => {
    const p = Number(new URLSearchParams(location.search).get('tab'));
    if (!Number.isNaN(p) && p >= 0 && p <= 5) return p;
    return Number(localStorage.getItem('se_dash_tab') || 0);
  });
  React.useEffect(() => { localStorage.setItem('se_lang', lang); }, [lang]);
  React.useEffect(() => { localStorage.setItem('se_dash_tab', tab); }, [tab]);
  const t = window.SE_DASH[lang];
  const Panel = PANELS[tab];

  return (
    <div className="scroll-root">
      <header className="dnav">
        <a className="dnav__brand" href="../landing/index.html">
          <img src="../../assets/logo-mark-terracotta.png" className="dnav__logo" alt="" />
          <div className="dnav__name">
            <span className="dnav__name-main">San Eduardo</span>
            <span className="dnav__name-sub mono">{t.subtitle}</span>
          </div>
        </a>
        <div className="dnav__right">
          <a className="dnav__back" href="../landing/index.html"><DIcon d={ICO.arrow} size={15} /><span style={{transform:'scaleX(-1)',display:'inline-block'}}></span>{t.back}</a>
          <div className="nav__lang">
            <button className={lang === 'es' ? 'on' : ''} onClick={() => setLang('es')}>ES</button>
            <button className={lang === 'en' ? 'on' : ''} onClick={() => setLang('en')}>EN</button>
          </div>
        </div>
      </header>

      <section className="dhero">
        <div className="dhero__bg" />
        <div className="dhero__inner">
          <div className="dhero__eyebrow mono">{t.hero.eyebrow}</div>
          <h1 className="dhero__title">{t.appTitle}</h1>
          <div className="dhero__stats">
            {[['2.728',t.hero.s[0]],['5.265',t.hero.s[1]],['5',t.hero.s[2]],['49%',t.hero.s[3]]].map(([n,l],i)=>(
              <div className="dhero__stat" key={i}><span className="dhero__statnum">{n}</span><span className="dhero__statlbl mono">{l}</span></div>
            ))}
          </div>
        </div>
      </section>

      <nav className="dtabs">
        <div className="dtabs__inner">
          {t.tabs.map((label, i) => (
            <button key={i} className={"dtab" + (tab === i ? " dtab--on" : "")} onClick={() => setTab(i)}>
              <DIcon d={ICO[TAB_ICONS[i]]} size={15} /><span>{label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="dmain">
        <Panel t={t} />
      </main>

      <footer className="dfooter mono">San Eduardo · Bragado, BA — IE University ML Foundations 2026</footer>
    </div>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<DashApp />);
