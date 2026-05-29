# UI Kit — Landing Page

The San Eduardo marketing + project showcase. A single-scroll editorial landing that features the farm, presents the ML project's main findings, and showcases the author's capabilities. Bilingual (ES/EN toggle, persisted to `localStorage`).

## Run
Open `index.html`. It links `../../colors_and_type.css` and loads React 18 + Babel from CDN.

## Files
| File | Role |
|---|---|
| `index.html` | Shell + all section CSS (the full visual system lives here) |
| `i18n.js` | Bilingual content dictionary (`window.SE_I18N`) — ES & EN, every string keyed |
| `components.jsx` | All sections + primitives + inline Lucide-style icon set; exported to `window` |
| `app.jsx` | App shell, language state, smooth-scroll + dashboard nav |

## Sections (in order)
`Nav` (sticky, translucent→cream on scroll, ES/EN toggle, "Sensor: Activo") → `Hero` (full-bleed herd photo, big bold-grotesque headline w/ gold italic accent, glass stat badges) → `Marquee` (terracotta ticker) → `Farm` (text + photo, mono REC tag) → `Finding` (giant 49% figure + three callouts + pullquote) → `Model` (predictor cards + dark telemetry panel) → `Vision` (3 phase cards) → `Author` (headshot + skills) → `CtaBand` (dark, gold CTA) → `Footer`.

## Notes
- Icons are inline SVG (`SE_ICONS` map) — Lucide-style, 2px stroke. Swap in the real Lucide CDN if you need more.
- Entrance animations animate transform only (never `opacity:0` on big wrappers) so DOM-clone screenshots don't capture a blank frame.
- "Ver Dashboard" / hero secondary link to `../dashboard/index.html`.
- This is a high-fidelity recreation/showcase, not production code — interactions are cosmetic.
