/* San Eduardo — landing page app shell */
function App() {
  const [lang, setLang] = React.useState(
    () => localStorage.getItem('se_lang') || 'es'
  );
  React.useEffect(() => { localStorage.setItem('se_lang', lang); }, [lang]);
  const t = window.SE_I18N[lang];

  const scrollTo = (id) => {
    const node = document.getElementById(id);
    if (node) window.scrollTo({ top: node.getBoundingClientRect().top + window.scrollY - 64, behavior: 'smooth' });
  };
  const openDashboard = (tab = 0) => { window.location.href = '../dashboard/index.html?tab=' + tab; };

  return (
    <div className="scroll-root">
      <Nav t={t} lang={lang} setLang={setLang} onCta={() => openDashboard(0)} />
      <Hero t={t} onPrimary={() => openDashboard(1)} onSecondary={() => openDashboard(0)} />
      <Marquee items={t.marquee} />
      <Farm t={t} />
      <Finding t={t} />
      <Author t={t} />
      <CtaBand t={t} onCta={() => openDashboard(0)} />
      <Footer t={t} />
    </div>
  );
}
ReactDOM.createRoot(document.getElementById('root')).render(<App />);
