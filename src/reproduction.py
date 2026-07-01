"""
Reproductive event extraction.

The farm runs an annual breeding cycle:
  - September:  IATF (artificial insemination) sessions
  - November:   Ecografía (early ultrasound, ~30-60 days post-AI)
  - March:      Tacto (palpation, ~6 months post-AI, the canonical pregnancy check)

Each cycle produces three related per-cow records. This module reads all
three file families from data/raw/ and combines them into:

  - reproduction_events: long-form, one row per (cow, session, event_type)
  - reproduction_outcomes: wide, one row per (cow, breeding_year) with the
    cycle outcome (cabeza/cuerpo/cola/vacia) and timing

Why this matters:
  The IHM target measures milk transfer to the calf. But a heifer who
  consistently fails to conceive is not a productive cow regardless of
  her IHM. Reproductive consistency is a SECOND outcome dimension.

  We use this in two ways:
    1. As a leakage-safe selection-time feature for daughter cohorts:
       "mother's gestation timing in years before daughter's selection".
    2. As a secondary outcome for cows in the supervised dataset, used
       to build a composite productivity score.
"""

import re
import warnings
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from src.clean import normalize_idv_column

# ---------------------------------------------------------------------------
# File pattern detection
# ---------------------------------------------------------------------------

# Filenames look like:
#   Inseminacion_Rodeo_FM__13_set__2024_.csv
#   Ecografia_rodeo_mixto__28_nov__2025_.csv
#   Tacto_FM_25_26__16_marzo_2026_.csv
#
# We classify by prefix and parse the date from the filename. The date in
# the filename is the SESSION date (when the chute work happened).

_SPANISH_MONTHS = {
    'ene': 1, 'enero': 1,
    'feb': 2, 'febrero': 2,
    'mar': 3, 'marzo': 3,
    'abr': 4, 'abril': 4,
    'may': 5, 'mayo': 5,
    'jun': 6, 'junio': 6,
    'jul': 7, 'julio': 7,
    'ago': 8, 'agosto': 8,
    'sep': 9, 'set': 9, 'septiembre': 9, 'setiembre': 9,
    'oct': 10, 'octubre': 10,
    'nov': 11, 'noviembre': 11,
    'dic': 12, 'diciembre': 12,
}


def _parse_session_date(fname: str):
    """Pull a session date out of the filename. Returns pd.Timestamp or NaT."""
    m = re.search(r'__?(\d{1,2})_(?:de_)?([a-záéíóú]+)[._]?_(\d{4})', fname.lower())
    if not m:
        return pd.NaT
    day, month_word, year = m.group(1), m.group(2), m.group(3)
    month = _SPANISH_MONTHS.get(month_word[:3])
    if month is None:
        return pd.NaT
    try:
        return pd.Timestamp(year=int(year), month=month, day=int(day))
    except (ValueError, TypeError):
        return pd.NaT


def _classify_session_file(fname: str) -> str:
    """Return 'insemination', 'ecografia', 'tacto', or None."""
    f = fname.lower()
    if f.startswith('inseminacion') or f.startswith('inceminacion'):
        return 'insemination'
    if f.startswith('ecografia') or f.startswith('ecografi_a'):
        return 'ecografia'
    if f.startswith('tacto'):
        return 'tacto'
    return None


# ---------------------------------------------------------------------------
# Row-level normalization
# ---------------------------------------------------------------------------

def _normalize_gestacion_value(v) -> str:
    """Map the gestation-stage column to canonical labels.

    Source values include: Cabeza, Cuerpo, Cola, Vacía / Vacia, NaN.
    Sometimes appear as '3 (2 verd)' style — these are the Clasificación
    column, NOT the Gestacion column. We only call this on the right column.
    """
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).strip().lower()
    s = s.replace('á', 'a').replace('í', 'i')
    if s in ('cabeza',): return 'cabeza'
    if s in ('cuerpo',): return 'cuerpo'
    if s in ('cola',):   return 'cola'
    if s in ('vacia', 'vacía'): return 'vacia'
    return None


# ---------------------------------------------------------------------------
# Loaders for the three session families
# ---------------------------------------------------------------------------

def load_session_files(raw_dir, kind: str) -> pd.DataFrame:
    """Load all session files of a given kind ('insemination', 'ecografia',
    'tacto') and concatenate.

    Returns a DataFrame with columns:
        idv               canonical IDV
        session_date      from filename
        session_kind      'insemination' / 'ecografia' / 'tacto'
        session_file      filename of origin
        peso              cow weight at session (if available)
        gestacion         normalized gestation stage (cabeza/cuerpo/cola/vacia)
                          None for insemination sessions
        semen_utilizado   bull/semen name (insemination only)
        rodeo             rodeo when recorded
    """
    raw_dir = Path(raw_dir)
    rows = []
    for path in sorted(raw_dir.glob('*.csv')):
        if _classify_session_file(path.name) != kind:
            continue
        try:
            df = pd.read_csv(path, sep=';', encoding='utf-8')
        except Exception as e:
            warnings.warn(f"Failed to read {path.name}: {e}")
            continue
        session_date = _parse_session_date(path.name)
        out = pd.DataFrame()
        out['idv'] = (df['IDV'].map(lambda v: v if pd.isna(v) else str(v))
                      .pipe(normalize_idv_column) if 'IDV' in df.columns else None)
        out['session_date'] = session_date
        out['session_kind'] = kind
        out['session_file'] = path.name
        out['peso'] = (pd.to_numeric(df['Peso'], errors='coerce')
                       if 'Peso' in df.columns else np.nan)
        if kind in ('ecografia', 'tacto') and 'Gestacion' in df.columns:
            out['gestacion'] = df['Gestacion'].map(_normalize_gestacion_value)
        else:
            out['gestacion'] = None
        out['semen_utilizado'] = (df['Semen utilizado']
                                   if kind == 'insemination' and 'Semen utilizado' in df.columns
                                   else None)
        out['rodeo'] = (df['Rodeo Gestacion']
                        if 'Rodeo Gestacion' in df.columns else None)
        out = out[out['idv'].notna()]
        rows.append(out)
    if not rows:
        return pd.DataFrame(columns=['idv', 'session_date', 'session_kind',
                                      'session_file', 'peso', 'gestacion',
                                      'semen_utilizado', 'rodeo'])
    return pd.concat(rows, ignore_index=True)


def build_reproduction_events(raw_dir) -> pd.DataFrame:
    """Combine all three session families into one long-form events table."""
    parts = []
    for kind in ('insemination', 'ecografia', 'tacto'):
        parts.append(load_session_files(raw_dir, kind))
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Per-cow-per-cycle outcome aggregation
# ---------------------------------------------------------------------------

def _breeding_year(d: pd.Timestamp) -> int:
    """Map a session date to its breeding year.

    The cycle runs Sept (insemination) → Nov (ecografía) → Mar (tacto).
    Sessions in Sept-Dec belong to that calendar year's cycle. Sessions in
    Jan-Apr (i.e., the tacto) belong to the PRIOR year's cycle.
    Example: Sept 2024 IATF + Nov 2024 ecografía + March 2025 tacto are
    all the "2024 breeding cycle".
    """
    if pd.isna(d):
        return None
    return int(d.year if d.month >= 8 else d.year - 1)


def build_reproduction_outcomes(events: pd.DataFrame) -> pd.DataFrame:
    """Roll session events up to one row per (cow, breeding_year).

    Returns columns:
        idv                     cow IDV
        breeding_year           year of the cycle (e.g. 2024 for Sept24-Mar25)
        was_inseminated         bool — has insemination record
        had_ecografia           bool — has ecografía record
        had_tacto               bool — has tacto record
        ecografia_gestacion     stage at ecografía if available
        tacto_gestacion         stage at tacto (the canonical outcome)
        gestation_outcome       FINAL canonical outcome derived from tacto:
                                  cabeza / cuerpo / cola / vacia / unknown
        is_pregnant             bool — successful gestation (not vacía)
        early_conception        bool — gestated cabeza (early in cycle)
        semen_utilizado         bull/semen used at insemination
    """
    if len(events) == 0:
        return pd.DataFrame()

    df = events.copy()
    df['breeding_year'] = df['session_date'].map(_breeding_year)
    df = df[df['breeding_year'].notna()].copy()

    # Pivot: for each (idv, year), find the latest session of each kind
    aggregated = []
    for (idv, year), grp in df.groupby(['idv', 'breeding_year']):
        ins = grp[grp['session_kind'] == 'insemination']
        eco = grp[grp['session_kind'] == 'ecografia']
        tac = grp[grp['session_kind'] == 'tacto']
        # Use the latest session of each kind if multiple
        ins = ins.sort_values('session_date').tail(1)
        eco = eco.sort_values('session_date').tail(1)
        tac = tac.sort_values('session_date').tail(1)

        eco_gestacion = eco['gestacion'].iloc[0] if len(eco) else None
        tac_gestacion = tac['gestacion'].iloc[0] if len(tac) else None
        # Final outcome: tacto wins; ecografía is a fallback
        final = tac_gestacion if tac_gestacion is not None else eco_gestacion
        if final is None:
            final = 'unknown'

        aggregated.append({
            'idv':                idv,
            'breeding_year':      int(year),
            'was_inseminated':    len(ins) > 0,
            'had_ecografia':      len(eco) > 0,
            'had_tacto':          len(tac) > 0,
            'ecografia_gestacion':eco_gestacion,
            'tacto_gestacion':    tac_gestacion,
            'gestation_outcome':  final,
            'is_pregnant':        final in ('cabeza', 'cuerpo', 'cola'),
            'early_conception':   final == 'cabeza',
            'semen_utilizado':    ins['semen_utilizado'].iloc[0] if len(ins) else None,
        })
    return pd.DataFrame(aggregated)


def cow_reproductive_summary(outcomes: pd.DataFrame,
                              registry: pd.DataFrame) -> pd.DataFrame:
    """For each cow, compute her overall reproductive history:
        n_cycles_observed
        n_pregnancies
        pregnancy_rate
        early_conception_rate
        n_vacia (empty cycles)
    """
    if len(outcomes) == 0:
        return pd.DataFrame(columns=['idv', 'n_cycles_observed', 'n_pregnancies',
                                      'pregnancy_rate', 'early_conception_rate',
                                      'n_vacia'])
    g = outcomes.groupby('idv').agg(
        n_cycles_observed=('breeding_year', 'count'),
        n_pregnancies=('is_pregnant', 'sum'),
        n_early=('early_conception', 'sum'),
        n_vacia=('gestation_outcome', lambda s: (s == 'vacia').sum()),
    ).reset_index()
    g['pregnancy_rate'] = g['n_pregnancies'] / g['n_cycles_observed']
    g['early_conception_rate'] = g['n_early'] / g['n_cycles_observed']
    g = g.drop(columns='n_early')
    return g


# ---------------------------------------------------------------------------
# Leakage-safe mother reproductive features
# ---------------------------------------------------------------------------

def mother_reproductive_at_selection(outcomes: pd.DataFrame,
                                       registry: pd.DataFrame,
                                       selection_year_offset: int = 2) -> pd.DataFrame:
    """For each heifer with a known mother, summarize the mother's
    reproductive history STRICTLY BEFORE the heifer's selection year.

    A heifer born in 2020 has selection year 2022. Mother's breeding cycles
    in 2020 and 2021 are leakage-safe.
    """
    cohort = registry[registry['madre_idv'].notna() &
                       registry['anio_nacimiento'].notna()].copy()
    cohort['selection_year'] = cohort['anio_nacimiento'] + selection_year_offset

    rows = []
    for _, row in cohort.iterrows():
        m = outcomes[(outcomes['idv'] == row['madre_idv']) &
                     (outcomes['breeding_year'] < row['selection_year'])]
        if len(m) == 0:
            rows.append({
                'idv': row['idv'],
                'madre_idv': row['madre_idv'],
                'madre_n_cycles_pre': 0,
                'madre_pregnancy_rate_pre': np.nan,
                'madre_early_conception_rate_pre': np.nan,
            })
        else:
            rows.append({
                'idv': row['idv'],
                'madre_idv': row['madre_idv'],
                'madre_n_cycles_pre': len(m),
                'madre_pregnancy_rate_pre': m['is_pregnant'].mean(),
                'madre_early_conception_rate_pre': m['early_conception'].mean(),
            })
    return pd.DataFrame(rows)
