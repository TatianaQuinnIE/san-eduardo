"""
Phase 2: extended supervised dataset with reproductive features.

This module wraps `build_supervised_dataset` from src.features and adds:
  - Cow's own reproductive history (pregnancy_rate, early_conception_rate)
  - Mother's reproductive history pre-selection (when available)
  - Composite productivity outcome (IHM × pregnancy_rate)

The composite outcome reflects Matteo's framing: "we are not just building
a predictive model, but understanding a real-life decision system." A
productive cow is one that produces high IHM AND conceives reliably.

Key empirical finding: in our data, mean future IHM and pregnancy rate are 
weakly negatively correlated (r ≈ −0.15). They measure two genuinely different
productivity dimensions. This justifies the multi-target framing.
"""

import numpy as np
import pandas as pd

from src.features import build_supervised_dataset
from src.reproduction import (
    build_reproduction_events,
    build_reproduction_outcomes,
    cow_reproductive_summary,
    mother_reproductive_at_selection,
)


def build_supervised_dataset_v2(sources: dict,
                                  registry: pd.DataFrame,
                                  ihm_history: pd.DataFrame,
                                  raw_dir,
                                  min_birth_year: int = 2017,
                                  max_birth_year: int = 2022) -> pd.DataFrame:
    """Extended supervised dataset including reproductive features.

    Adds these columns to the base dataset:

    Mother's reproductive history (leakage-safe, pre-selection only):
        madre_n_cycles_pre
        madre_pregnancy_rate_pre
        madre_early_conception_rate_pre

    Cow's own reproductive history (one row per cow, post-selection):
        own_n_cycles
        own_n_pregnancies
        own_pregnancy_rate
        own_early_conception_rate
        own_n_vacia

    Composite outcomes (use either or both as targets):
        mean_future_ihm                 (already in base)
        own_pregnancy_rate              (secondary outcome)
        composite_productivity          (mean_future_ihm × own_pregnancy_rate)
    """
    # Base dataset (IHM target + selection-time features from features.py)
    base = build_supervised_dataset(sources, registry, ihm_history,
                                     min_birth_year=min_birth_year,
                                     max_birth_year=max_birth_year)

    # Reproductive events and outcomes
    events = build_reproduction_events(raw_dir)
    outcomes = build_reproduction_outcomes(events)

    # Mother's reproductive history pre-selection
    mom_repro = mother_reproductive_at_selection(outcomes, registry)
    base = base.merge(
        mom_repro[['idv', 'madre_n_cycles_pre',
                   'madre_pregnancy_rate_pre',
                   'madre_early_conception_rate_pre']],
        on='idv', how='left'
    )

    # Cow's own reproductive history (used as secondary outcome and as
    # post-selection observation, NOT as a feature for the IHM model)
    own_repro = cow_reproductive_summary(outcomes, registry)
    own_repro = own_repro.rename(columns={
        'n_cycles_observed':       'own_n_cycles',
        'n_pregnancies':           'own_n_pregnancies',
        'pregnancy_rate':          'own_pregnancy_rate',
        'early_conception_rate':   'own_early_conception_rate',
        'n_vacia':                 'own_n_vacia',
    })
    base = base.merge(own_repro, on='idv', how='left')

    # Composite productivity outcome
    base['composite_productivity'] = (
        base['mean_future_ihm'] * base['own_pregnancy_rate']
    )

    return base


def supervised_summary(ds: pd.DataFrame) -> dict:
    """Quick stats on coverage of the v2 dataset."""
    trainable = ds[ds['mean_future_ihm'].notna()]
    return {
        'total_rows':                  len(ds),
        'with_ihm_outcome':            int(ds['mean_future_ihm'].notna().sum()),
        'with_repro_outcome':          int(ds['own_pregnancy_rate'].notna().sum()),
        'with_both_outcomes':          int(((ds['mean_future_ihm'].notna()) &
                                            (ds['own_pregnancy_rate'].notna())).sum()),
        'with_composite_outcome':      int(ds['composite_productivity'].notna().sum()),
        'with_mother_ihm_pre':         int(ds['madre_mean_ihm_pre'].notna().sum()),
        'with_mother_repro_pre':       int(ds['madre_pregnancy_rate_pre'].notna().sum()),
    }
