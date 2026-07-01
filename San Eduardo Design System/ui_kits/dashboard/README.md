# UI Kit — Data Dashboard

The cattle-intelligence panel — a rebrand of the project's original Streamlit app (`cattle-heifer-selection/app.py`) in the San Eduardo design system. Hero strip + pill tabs + hand-built charts + data tables. Bilingual (ES/EN toggle, persisted), tab state persisted.

## Run
Open `index.html`. Links `../../colors_and_type.css`; loads React 18 + Babel from CDN.

## Files
| File | Role |
|---|---|
| `index.html` | Shell + all dashboard CSS |
| `data.js` | Bilingual labels + chart/table data (`window.SE_DASH`) — numbers approximate the real project outputs |
| `charts.jsx` | Hand-built SVG/CSS charts (no chart lib): `LineChart`, `BarChart`, `HBars` |
| `components.jsx` | Metric cards, section headers, notes, panels, and the six tab panels |
| `app.jsx` | App shell: top nav, hero strip, pill tab bar, panel switcher |

## Tabs
1. **Tu Rodeo / Your Herd** — overview metrics + IHM line chart + records bar chart
2. **Auditoría / Rule Audit** — the 49% finding, agreement-by-category bars
3. **El Modelo / The Model** — SHAP importance + model-comparison bars
4. **Datos Faltantes / Missing Data** — data-quality table with status pills
5. **La Visión / The Vision** — 3-phase roadmap cards
6. **Modelo 2027** — verifiable cohort ranking table with score bars

## Notes
- Charts are pure SVG/CSS — restyle via the `CL` palette object in `charts.jsx` (mirrors the CSS tokens).
- Tab panels animate transform only (no `opacity:0`) to stay screenshot-safe.
- Brand / "Inicio" links return to `../landing/index.html`.
- High-fidelity recreation, not production code. The original lives in `cattle-heifer-selection/`.
