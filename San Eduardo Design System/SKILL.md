---
name: san-eduardo-design
description: Use this skill to generate well-branded interfaces and assets for Estancia San Eduardo (a pampa beef-cattle farm + its replacement-heifer ML project), either for production or throwaway prototypes/mocks/decks. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping in the "terracotta intelligence" brand.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

## Quick orientation
- **Tokens:** `colors_and_type.css` — link it and use the CSS variables. Don't hardcode hexes.
- **The look in one line:** bright, punchy, warm — heavy grotesque (Hanken Grotesk 800/900) display with a colored bold-italic accent word, upright bold-sans numbers, terracotta + clover-green + bright wheat-gold on warm bone, espresso ink, and a "herd-telemetry / soil-computing" data texture (Space Mono micro-tags, sensor dots, dotted-leader readout panels).
- **Assets:** `assets/` — recolorable cattle-brand logo (`logo-mark-{terracotta,forest,cream,espresso}.png`), favicon, real farm photography (`herd-running.jpg`, `herd-portrait.jpg`, `hero.jpg`, `farm_calves*.jpg`), author headshot.
- **Patterns to copy:** see `preview/` cards and the two UI kits (`ui_kits/landing`, `ui_kits/dashboard`) and `slides/` for ready-made component and layout patterns.
- **Bilingual:** content ships ES (Spanish-first) + EN via a toggle; see the `i18n.js` / `data.js` dictionaries for the pattern and voice.

## Rules of thumb
- Headlines: Hanken Grotesk 800, tight tracking, one italic accent word in clay/gold/green.
- Numbers/stats: big, upright, bold sans — never italic serif.
- Cards: cream surface, hairline border, soft warm shadow, 4px colored left-border to encode meaning; dark forest-green telemetry panels with gold figures + dotted leaders.
- Accent = bright gold for primary CTAs; clay for solid buttons.
- No emoji. Lucide-style 2px stroke icons. No gradients on flat content; reserve dark scrims + grain for hero/CTA bands.
- Don't start large content wrappers from `opacity:0` in entrance animations (transform-only) — it breaks screenshotting and risks a flash.
