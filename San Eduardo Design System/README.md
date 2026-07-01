# San Eduardo — Design System

A complete brand and interface design system for **Estancia San Eduardo**, a family beef-cattle ranch in **Bragado, Buenos Aires, Argentina**, and the machine-learning portfolio project built around it: *Selección de Vaquillonas* (Replacement-Heifer Selection).

This system exists to present the project beautifully — as a LinkedIn-grade showcase of both the farm and the author's data-science capabilities. It fuses a warm, earthy, pampa-agricultural palette with editorial display typography and a "herd-telemetry" data aesthetic ("terracotta intelligence"): agriculture read as a precise, data-driven signal.

> **The design direction** was adapted from a Lovable landing-page concept the user shared ("The Clay & Clover" / Cloverdale — an organic-dairy site themed around *terracotta soil computing*). We carried over its energy — red-earth + clover palette, big editorial type, telemetry/sensor framing, marquees, oversized stat figures — and reapplied it to San Eduardo's real content, photography, and project findings.

---

## What the project is about

Every autumn the farm chooses among ~300–400 heifers: which stay as future mothers (defining the herd's genetics for 5–10 years) and which go to fattening. Today that's a hand-coded rule plus a trained eye. The project asks: **can a model learn to pick the next mothers better than the spreadsheet?**

Key findings that drive the content of every surface:
- **2,728** unique cows reconciled from 9 raw sources; **5,265** IHM observations (2022–2026); **337** cows in the supervised population.
- **49%** rule consistency — the farm matches its own documented rule only about half the time. ~28% of decisions are "producer exceptions" (tacit knowledge). *This gap is the headline finding.*
- Model is honest: **35%** precision@top-30% on a temporal holdout vs. **30%** at random — real but weak signal. The bottleneck is missing data (mothers' IHM only exists from 2022).
- **Predictor #1:** the mother's own IHM history ("good mothers make good daughters").
- A verifiable **2027 cohort** (405 heifers) is ranked for future validation.

IHM = *Índice de Habilidad Materna* (Maternal Ability Index) = calf weight at 205 days ÷ mother's weight.

## Products / surfaces in this system

1. **Landing page** (`ui_kits/landing/`) — the marketing + project showcase. Features the farm proudly, presents the main results, and showcases the author's skills. ES/EN toggle.
2. **Data dashboard** (`ui_kits/dashboard/`) — the cattle-intelligence panel: hero strip, pill tabs, hand-built charts, data tables. A redesign of the original Streamlit app in the new brand. ES/EN toggle.
3. **Slide deck** (`slides/`) — branded presentation templates (cover, section divider, big-stat, two-column-with-chart, quote, roadmap, closing).

## Sources (for whoever maintains this — access may be needed)

- **Codebase:** `cattle-heifer-selection/` — a Streamlit app (`app.py`) + Python ML pipeline (`src/`, `scripts/`). The original design tokens (forest green / terracotta / amber, Libre Baskerville + Source Sans 3) were extracted from `app.py`; this system evolves them.
- **Lovable design reference (public):** https://moo-land-magic.lovable.app — the "Clay & Clover" aesthetic the user wanted. (A second, token-gated `id-preview--356c5e04…lovable.app` URL was inaccessible.)
- **Uploaded assets:** farm photography (`uploads/IMG_2458.jpg`, `IMG_2462 2.jpg`) and the "Silvia R. Quesada" cattle-brand logo (`uploads/WhatsApp Image 2026-05-28…jpeg`).
- **Author:** Tatiana Quinn — Computer Science & AI, IE University, Madrid · linkedin.com/in/tatianaquinn

---

## CONTENT FUNDAMENTALS

**Voice — honest, grounded, editorial.** The project's credibility comes from *not* overselling. Copy states limitations as plainly as wins ("Señal real, honestamente débil" / "Real signal, honestly weak"). It respects the reader's intelligence and the farm's experience.

- **Bilingual, Spanish-first.** Spanish is the native register (the farm is Argentine); English is a peer translation, never a watered-down version. Both ship together via a toggle. Spanish uses Argentine vocabulary: *vaquillonas, rodeo, invernada, campo, pampa, IATF, IHM*.
- **Person:** mostly impersonal/collective ("Procesamos…", "Entrenamos el modelo…", "We trained…"). The author speaks in first person only in the bio. Addresses the farm as "el campo."
- **Casing:** Sentence case for body and headlines. Mono eyebrows and tags are UPPERCASE with wide tracking (`EL HALLAZGO PRINCIPAL`, `SENSOR: ACTIVO`). Display headlines are sentence case for an editorial, literary feel.
- **Numbers carry the story.** Big bold-sans figures are the rhetorical centerpiece (49%, 2.728, 35%). Spanish uses `.` as thousands separator and `,` as decimal (2.728, 0,42); English uses `,` and `.` (2,728, 0.42).
- **Tone words:** precise, earthy, confident, a little poetic. Telemetry framing ("Sensor: Activo", "Panel de telemetría", "REC · WEST-3 PADDOCK", "LIVE") gives a tech-meets-soil texture lifted from the Lovable reference.
- **No emoji.** Not part of the brand. Use the icon set or mono symbols (✦, ●, ★) instead.
- **Examples of headline voice:**
  - *"El rodeo, leído por los datos."* / "The herd, read by data."
  - *"El campo no aplica su propia regla la mitad de las veces. No es un error: es experiencia que todavía no fue escrita."*
  - *"Las buenas madres dan buenas hijas."* / "Good mothers make good daughters."

---

## VISUAL FOUNDATIONS

**Overall vibe:** warm/earthy/agricultural × premium editorial × data-credible. Think a livestock magazine spread that's also a sensor dashboard.

### Color
Dual-anchor palette, **bright and punchy** (matched to the Lovable reference). **Clay / terracotta** (`#C0532E`) is the primary signature — it ties to the red-brown cattle and fired earth. **Pasture/clover green** (`#1B4332`→`#2D6A4F`→`#95D5B2`) is the secondary, drawn from the pampa. **Bright wheat gold** (`#F2C53D`) is the single accent (CTAs, hero figures, accent words). Everything sits on **warm off-white bone/cream** surfaces (`#F2EEE3`, `#FBF8F1`) with **warm espresso ink** (`#2C1A0E`) — never pure black or cool gray. Status: green=ok, gold=warn, brick=alert. A rare cool "pampa sky" blue (`#5B7E94`) exists for special accents. Full tokens in `colors_and_type.css`.

### Type
Matches the Lovable "Clay & Clover" brand: **one punchy grotesque does almost everything**, in different weights (see substitution note below).
- **Display — Hanken Grotesk, 800/900 (Black):** heavy grotesque, set BIG (48–168px) with tight tracking (-0.035em). A colored **bold-italic accent word** in each headline is the signature move (e.g. *leído*, *Circuits*).
- **Numbers — Hanken Grotesk 800, upright:** every hero figure/stat is bold upright sans — not italic, not serif.
- **Body/UI — Hanken Grotesk 300–700:** same family, lighter weights.
- **Eyebrows/labels — Hanken Grotesk 800 uppercase**, wide tracking (0.14em).
- **Telemetry — Space Mono:** reserved for genuine data micro-tags (SENSOR: ACTIVO, batch codes, dashboard table headers, data-row keys) — the "soil-computing" texture.

### Backgrounds & imagery
Full-bleed **farm photography** (real herd photos: warm afternoon light, red-brown Angus-cross cattle, green pampa, blue sky) under a dark forest-green gradient scrim for hero areas. Body sections are flat bone/cream — **no gradients on content**, no busy patterns. A subtle **fractal-noise grain** overlay (opacity ~0.07, `mix-blend: overlay`) sits on dark hero/CTA bands for an organic, printed texture. Imagery color vibe: warm, sunlit, natural — never desaturated or cool.

### Layout
Centered max-width ~1180–1200px content columns with generous padding (`clamp(64px,9vw,120px)` vertical on landing). Sticky translucent nav (blurs to cream on scroll). Editorial rhythm: alternate full-bleed photo sections, centered big-number moments, two-column text+media, and dark telemetry panels. Marquee ticker breaks sections. 8pt spacing base.

### Cards, borders, radii
Cards = cream surface, 1px `--line` border, soft warm shadow, often a **4px colored left-border** to encode meaning (clay/green/gold). Radii: 8 / 14 / 22 / 32 / pill(999). Phase/roadmap cards use a colored **top** border instead. Telemetry panels invert to dark forest-green with gold italic figures and dotted leader lines.

### Shadows
Warm-tinted, espresso-based (never gray): `--sh-1`…`--sh-4` from a 1px hairline to a 28px lift. Hover states lift cards (`translateY(-4/-5px)`) and deepen the shadow; some add a gold focus ring (`0 0 0 3px rgba(212,160,23,0.3)`).

### Motion
Calm and editorial. Eases: `cubic-bezier(0.22,0.61,0.36,1)` standard, `(0.16,1,0.3,1)` for entrances. Hero stat badges fade-up staggered. Marquee scrolls linearly (38s). Sensor dots pulse. **Important:** entrance animations must not start from `opacity:0` on large content wrappers (it breaks DOM-clone screenshotting and risks a flash) — animate transform only, or fade small elements.

### Hover / press
Hover: lift + shadow + (sometimes) gold ring; links shift toward `--clay-700` / grow their gap. Press: `scale(0.97)`. Gold button lifts and brightens.

### Transparency / blur
Used for the sticky nav (`rgba(cream,0.86)` + `blur(16px)`), hero glass stat badges (`rgba(cream,0.07)` + `blur(14px)` + gold hairline), and photo tags over imagery (`rgba(forest,0.78)` + blur). Not used on flat content.

---

## ICONOGRAPHY

- **Primary set:** a small **Lucide-style, 2px-stroke, round-cap** line-icon set, defined inline as SVG paths (`SE_ICONS` in `ui_kits/landing/components.jsx`, `ICO` in the dashboard). Stroke icons only — no filled glyphs except stars (★) for selection tiers. Icons inherit `currentColor`; default clay or green.
  - *Why inline, not a CDN font:* keeps the kits self-contained and offline-safe. If you need the full library, **Lucide** (lucide.dev) is the closest match — same geometry and stroke weight — link it from CDN and document it.
- **Brand mark:** the **cattle-brand logo** (`assets/logo-mark-*.png`) — a hand-drawn livestock brand glyph. Recolorable (terracotta / forest / cream variants generated), text-free (the "Silvia R. Quesada" wordmark was removed per request). Use at small sizes in nav/footer; don't oversaturate.
- **Favicon:** `assets/favicon.png` — a small green cow-face icon (from the original app).
- **Unicode used as iconography:** `✦` (marquee separators), `●` / `•` (list bullets, sensor dots), `★★★` (selection tiers), `→` (CTAs). No emoji anywhere.

---

## Index — what's in this folder

| Path | What |
|---|---|
| `README.md` | This file — context, content & visual foundations, iconography, index |
| `SKILL.md` | Agent-Skill manifest (for Claude Code use) |
| `colors_and_type.css` | **Core tokens** — colors, type families, scale, radii, spacing, shadows, motion + semantic type classes |
| `assets/` | Logo mark variants, favicon, farm photography, author headshot |
| `preview/` | 22 design-system cards (type, color, spacing, components, brand) shown in the Design System tab |
| `ui_kits/landing/` | Landing page UI kit — `index.html`, `i18n.js`, `components.jsx`, `app.jsx`, `README.md` |
| `ui_kits/dashboard/` | Data dashboard UI kit — `index.html`, `data.js`, `charts.jsx`, `components.jsx`, `app.jsx`, `README.md` |
| `slides/` | Branded slide deck — `index.html` + `deck-stage.js` |

### Fonts — substitution flagged
No original brand font files were provided. This system uses **Google Fonts**: Hanken Grotesk (display 800/900 + body) and Space Mono (telemetry micro-tags), loaded via `@import` in `colors_and_type.css`. This matches the Lovable reference's bold-grotesque brand feel. The original Streamlit app used Libre Baskerville + Source Sans 3 (kept only as deep fallbacks). **If you have preferred/licensed brand fonts, send them and I'll swap them in.**
