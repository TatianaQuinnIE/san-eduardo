# Source Inventory

Reference doc for every Excel sheet, CSV, and text file we ingest, where it comes from, and which fields are authoritative when sources disagree.

## Files received from the farm

| File | Sheets/format used | Notes |
|---|---|---|
| `Futuras_Madres.xlsx` | `Historial IHM`, `FM p-rep.`, `Vientres`, `Terneros de Sesiones` | Original IHM history + 2025 cohort |
| `Futuras_Madres_a_xr5000.xlsx` | (none) | Mostly redundant with above. We do not load this file. |
| `Paricion_2025.xlsx` | `Nacimientos`, `Base de Madres` | 2025 field birth log + cycle tracker |
| `Preseleccio_n_FM_2027.xlsx` | `Terneras`, `IHM Histórico`, `Peso Terneros` | 2027 cohort + updated/adjusted IHM history |
| `IATF_Rodeo_*.csv` (×4) | semicolon-separated CSV | DataMars exports of 2025 IATF sessions, 696 events total |
| `whatsapp_alarms.txt` | text export | WhatsApp group export, parsed in `events.py` |

## Sheet-by-sheet detail

### `Historial IHM` (older IHM database)
- 822 rows × 22 cols, one row per cow
- IHM as PERCENT (0–100), uses raw (non-adjusted) weaning weight
- Columns: `IHM 2022`, `IHM 2023`, `IHM 2024`, `IHM 2025`, gestation history
- Used as fallback when a cow isn't in the newer source

### `IHM Histórico` (newer database — preferred)
- 1208 rows × 18 cols
- IHM as PROPORTION (0–1), 205-day adjusted (column suffix `(AJ)`)
- `IHM 2024 (AJ)`, `IHM 2025 (AJ)`, `IHM 2026 (AJ)`
- Has raw inputs: `Peso Madre 2024/25/26`, `Peso Ternero 2024/25/26 (205 días)`
- Missing values stored as the literal string `s/d` — interpreted as identification errors per farmer

### `FM p-rep.` (2025 cohort)
- 364 rows; ~346 are female (the heifer cohort)
- Recorded label in column `Presel 2025`: `3 Verdes`, `2 Verdes` / `2 verdes`, `1 Verde`, `Venta`
- Mother's IHM already joined: `IHM Madre 2022..2025`

### `Terneras` (2027 cohort)
- 405 rows, all female
- Recorded label in column `Categoria`: `3 Estrellas`, `2 Estrellas`, `1 Estrella`, `Pesadas sin Genealogia`, `Venta`, `Venta Reproduccion`
- Engineered farm flags: `Peso + 160 vaq / + 180 Vac`, `Hija IATF?`, `Abuelo Moderado?`, `Hija Cut`, `IHM Minimo`
- Has `Peso 205 días` (205-day adjusted weight) and `Abuelo Materno`

### `Vientres` (adult cow database)
- 881 rows, female only
- Independent gestation history: `Gest 20/21` ... `Gest 23/24`
- Used as fallback for cows missing from IHM history

### `Terneros de Sesiones` (calves through chute)
- 726 rows, weighing-session records
- Column has mojibake from encoding (`Rodeo GestacIÃ³n`) — accepted as-is

### `Nacimientos` (2025 field birth log)
- 800 rows recorded by the rider on motorbike
- 793 of 800 have mother IDV
- `Notas` column has rich qualitative info (assisted birth, mortality, twins, mismothering)
- Header `Fecha` has trailing space — stripped in loader

### `Base de Madres` (2025 cycle tracker)
- 792 rows
- `Pario??` (boolean has-calved-this-cycle), `Clasificacion`, `Gestacion previa`

### `Peso Terneros` (2025 calf weights)
- 757 rows, both sexes
- Has both `Peso Destete` and `Peso 205 días` — useful for validating the adjustment formula

### IATF session CSVs
- 4 files, one per rodeo: `1ra y 2da`, `Cabeza Mixto`, `Cabeza Negro`, `FM`
- 696 IATF events total
- Semicolon-separated; mojibake in header row from DataMars export
- Key columns: `IDV`, `Fecha` (YYYY-MM-DD), `Peso`, `Semen utilizado`
- 8 distinct semen sources: Felix AN (201), Dinamitado (159), Charlie AN (94), Maestro AC (67), El Macho AC (66), Coronel AN (66), Agropiro AC (35), Dinamitado AC (8)

### WhatsApp alarms log
- Single text file, exported from the farm's "San Eduardo alarmas" group
- Spans Jan 2024 – May 2026
- 79 distinct events parsed:
  - 17 aborto, 11 posible aborto, 15 alzada, 8 fm_flagged, 3 descarte, 3 salud_grave, 1 cesárea
- Parser handles both full IDV (`BE099L322`) and short visual (`L322`) formats

## Authoritative fields by topic

When the same cow appears in multiple sources with different values, here's which source we trust:

| Field | First choice | Fallback |
|---|---|---|
| Birth date / year | `Terneras` | `Nacimientos`, `Vientres` |
| Birth weight | `Terneras`, `Nacimientos` | `Terneros de Sesiones` |
| Pelaje | `Terneras` | `IHM Histórico`, `Vientres` |
| Mother IDV | `Terneras`, `Nacimientos` | `IHM Histórico`, `Vientres` |
| Sire name | `Terneras` | `IHM Histórico` |
| IHM value | `IHM Histórico` (adjusted) | `Historial IHM` (raw, divide by 100) |
| Recorded label | `Terneras.Categoria` (2027) / `FM p-rep.Presel 2025` (2025) | — |
| Semen used | IATF session CSVs | — |
| Health/abortion events | WhatsApp log | — |

Conflict-resolution code: `src/lineage.py::build_cow_registry`.

## Files NOT loaded

`Futuras_Madres_a_xr5000.xlsx` is in `data/raw/` for completeness but not loaded — its sheets either duplicate `Futuras_Madres.xlsx` or contain strict subsets we already cover.
