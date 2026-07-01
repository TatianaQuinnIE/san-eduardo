"""
Feature engineering and supervised dataset construction.

The hardest constraint here is leakage: every feature must be derivable
from information knowable at the moment of the heifer's selection. The
supervised target is mean future IHM, computed from years AFTER selection.

Per-cow selection year: defined as `birth_year + 2`, since heifers are
typically classified for retention in their second year of life
(based on the farm's process).

The IHM in the data covers years 2022-2026. We can only build training
examples for cows whose:
  - selection year is within range, AND
  - they have at least 1 future IHM observation past their selection year.

Per the farmer (May 2026 conversation): first-year IHM is biased high
because vaquillonas are still growing. We exclude first-year IHM from the
outcome, treating it as part of the "vaquillona" regime not the "vaca adulta"
regime. Specifically, we use IHM from age 4 onwards (selection_year + 2 onwards)
when computing the mean future IHM target.
"""

from typing import Optional
import pandas as pd
import numpy as np

from src.clean import normalize_idv_column, to_proportion


# ---------------------------------------------------------------------------
# IHM history
# ---------------------------------------------------------------------------

def build_ihm_history(sources: dict) -> pd.DataFrame:
    """Long-form IHM observations: one row per (cow, year).

    Columns:
        idv               canonical cow IDV
        year              year the IHM applies to
        ihm               IHM as proportion (0-1), NaN if missing,
                          0.0 sentinel if cow had no calf that year
        peso_madre        mother weight that year (kg) if available
        peso_ternero_205  calf 205-day adjusted weight if available
        source            'historico_new' (preferred) or 'historial_old'
    """
    rows = []

    # Newer 205-day-adjusted IHM (preferred)
    new = sources['ihm_historico_new'].copy()
    new['idv'] = normalize_idv_column(new['IDV'])
    new = new[new['idv'].notna()]
    for year in [2024, 2025, 2026]:
        ihm_col = f'IHM {year} (AJ)'
        peso_madre_col = (f'Peso Madre \n{year}' if year == 2024
                          else f'Peso Madre\n{year}')
        peso_ternero_col = f'Peso Ternero {year}\n(205 días)'
        rows.append(pd.DataFrame({
            'idv':              new['idv'],
            'year':             year,
            'ihm':              new[ihm_col].map(to_proportion),
            'peso_madre':       pd.to_numeric(new[peso_madre_col], errors='coerce'),
            'peso_ternero_205': pd.to_numeric(new[peso_ternero_col], errors='coerce'),
            'source':           'historico_new',
        }))

    # Older unadjusted IHM (fallback for years not in new file)
    old = sources['historial_ihm_old'].copy()
    old['idv'] = normalize_idv_column(old['IDV'])
    old = old[old['idv'].notna()]
    for year in [2022, 2023, 2024, 2025]:
        ihm_col = f'IHM {year}'
        if ihm_col not in old.columns:
            continue
        rows.append(pd.DataFrame({
            'idv':              old['idv'],
            'year':             year,
            'ihm':              old[ihm_col].map(to_proportion),
            'peso_madre':       np.nan,
            'peso_ternero_205': np.nan,
            'source':           'historial_old',
        }))

    long = pd.concat(rows, ignore_index=True)

    # Deduplicate: prefer historico_new
    long['_priority'] = long['source'].map(
        {'historico_new': 1, 'historial_old': 2}
    )
    long = long.sort_values(['idv', 'year', '_priority'])
    long = long.drop_duplicates(subset=['idv', 'year'], keep='first')
    long = long.drop(columns='_priority').reset_index(drop=True)
    return long


# ---------------------------------------------------------------------------
# Outcome target — mean future IHM
# ---------------------------------------------------------------------------

def compute_future_ihm(ihm_history: pd.DataFrame,
                        registry: pd.DataFrame,
                        first_outcome_age: int = 4) -> pd.DataFrame:
    """For each cow, compute her future-IHM outcomes treating year = age 4+
    as adult-cow regime (per farmer: first-year IHM is inflated for vaquillonas).

    Parameters
    ----------
    first_outcome_age : minimum age (in years) for an IHM to count as adult.
        Default 4: cow born in 2020, first adult IHM = 2024.

    Returns one row per cow with columns:
        idv
        n_outcome_years     # of years with adult IHM observations
        mean_future_ihm     average over outcome years (real, >0 only)
        max_future_ihm
        any_future_ihm      bool: at least one outcome observation
    """
    df = ihm_history.merge(
        registry[['idv', 'anio_nacimiento']], on='idv', how='left'
    )
    df['age'] = df['year'] - df['anio_nacimiento']
    adult = df[(df['age'] >= first_outcome_age) &
                df['ihm'].notna() &
                (df['ihm'] > 0)].copy()

    if len(adult) == 0:
        return pd.DataFrame(columns=['idv', 'n_outcome_years', 'mean_future_ihm',
                                      'max_future_ihm', 'any_future_ihm'])

    agg = adult.groupby('idv').agg(
        n_outcome_years=('ihm', 'count'),
        mean_future_ihm=('ihm', 'mean'),
        max_future_ihm=('ihm', 'max'),
    ).reset_index()
    agg['any_future_ihm'] = True
    return agg


# ---------------------------------------------------------------------------
# Selection-time mother-IHM features (leakage-safe)
# ---------------------------------------------------------------------------

def mother_ihm_at_selection(ihm_history: pd.DataFrame,
                             registry: pd.DataFrame,
                             selection_year_offset: int = 2) -> pd.DataFrame:
    """For every cow in the registry, compute her mother's IHM history
    STRICTLY BEFORE the cow's selection year.

    A cow born in 2020 has selection year 2022 (offset=2). Her mother's IHM
    observations from 2021 and earlier are leakage-safe; 2022 onward is not.

    Returns one row per heifer (cow with known mother) with:
        idv (heifer)
        madre_idv
        madre_n_ihm_pre
        madre_mean_ihm_pre
        madre_max_ihm_pre
        madre_latest_ihm_pre
    """
    cohort = registry[registry['madre_idv'].notna() &
                       registry['anio_nacimiento'].notna()].copy()
    cohort['selection_year'] = cohort['anio_nacimiento'] + selection_year_offset

    # Real (non-zero) IHM observations only
    real = ihm_history[ihm_history['ihm'].notna() &
                        (ihm_history['ihm'] > 0)].copy()

    rows = []
    for _, row in cohort.iterrows():
        madre = row['madre_idv']
        cutoff = row['selection_year']
        m = real[(real['idv'] == madre) & (real['year'] < cutoff)]
        if len(m):
            rows.append({
                'idv': row['idv'],
                'madre_idv': madre,
                'madre_n_ihm_pre': len(m),
                'madre_mean_ihm_pre': m['ihm'].mean(),
                'madre_max_ihm_pre': m['ihm'].max(),
                'madre_latest_ihm_pre': m.sort_values('year')['ihm'].iloc[-1],
            })
        else:
            rows.append({
                'idv': row['idv'],
                'madre_idv': madre,
                'madre_n_ihm_pre': 0,
                'madre_mean_ihm_pre': np.nan,
                'madre_max_ihm_pre': np.nan,
                'madre_latest_ihm_pre': np.nan,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sire-effect features
# ---------------------------------------------------------------------------

def sire_average_outcome(ihm_history: pd.DataFrame,
                          registry: pd.DataFrame,
                          first_outcome_age: int = 4) -> pd.DataFrame:
    """Per-sire average daughter-IHM, restricted to OTHER daughters of that
    sire whose adult IHM is observed.

    For each cow (potential heifer), we want the average adult IHM of her
    sire's other daughters (excluding herself). This is leakage-safe at
    selection time only if those other daughters' adult IHM was already
    measurable by the cow's selection year. We compute this conservatively
    using only daughters whose adult IHM was observed in years strictly
    before the cow's selection year.

    Returns one row per cow:
        idv
        sire_n_prior_daughters_observed
        sire_mean_daughter_ihm_prior
    """
    df = ihm_history.merge(
        registry[['idv', 'anio_nacimiento', 'nombre_padre']],
        on='idv', how='left'
    )
    df['age'] = df['year'] - df['anio_nacimiento']
    adult = df[(df['age'] >= first_outcome_age) &
                df['ihm'].notna() & (df['ihm'] > 0) &
                df['nombre_padre'].notna()].copy()

    cohort = registry[registry['nombre_padre'].notna() &
                       registry['anio_nacimiento'].notna()].copy()
    cohort['selection_year'] = cohort['anio_nacimiento'] + 2

    rows = []
    for _, row in cohort.iterrows():
        sire = row['nombre_padre']
        cutoff = row['selection_year']
        own = row['idv']
        peers = adult[(adult['nombre_padre'] == sire) &
                       (adult['idv'] != own) &
                       (adult['year'] < cutoff)]
        if len(peers):
            rows.append({
                'idv': own,
                'sire_n_prior_daughters_observed': peers['idv'].nunique(),
                'sire_mean_daughter_ihm_prior': peers['ihm'].mean(),
            })
        else:
            rows.append({
                'idv': own,
                'sire_n_prior_daughters_observed': 0,
                'sire_mean_daughter_ihm_prior': np.nan,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Build the supervised dataset
# ---------------------------------------------------------------------------

def build_supervised_dataset(sources: dict,
                              registry: pd.DataFrame,
                              ihm_history: pd.DataFrame,
                              min_birth_year: int = 2017,
                              max_birth_year: int = 2022) -> pd.DataFrame:
    """Build the analysis-ready supervised dataset.

    Each row is a heifer with at-selection-time features and her future-IHM
    outcome. Restricted to female cows born in the configured range whose
    adult IHM has been at least partially observed.

    Columns:
        idv, anio_nacimiento, selection_year
        peso_al_nacer, pelaje, tipo_padre, nombre_padre
        rodeo_nacimiento, rodeo_gestacion
        madre_idv, madre_n_ihm_pre, madre_mean_ihm_pre, madre_max_ihm_pre,
        madre_latest_ihm_pre
        sire_n_prior_daughters_observed, sire_mean_daughter_ihm_prior
        n_outcome_years, mean_future_ihm, max_future_ihm
    """
    base = registry[
        (registry['sex'].astype(str).str.strip() == 'Hembra') &
        registry['anio_nacimiento'].notna() &
        (registry['anio_nacimiento'] >= min_birth_year) &
        (registry['anio_nacimiento'] <= max_birth_year)
    ].copy()
    base['selection_year'] = base['anio_nacimiento'].astype(int) + 2

    # Mother features
    mom = mother_ihm_at_selection(ihm_history, registry)
    base = base.merge(mom, on=['idv', 'madre_idv'], how='left')

    # Sire features
    sire = sire_average_outcome(ihm_history, registry)
    base = base.merge(sire, on='idv', how='left')

    # Outcome
    outcome = compute_future_ihm(ihm_history, registry)
    base = base.merge(outcome, on='idv', how='left')

    return base.reset_index(drop=True)
