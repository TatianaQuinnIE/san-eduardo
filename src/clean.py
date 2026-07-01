"""
Cleaning and normalization.

The farm's spreadsheets carry the kind of inconsistencies you'd expect from
a decade of pragmatic Excel work: cow IDs in mixed casing, label spellings
that drift over time, IHM values stored as percent in the old file and
proportion in the new one. This module canonicalizes those values without
losing information — we only normalize, we don't impute.

Every transformation in here is conservative. Imputation choices are
deferred to the modelling stage, where they can be made in context.

All decisions are mirrored in `reports/data_dictionary.md`.
"""

import re

import numpy as np
import pandas as pd


# ----- IDV (cow ID) normalization -------------------------------------------
#
# The IDV is the cow's permanent identifier. It looks like "BE099L322" but
# in the source data it appears as "Be099l322", "  BE099L322 ", "be099L322 ",
# and occasionally as the literal string "s/d" or "Desconocido" when a
# value was unknown at the time of entry.
#
# Canonical form: uppercase, all whitespace stripped. Anything that isn't a
# real ID becomes None.

_IDV_PLACEHOLDERS = {
    '', 'NAN', 'S/D', 'DESCONOCIDO', '#N/D', '#N/A', 'NONE', 'NULL',
}


def normalize_idv(value):
    """Canonical IDV string, or None for missing/placeholder."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    s = str(value).strip().upper()
    if s in _IDV_PLACEHOLDERS:
        return None
    s = re.sub(r'\s+', '', s)
    return s if s else None


def normalize_idv_column(series):
    """Vectorized version of normalize_idv."""
    return series.map(normalize_idv)


# ----- Label normalization --------------------------------------------------
#
# The farm uses two distinct labelling schemes that evolved across years:
#
#  • 'verdes' (used for the 2025 cohort): 3 Verdes, 2 Verdes, 1 Verde,
#    Venta, plus older terms like FM Venta, Invernada, Pesada sin Genealogia.
#
#  • 'estrellas' (used for the 2027 cohort): 3 Estrellas, 2 Estrellas,
#    1 Estrella, Venta, Venta Reproduccion, Pesadas sin Genealogia.
#
# Within each scheme, casing is inconsistent ('2 Verdes' vs '2 verdes',
# 'Venta Reproduccion' vs 'Venta reproduccion'). The canonical form is
# snake_case prefixed with the scheme name, so downstream code can tell
# 'verdes_3' apart from 'estrellas_3' (we don't yet know whether they
# mean the same thing — see data_dictionary.md).

VERDES_CANONICAL = {
    '3 verdes':                'verdes_3',
    '2 verdes':                'verdes_2',
    '1 verde':                 'verdes_1',
    'fm venta':                'verdes_fm_venta',
    'pesada sin genealogia':   'verdes_pesada_sin_genealogia',
    'pesadas sin genealogia':  'verdes_pesada_sin_genealogia',
    'invernada':               'verdes_invernada',
    'venta':                   'verdes_venta',
    'ver':                     'verdes_revisar',
}

ESTRELLAS_CANONICAL = {
    '3 estrellas':             'estrellas_3',
    '2 estrellas':             'estrellas_2',
    '1 estrella':              'estrellas_1',
    'pesadas sin genealogia':  'estrellas_pesada_sin_genealogia',
    'pesada sin genealogia':   'estrellas_pesada_sin_genealogia',
    'venta':                   'estrellas_venta',
    'venta reproduccion':      'estrellas_venta_reproduccion',
}


def _canonicalize_text(value):
    """Lowercase, strip, drop accents, collapse whitespace.

    We strip accents the manual way (replace á → a etc.) rather than via
    unicodedata, because the set of accents that actually appears in this
    data is small and known.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    s = str(value).strip().lower()
    s = (s.replace('á', 'a').replace('é', 'e').replace('í', 'i')
           .replace('ó', 'o').replace('ú', 'u').replace('ñ', 'n'))
    s = re.sub(r'\s+', ' ', s)
    return s if s else None


def normalize_label_verdes(value):
    """Map a 2025 'verdes' label to canonical form. Unknown → None."""
    s = _canonicalize_text(value)
    return VERDES_CANONICAL.get(s)


def normalize_label_estrellas(value):
    """Map a 2027 'estrellas' label to canonical form. Unknown → None."""
    s = _canonicalize_text(value)
    return ESTRELLAS_CANONICAL.get(s)


# A coarse, scheme-agnostic mapping. Approximate — confirm with the farm
# before relying on it for cross-cohort training. Documented in
# data_dictionary.md as tentative.
UNIFIED_TIER = {
    'verdes_3':                       'tier_top',
    'estrellas_3':                    'tier_top',
    'verdes_2':                       'tier_high',
    'estrellas_2':                    'tier_high',
    'verdes_1':                       'tier_mid',
    'estrellas_1':                    'tier_mid',
    'verdes_pesada_sin_genealogia':   'tier_unlabeled_heavy',
    'estrellas_pesada_sin_genealogia':'tier_unlabeled_heavy',
    'verdes_fm_venta':                'tier_sale_for_breeding',
    'estrellas_venta_reproduccion':   'tier_sale_for_breeding',
    'verdes_invernada':               'tier_fattening',
    'verdes_venta':                   'tier_fattening',
    'estrellas_venta':                'tier_fattening',
    'verdes_revisar':                 'tier_review',
}


def to_unified_tier(canonical_label):
    if canonical_label is None:
        return None
    return UNIFIED_TIER.get(canonical_label)


# ----- Pelaje (coat color) --------------------------------------------------
#
# The herd is split between black ('negro') and red ('colorado') rodeos.
# The farm also records spotted coats ('p_negro' = parted black) and mixed.

_PELAJE_MAP = {
    'negro':       'negro',
    'colorado':    'colorado',
    'p/negro':     'p_negro',
    'p/ negro':    'p_negro',
    'p/colorado':  'p_colorado',
    'p/ colorado': 'p_colorado',
    'mixto':       'mixto',
}


def normalize_pelaje(value):
    s = _canonicalize_text(value)
    return _PELAJE_MAP.get(s) if s else None


# ----- Tipo Padre (sire type) -----------------------------------------------

_TIPO_PADRE_MAP = {
    'iatf':            'iatf',
    'toro de repaso':  'repaso',
    't. repaso':       'repaso',
    'desconocido':     'desconocido',
}


def normalize_tipo_padre(value):
    s = _canonicalize_text(value)
    return _TIPO_PADRE_MAP.get(s) if s else None


# ----- IHM scale unification ------------------------------------------------
#
# Old file: percent (0–100).
# New file: proportion (0–1), already 205-day adjusted.
#
# We standardize on PROPORTION (0–1) everywhere downstream. Zero is a real
# observation meaning "no calf that year" — we keep it as 0.0 rather than
# treating it as missing, so the caller can decide.

def to_proportion(ihm_value):
    """Coerce an IHM value to proportion (0–1).

    Rules:
      * already a proportion (0 < x < 1.5)  → returned as-is
      * percent (1.5 ≤ x ≤ 100)             → divided by 100
      * 's/d', '#N/A', NaN, None            → NaN
      * exact zero                          → 0.0 (semantically: no calf)
      * out of range                        → NaN (treated as bad data)
    """
    if ihm_value is None:
        return np.nan
    try:
        x = float(ihm_value)
    except (TypeError, ValueError):
        return np.nan
    if np.isnan(x):
        return np.nan
    if x == 0:
        return 0.0
    if 0 < x < 1.5:
        return x
    if 1.5 <= x <= 100:
        return x / 100
    return np.nan