# Data Dictionary

A living document. Every cleaning, normalization, or interpretation decision is recorded here at the moment it's made.

## Source files

| File | Received | Used for |
|---|---|---|
| `Futuras_Madres.xlsx` | Apr 30, 2026 | Older IHM history, 2025 cohort labels, adult cow registry |
| `Paricion_2025.xlsx` | Apr 30, 2026 | 2025 birth log + mother cycle tracker |
| `Preseleccio_n_FM_2027.xlsx` | May 5, 2026 | Adjusted IHM history (205-day), 2027 cohort labels |
| `IATF_Rodeo_*.csv` (×4) | May 5, 2026 | DataMars exports of 2025 IATF sessions, with semen used per cow |
| `whatsapp_alarms.txt` | May 5, 2026 | WhatsApp alarm group export (abortions, sales, health flags) |

## Field-level decisions

### IDV (cow identifier)

The IDV is the cow's permanent ID like `BE099L322`. The source data spells it inconsistently (`Be099l322`, `BE099 L322`, etc.), and in some informal contexts (WhatsApp messages) only the visual short form (`L322`) is used.

- **Canonical form:** uppercase, all whitespace removed, non-IDV placeholders mapped to NaN.
- **Placeholders mapped to NaN:** `''`, `NAN`, `S/D`, `DESCONOCIDO`, `#N/D`, `#N/A`, `NONE`, `NULL`.
- **Short-form expansion:** in event parsing, a 4-character short form like `K386` is expanded to `BE099K386` for matching against the registry.

### Class labels — two evolving schemes

The farm uses two distinct schemes that evolved across years:

- **`verdes` (used for 2025 cohort):** `3 Verdes`, `2 Verdes` / `2 verdes`, `1 Verde`, `Venta`, plus older terms like `Pesada sin Genealogia`, `FM Venta`, `Invernada`, `Ver`.
- **`estrellas` (used for 2027 cohort):** `3 Estrellas`, `2 Estrellas`, `1 Estrella`, `Pesadas sin Genealogia`, `Venta`, `Venta Reproduccion` / `Venta reproduccion`.

Casing is inconsistent within each scheme. We normalize to `snake_case` prefixed with the scheme name (`verdes_3`, `estrellas_3`) so downstream code can tell them apart.

**Confirmed equivalent (May 2026 conversation with farm):** `verdes_N` ≡ `estrellas_N`. The farmer described the rename as an inadvertent inconsistency on his side. The `UNIFIED_TIER` mapping in `clean.py` is therefore validated — but the underlying *rule* changed even though the labels are equivalent, see below.

### IHM scale

The two IHM databases use different scales:

- **`Historial IHM` (old):** percent (0–100). Mean ≈ 45. Uses **raw** weaning weight.
- **`IHM Histórico` (new):** proportion (0–1). Mean ≈ 0.41. Uses **205-day adjusted** weaning weight (column suffix `(AJ)`).

**Decision:** all IHM normalized to **proportion (0–1)** downstream. When the same cow has IHM in both for the same year, the new (adjusted) value wins.

The new file's adjusted IHM is ~10% lower than the old file's unadjusted value. The farmer confirmed (May 2026) that all years in the new file (2024, 2025, 2026) are 205-day adjusted.

### IHM zero values vs. missing

Per farmer (May 2026), `s/d` and `#N/A` in IHM columns mean **identification errors**, not "no calf". They should be treated as missing. We therefore treat them as NaN, not as 0.0.

(Earlier we treated 0 as a sentinel for "no calf". This was an over-interpretation; the new instruction is to treat `s/d` as missing.)

### Pelaje (coat)

Canonical values: `negro`, `colorado`, `p_negro` (parted black), `p_colorado`, `mixto`. Unknown returns None.

### Tipo Padre (sire type)

Canonical values: `iatf`, `repaso`, `desconocido`.

For repaso (cleanup-bull) calves, the farmer confirmed **the specific bull is not known** — only that it was one of 2–3 bulls assigned to that rodeo. So we treat repaso as a single category, not a per-bull feature.

## Rule evolution (concept drift)

The documented rule from Ezequiel's slide:
- weight ≥ 190 kg
- mother known
- mother's IHM ≥ 40%
- sire IATF (for 3 verdes) or known (for 2 verdes)

Confirmed by the farmer in May 2026:
- **Weight threshold remains 190 kg** — the documented slide is correct
- **IHM input has switched from raw weaning weight to 205-day adjusted** — same 40% threshold but different denominator
- **`venta_reproduccion` category was introduced in 2027** for heifers passing IHM but whose mothers exceed 550 kg (frame control)
- **Implicit `madre CUT` bonus**: cows from the CUT (long-lived) rodeo get an upgrade; not in any documentation

The 2027 cohort has explicit binary flags for these criteria (`Hija IATF?`, `Abuelo Moderado?`, `Hija Cut`, `IHM Minimo`, `Peso + 160 vaq / + 180 Vac`).

## Cow registry

`build_cow_registry` produces 2,728 rows after reconciling all sources via the precedence ordering documented in `src/lineage.py`. Field coverage:

- sex: 100%
- anio_nacimiento: 71%
- pelaje: 94%
- madre_idv: 64%
- nombre_padre: 82%
- tipo_padre: 75%

## Lineage

- 1,733 cows have known mother IDV (64%)
- 1,610 of those mothers exist in the registry — so 93% of the time we can chain to grandmother
- 422 cows have known maternal grandmother (15%)
- 1,607 cows have known maternal grandsire (60%)

## IHM history

5,265 cow-year observations, 2022–2026. 685 cows have ≥2 real IHM observations. 343 cows have at least one adult IHM observation (using age ≥ 3 as the threshold, since first-year IHM is biased high for vaquillonas — confirmed by farmer May 2026).

## Events table

- 79 WhatsApp events: 17 abortions, 11 possible abortions, 15 heat events, 8 FM-flagged, 3 sales, 3 grave health
- 696 IATF events from 2025: 8 distinct semen sources used
- Total 775 events

## Rule reproduction

Verdes rule applied to 2025 cohort:
- **Match rate: 49%** (documented 190 kg threshold)
- `verdes_3`: 100% (90/90)
- `verdes_2`: 92% (79/86)
- `verdes_1`: 0% (the entire class is missing from the documented rule)
- `verdes_venta`: ~38%

This gap is the project's headline finding, the rule documents the *top* but not the *middle*.

## Reproductive event data (Phase 2)

Tatiana's uncle provided 26 additional CSV files in May 2026, exported from DataMars, covering the farm's annual reproductive cycle for two consecutive years.

### File families

The farm's breeding cycle runs:
- **September:** IATF (artificial insemination) sessions
- **November:** ecografía (early ultrasound, ~30-60 days post AI)
- **March:** tacto (palpation, ~6 months post-AI; the canonical pregnancy check)

| Family | Files | Total events | Coverage |
|---|---|---|---|
| Insemination | 5 | 736 | Sept-Oct 2024 |
| Ecografía | 10 | 1,587 | Nov-Dec 2024, Nov-Dec 2025 |
| Tacto | 11 | 1,772 | March 2025, March 2026 |

The 2025 IATF sessions (4 files we already had) plus these 5 new 2024 IATF files give us **two complete breeding cycles** (2024-25 and 2025-26).

### Key column: `Gestacion`

Both ecografía and tacto sessions record the gestation stage in the `Gestacion` column. Canonical values after normalization:

| Source value | Canonical | Meaning |
|---|---|---|
| `Cabeza` | `cabeza` | Conceived early in the cycle (best outcome) |
| `Cuerpo` | `cuerpo` | Conceived mid cycle |
| `Cola` | `cola` | Conceived late |
| `Vacía` / `Vacia` | `vacia` | Did not conceive |

When both ecografía and tacto exist for the same cow-year, **tacto wins**, it's later and more authoritative.

### Breeding year logic

Sessions in months Aug-Dec belong to that calendar year's cycle. Sessions in months Jan-Apr (i.e., the tacto session) belong to the PRIOR year's cycle.

Example: a cow inseminated September 2024, checked at ultrasound November 2024, and palpated March 2025, all three events are part of the **2024 breeding cycle**.

### Outcome distribution

Across all 1,782 cow-year outcomes:

| Outcome | Count | % |
|---|---|---|
| cabeza (early) | 1,192 | 67% |
| cuerpo | 215 | 12% |
| cola | 87 | 5% |
| vacia (empty) | 73 | 4% |
| unknown | 83 | 5% |
| (no record) | 132 | 7% |

Overall pregnancy rate: **~84%** across cycles.

### Coverage summary

- 1,034 unique cows have at least one reproductive cycle on record
- 748 cows have 2+ cycles (the canonical population for reproductive consistency analysis)

### Why this matters for the project

**IHM and pregnancy rate are weakly negatively correlated** (Pearson r ≈ −0.15, p=0.008, n=312). They measure two genuinely different productivity dimensions. This justifies a multi objective framing:

- **IHM target**: how much milk does the cow transfer to her calf?
- **Pregnancy rate target**: how reliably does she conceive each year?
- **Composite target**: IHM × pregnancy rate (rewards excellence on both)

Empirically, IHM is more predictable from selection-time features (Spearman ρ ≈ 0.32) than pregnancy rate (ρ ≈ 0.15). This may reflect that reproductive success is partly stochastic (timing, bull effects, weather) while IHM is more strongly determined by genetics and early-life conditions.

### Known limitations

**Mother's reproductive features are unavailable for our trainable cohort.** The reproductive event data starts in September 2024. Our trainable heifers were born 2017-2022, so their selection cutoff is at most 2024. Mothers therefore have no pre selection reproductive history. We keep the `madre_pregnancy_rate_pre` column for future-data extension but it contains no information for current modeling.

This is a documented limitation, not a bug. As the farm's reproductive data extends backward (via DataMars historical export, if available), this feature family will become populated.

## Outstanding questions

1. ~~Are verdes and estrellas equivalent?~~ Yes (farmer confirmed)
2. ~~Was 205-day adjustment retroactive?~~ Yes for the new file (farmer confirmed)
3. ~~What does s/d mean?~~ Identification errors, treat as missing (farmer confirmed)
4. Where are 2024 and 2026 cohort labels? — They don't exist; preselection only systematized in 2025.
5. Records of culled cows? — Not formally recorded. We have only the ad-hoc WhatsApp log.
6. Prior-year birth logs? — Not centralized; partially retrievable via DataMars.
