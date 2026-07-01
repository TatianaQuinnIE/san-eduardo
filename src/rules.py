"""
Programmatic reproduction of the farm's hand-coded heifer-selection rules.

Two schemes documented:
  - 'verdes' (2025 cohort): based on the slide table — weight, sire IATF,
    mother known, mother IHM threshold.
  - 'estrellas' (2027 cohort): more nuanced, with the engineered binary
    flags (Hija IATF?, Abuelo Moderado?, Hija Cut, IHM Minimo).

The 'verdes' scheme uses a weight threshold of 190 kg. The underlying
criteria also evolved in the newer scheme:
  - IHM input: raw weaning weight → 205-day adjusted weight
  - New 'venta_reproduccion' category in 2027: heifers passing IHM but
    whose mothers exceed 550 kg (frame control)
  - Implicit 'madre CUT' bonus: cows from the CUT (longeva) rodeo get
    an upgrade — not in any documentation.

Reproducing the documented rule on the 2025 cohort yields ~49% match,
with perfect agreement in the top tier (verdes_3) and divergence in
lower tiers — evidence the documented rule captures only part of the
actual decision logic.
"""

import pandas as pd
import numpy as np

from src.clean import (
    normalize_idv_column,
    normalize_label_verdes,
    normalize_label_estrellas,
    normalize_tipo_padre,
    to_proportion,
)


VERDES_THRESHOLDS_DOCUMENTED = {
    'peso_destete_min': 190.0,   # documented in slide
    'ihm_madre_min':    0.40,
}


# Canonical tier ordering across both label namespaces (predicted + recorded).
# Used by make_report_tables.py to compute tier-distance for the deviation list sort.
# Higher = better outcome for the heifer from this farm's perspective.
TIER_ORDER = {
    'verdes_3':                     4,  # top tier: IATF sire, known mother, IHM ≥ 0.40
    'verdes_2':                     3,  # good tier: known sire (not IATF), genealogy complete
    'verdes_1':                     2,  # recorded only: kept, below full criteria
    'verdes_fm_venta':              1,  # sold as future mother to another farm
    'verdes_pesada_sin_genealogia': 1,  # heavy but no known mother — sell as fm_venta equivalent
    'verdes_venta':                 0,  # recorded only: sold to fattening / commercial
    'verdes_invernada':             0,  # fattened (below weight threshold)
    'verdes_unknown':               0,  # no weight data available
}


def apply_verdes_rule(row, thresholds=VERDES_THRESHOLDS_DOCUMENTED) -> str:
    """Apply the 'verdes' rule to a single heifer row.

    Expected fields:
        peso_destete   : weaning weight (kg)
        padre_conocido : bool
        padre_iatf     : bool
        madre_conocida : bool
        ihm_madre      : mother's most recent IHM as proportion (or NaN)
    """
    peso = row.get('peso_destete', np.nan)
    if pd.isna(peso):
        return 'verdes_unknown'

    if peso <= thresholds['peso_destete_min']:
        return 'verdes_invernada'

    madre_conocida = bool(row.get('madre_conocida', False))
    if not madre_conocida:
        return 'verdes_pesada_sin_genealogia'

    ihm = row.get('ihm_madre', np.nan)
    if pd.isna(ihm) or ihm < thresholds['ihm_madre_min']:
        return 'verdes_fm_venta'

    padre_conocido = bool(row.get('padre_conocido', False))
    if not padre_conocido:
        return 'verdes_2'

    padre_iatf = bool(row.get('padre_iatf', False))
    return 'verdes_3' if padre_iatf else 'verdes_2'


def build_verdes_rule_inputs(fm_prep_df: pd.DataFrame) -> pd.DataFrame:
    """Pre-process the FM p-rep. sheet into the columns apply_verdes_rule expects."""
    df = fm_prep_df.copy()
    df = df[df['Sexo'].astype(str).str.strip() == 'Hembra'].copy()

    out = pd.DataFrame({
        'idv':            normalize_idv_column(df['IDV']),
        'peso_destete':   pd.to_numeric(df['Peso'], errors='coerce'),
        'madre_idv':      normalize_idv_column(df['Madre IDV']),
        'tipo_padre':     df['TIpo Padre'].map(normalize_tipo_padre),
    })
    out['madre_conocida'] = out['madre_idv'].notna()
    out['padre_conocido'] = out['tipo_padre'].notna() & (out['tipo_padre'] != 'desconocido')
    out['padre_iatf']     = out['tipo_padre'] == 'iatf'

    # Most recent IHM available (try 2025 → 2024 → 2023 → 2022)
    latest_ihm = pd.Series(np.nan, index=df.index)
    for c in ['IHM Madre 2025', 'IHM Madre 2024', 'IHM Madre 2023', 'IHM Madre 2022']:
        if c in df.columns:
            this_year = df[c].map(to_proportion)
            mask = latest_ihm.isna() & this_year.notna()
            latest_ihm.loc[mask] = this_year.loc[mask]
    out['ihm_madre'] = latest_ihm.values
    out['recorded_label'] = df['Presel 2025'].map(normalize_label_verdes).values
    return out


def evaluate_rule_reproduction(rule_inputs: pd.DataFrame,
                                rule_fn=apply_verdes_rule,
                                thresholds=VERDES_THRESHOLDS_DOCUMENTED) -> dict:
    """Apply the rule and compare against recorded labels."""
    df = rule_inputs.copy()
    df['predicted'] = df.apply(lambda r: rule_fn(r, thresholds=thresholds), axis=1)
    eval_df = df[df['recorded_label'].notna()].copy()
    match = (eval_df['predicted'] == eval_df['recorded_label']).mean()
    confusion = pd.crosstab(eval_df['recorded_label'], eval_df['predicted'])
    return {
        'n_evaluable':  len(eval_df),
        'n_match':      int((eval_df['predicted'] == eval_df['recorded_label']).sum()),
        'match_rate':   float(match),
        'confusion':    confusion,
        'predictions': df,
    }


# ---------------------------------------------------------------------------
# Concept drift analysis
# ---------------------------------------------------------------------------

def cohort_overlap(rule_a_predictions: pd.DataFrame,
                    rule_b_predictions: pd.DataFrame,
                    keep_classes: list,
                    id_col: str = 'idv') -> dict:
    """Compute Jaccard overlap between two rule's 'kept' sets.

    keep_classes : list of canonical labels treated as 'keep' (e.g.,
                   ['verdes_3', 'verdes_2'] for the top two tiers).
    """
    a = set(rule_a_predictions.loc[
        rule_a_predictions['predicted'].isin(keep_classes), id_col
    ])
    b = set(rule_b_predictions.loc[
        rule_b_predictions['predicted'].isin(keep_classes), id_col
    ])
    inter = a & b
    union = a | b
    jaccard = len(inter) / len(union) if union else 0.0
    return {
        'rule_a_kept':  len(a),
        'rule_b_kept':  len(b),
        'intersection': len(inter),
        'union':        len(union),
        'jaccard':      jaccard,
    }
