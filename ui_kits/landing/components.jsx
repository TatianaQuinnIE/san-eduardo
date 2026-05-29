/* San Eduardo — landing page components.
   Lucide-style 2px stroke icons defined inline (no CDN dependency).
   All components exported to window at the end. */

const SE_ICONS = {
  arrow:   "M5 12h14M13 5l7 7-7 7",
  chart:   "M3 3v18h18 M7 14l4-4 3 3 5-6",
  check:   "M20 6L9 17l-5-5",
  brain:   "M12 5a3 3 0 0 0-3 3 3 3 0 0 0-3 3 3 3 0 0 0 1 5 3 3 0 0 0 5 1 3 3 0 0 0 5-1 3 3 0 0 0 1-5 3 3 0 0 0-3-3 3 3 0 0 0-3-3z",
  database:"M12 2c5 0 9 1.3 9 3s-4 3-9 3-9-1.3-9-3 4-3 9-3z M21 5v14c0 1.7-4 3-9 3s-9-1.3-9-3V5 M21 12c0 1.7-4 3-9 3s-9-1.3-9-3",
  sprout:  "M7 20h10 M12 20V10 M12 10C12 6 9 4 5 4c0 4 3 6 7 6z M12 12c0-3 2-5 6-5 0 3-2 5-6 5z",
  pin:     "M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z M12 10a2 2 0 1 0 0-4 2 2 0 0 0 0 4z",
  signal:  "M2 20h.01 M7 20v-4 M12 20v-8 M17 20V8 M22 4v16",
  star:    "M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 18l-6 3.4 1.4-6.8L2.3 9.1l6.9-.8z",
  layers:  "M12 2l9 5-9 5-9-5 9-5z M3 12l9 5 9-5 M3 17l9 5 9-5",
  external:"M15 3h6v6 M10 14L21 3 M21 14v7H3V3h7",
};

function Icon({ name, size = 18, stroke = 2, fill = "none", className }) {
  const d = SE_ICONS[name] || "";
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill={fill} stroke="currentColor"
         strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" className={className}>
      {d.split(" M").map((seg, i) => <path key={i} d={(i ? "M" : "") + seg} />)}
    </svg>
  );
}

/* ── NAV ──────────────────────────────────────────────────────────────── */
function Nav({ t, lang, setLang, onCta }) {
  const [scrolled, setScrolled] = React.useState(false);
  React.useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 30);
    window.addEventListener('scroll', fn); fn();
    return () => window.removeEventListener('scroll', fn);
  }, []);
  const jump = (id) => () => {
    const node = document.getElementById(id);
    if (node) window.scrollTo({ top: node.getBoundingClientRect().top + window.scrollY - 64, behavior: 'smooth' });
  };
  const dash = (n) => "../dashboard/index.html?tab=" + n;
  return (
    <header className={"nav" + (scrolled ? " nav--scrolled" : "")}>
      <div className="nav__brand">
        <img src="../../assets/logo-mark-cream.png" alt="San Eduardo" className="nav__logo nav__logo--light" />
        <img src="../../assets/logo-mark-terracotta.png" alt="" className="nav__logo nav__logo--dark" />
        <div className="nav__name">
          <span className="nav__name-main">San Eduardo</span>
          <span className="nav__name-sub">{t.nav.sub}</span>
        </div>
      </div>
      <div className="nav__right">
        <div className="nav__sensor"><span className="nav__sensor-dot" />{t.sensor}</div>
        <div className="nav__lang" role="group" aria-label="language">
          <button className={lang === 'es' ? 'on' : ''} onClick={() => setLang('es')}>ES</button>
          <button className={lang === 'en' ? 'on' : ''} onClick={() => setLang('en')}>EN</button>
        </div>
        <button className="btn btn--solid btn--sm" onClick={onCta}>{t.nav.cta}</button>
      </div>
    </header>
  );
}

/* ── MARQUEE ──────────────────────────────────────────────────────────── */
function Marquee({ items }) {
  const run = [...items, ...items, ...items];
  return (
    <div className="marquee">
      <div className="marquee__track">
        {run.map((it, i) => (
          <span className="marquee__item" key={i}>{it}<span className="marquee__sep">✦</span></span>
        ))}
      </div>
    </div>
  );
}

/* ── HERO ─────────────────────────────────────────────────────────────── */
function Hero({ t, onPrimary, onSecondary }) {
  return (
    <section className="hero">
      <div className="hero__bg" style={{ backgroundImage: "url(../../assets/herd-running.jpg)" }} />
      <div className="hero__scrim" />
      <div className="hero__grain" />
      <div className="hero__inner">
        <div className="hero__eyebrow"><span className="hero__eyebrow-line" />{t.hero.eyebrow}</div>
        <h1 className="hero__title">
          {t.hero.title_a} <em>{t.hero.title_em}</em><br />{t.hero.title_b}
        </h1>
        <p className="hero__sub">{t.hero.sub}</p>
        <div className="hero__actions">
          <button className="btn btn--gold" onClick={onPrimary}>{t.hero.cta1}<Icon name="arrow" size={17} /></button>
        </div>
      </div>
    </section>
  );
}

/* ── FARM ─────────────────────────────────────────────────────────────── */
function Farm({ t }) {
  return (
    <section className="section farm" id="farm">
      <div className="farm__grid">
        <div className="farm__text">
          <Eyebrow icon="pin">{t.farm.eyebrow}</Eyebrow>
          <h2 className="h2">{t.farm.title}</h2>
          <p className="body">{t.farm.p1}</p>
          <p className="body">{t.farm.p2}</p>
          <p className="body">{t.farm.p3}</p>
          <div className="farm__tags">
            <span className="chip"><Icon name="pin" size={13} />{t.farm.tag1}</span>
            <span className="chip"><Icon name="sprout" size={13} />{t.farm.tag2}</span>
            <span className="chip"><Icon name="signal" size={13} />{t.farm.tag3}</span>
          </div>
        </div>
        <div className="farm__media">
          <div className="farm__photo" style={{ backgroundImage: "url(../../assets/herd-portrait.jpg)" }} />
          <div className="farm__photo-tag"><span className="mono">REC · WEST-3 PADDOCK</span></div>
        </div>
      </div>
    </section>
  );
}

/* ── FINDING — Lovable color-block row ────────────────────────────────── */
function Finding({ t }) {
  return (
    <section className="section finding" id="finding">
      <Eyebrow icon="chart" center>{t.finding.eyebrow}</Eyebrow>
      <p className="finding__lead lead">{t.finding.lead}</p>
      <div className="lgrid">
        <div className="lblock lblock--clay">
          <div className="lblock__top">
            <span className="ltag ltag--dark">{t.finding.b1_tag}</span>
            <span className="ltag ltag--round">TR-49</span>
          </div>
          <div className="lblock__bottom">
            <div className="lblock__title">{t.finding.b1_title}</div>
            <div className="lblock__text lblock__text--light">{t.finding.b1_text}</div>
          </div>
        </div>
        <div className="lblock lblock--gold">
          <div className="lblock__top">
            <span className="ltag ltag--dark2">{t.finding.b2_tag}</span>
            <span className="dot dot--green" />
          </div>
          <div className="lnum">{t.finding.bignum}</div>
          <div className="lblock__sub">{t.finding.b2_sub}</div>
          <div className="lblock__rule" />
          <div className="lblock__text">{t.finding.b2_text}</div>
        </div>
        <div className="lblock lblock--green">
          <div className="lblock__top">
            <span className="ltag ltag--light">{t.finding.b3_tag}</span>
          </div>
          <div className="lblock__greencontent">
            <div className="lnum lnum--light">{t.finding.b3_num}</div>
            <div className="lblock__text lblock__text--light">{t.finding.b3_text}</div>
          </div>
        </div>
      </div>
      <blockquote className="pullquote">{t.finding.quote}</blockquote>
    </section>
  );
}

/* ── MODEL — Lovable deep-green panel ─────────────────────────────────── */
function Model({ t }) {
  return (
    <section className="section model" id="model">
      <div className="greenpanel">
        <div className="greenpanel__grain" />
        <div className="greenpanel__head">
          <span className="ltag ltag--clay">{t.model.tag}</span>
          <h2 className="greenpanel__title">{t.model.title_a} <em>{t.model.title_em}</em> {t.model.title_b}</h2>
          <p className="greenpanel__lead">{t.model.lead}</p>
        </div>
        <div className="greenpanel__grid">
          <div className="lvgraph">
            <div className="lvgraph__cap">{t.model.shap_cap}</div>
            {t.model.shap.map(([label, val], i) => (
              <div className="lvbar" key={i}>
                <div className="lvbar__row">
                  <span className="lvbar__label">{label}</span>
                  <span className="lvbar__val">{val}</span>
                </div>
                <div className="lvbar__track"><div className="lvbar__fill" style={{ width: val + "%", background: i === 0 ? "var(--gold-500)" : "var(--green-300)" }} /></div>
              </div>
            ))}
          </div>
          <div className="statboxes">
            {t.model.boxes.map(([num, lbl], i) => (
              <div className="statbox" key={i}>
                <div className="statbox__num">{num}</div>
                <div className="statbox__lbl">{lbl}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

/* ── VISION ───────────────────────────────────────────────────────────── */
function Vision({ t }) {
  const accents = ['var(--green-500)', 'var(--gold-500)', 'var(--clay-500)'];
  return (
    <section className="section vision" id="vision">
      <div className="model__head">
        <Eyebrow icon="layers">{t.vision.eyebrow}</Eyebrow>
        <h2 className="h2">{t.vision.title}</h2>
        <p className="lead">{t.vision.lead}</p>
      </div>
      <div className="vision__grid">
        {t.vision.phases.map((p, i) => (
          <div className="phase" key={i} style={{ '--accent': accents[i] }}>
            <div className="phase__year mono">{p.y}</div>
            <div className="phase__name">{p.n}</div>
            <ul className="phase__list">
              {p.items.map((it, j) => <li key={j}>{it}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

/* ── AUTHOR ───────────────────────────────────────────────────────────── */
function Author({ t }) {
  return (
    <section className="section author">
      <div className="author__card">
        <div className="author__photo" style={{ backgroundImage: "url(../../assets/author_pro.jpg)" }} />
        <div className="author__body">
          <Eyebrow icon="signal">{t.author.eyebrow}</Eyebrow>
          <h3 className="author__name">{t.author.name}</h3>
          <div className="author__role mono">{t.author.role}</div>
          <p className="author__bio">{t.author.bio}</p>
          <div className="author__skills">
            {t.author.skills.map((s, i) => <span className="skill" key={i}>{s}</span>)}
          </div>
          <a className="author__link" href="https://www.linkedin.com/in/tatianaquinn" target="_blank" rel="noopener">
            {t.author.link}<Icon name="external" size={15} />
          </a>
        </div>
      </div>
    </section>
  );
}

/* ── CTA + FOOTER ─────────────────────────────────────────────────────── */
function CtaBand({ t, onCta }) {
  return (
    <section className="ctaband">
      <div className="ctaband__grain" />
      <div className="ctaband__inner">
        <h2 className="ctaband__title">{t.cta.title}</h2>
        <p className="ctaband__sub">{t.cta.sub}</p>
        <button className="btn btn--gold btn--lg" onClick={onCta}>{t.cta.btn}<Icon name="arrow" size={18} /></button>
      </div>
    </section>
  );
}

function Footer({ t }) {
  return (
    <footer className="footer">
      <div className="footer__inner">
        <img src="../../assets/logo-mark-cream.png" alt="" className="footer__logo" />
        <span className="footer__word">San&nbsp;Eduardo</span>
        <span className="footer__sep">·</span>
        <span className="footer__est mono">{t.footer.est}</span>
      </div>
    </footer>
  );
}

/* ── SHARED PRIMITIVES ────────────────────────────────────────────────── */
function Eyebrow({ icon, children, center }) {
  return (
    <div className={"eyebrow" + (center ? " eyebrow--center" : "")}>
      {icon && <Icon name={icon} size={14} />}<span>{children}</span>
    </div>
  );
}
function Callout({ tone, t, b }) {
  return (
    <div className={"callout callout--" + tone}>
      <div className="callout__bar" />
      <div className="callout__t">{t}</div>
      <div className="callout__b">{b}</div>
    </div>
  );
}
function PredictorCard({ rank, value, sub, icon, tone }) {
  return (
    <div className={"predictor predictor--" + tone}>
      <div className="predictor__icon"><Icon name={icon} size={20} /></div>
      <div className="predictor__rank mono">{rank}</div>
      <div className="predictor__value">{value}</div>
      <div className="predictor__sub">{sub}</div>
    </div>
  );
}

Object.assign(window, { Icon, Nav, Marquee, Hero, Farm, Finding, Model, Vision, Author, CtaBand, Footer, Eyebrow, Callout, PredictorCard });
