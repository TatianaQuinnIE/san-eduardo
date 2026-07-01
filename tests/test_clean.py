"""Unit tests for src/clean.py.

Run from project root: pytest tests/
"""

import math

import numpy as np
import pandas as pd
import pytest

from src.clean import (
    normalize_idv,
    normalize_idv_column,
    normalize_label_verdes,
    normalize_label_estrellas,
    normalize_pelaje,
    normalize_tipo_padre,
    to_proportion,
    to_unified_tier,
)


# ---- IDV normalization -----------------------------------------------------

class TestNormalizeIdv:

    def test_uppercase(self):
        assert normalize_idv('be099l322') == 'BE099L322'

    def test_strips_whitespace(self):
        assert normalize_idv('  BE099L322  ') == 'BE099L322'

    def test_internal_whitespace_removed(self):
        # Sometimes IDs come with stray spaces in the middle
        assert normalize_idv('BE099 L322') == 'BE099L322'

    def test_none_passthrough(self):
        assert normalize_idv(None) is None

    def test_nan_passthrough(self):
        assert normalize_idv(float('nan')) is None

    def test_placeholder_sd(self):
        assert normalize_idv('s/d') is None

    def test_placeholder_desconocido(self):
        assert normalize_idv('Desconocido') is None

    def test_placeholder_na(self):
        assert normalize_idv('#N/A') is None

    def test_empty_string(self):
        assert normalize_idv('') is None

    def test_column_vectorized(self):
        # pandas turns None into NaN when stored in a Series, so we check
        # the truthy values explicitly and the missing ones via isna()
        s = pd.Series(['be099l322', 's/d', None, '  XYZ  '])
        out = normalize_idv_column(s)
        assert out.iloc[0] == 'BE099L322'
        assert pd.isna(out.iloc[1])
        assert pd.isna(out.iloc[2])
        assert out.iloc[3] == 'XYZ'


# ---- Label normalization ---------------------------------------------------

class TestNormalizeLabelVerdes:

    def test_canonical_form(self):
        assert normalize_label_verdes('3 Verdes') == 'verdes_3'

    def test_lowercase_input(self):
        # The label '2 verdes' (lowercase) appears alongside '2 Verdes'
        # in the source data; both must map to the same canonical value
        assert normalize_label_verdes('2 verdes') == 'verdes_2'
        assert normalize_label_verdes('2 Verdes') == 'verdes_2'

    def test_extra_whitespace(self):
        assert normalize_label_verdes('  1 Verde  ') == 'verdes_1'

    def test_unknown_label_returns_none(self):
        assert normalize_label_verdes('Algo Raro') is None

    def test_none_input(self):
        assert normalize_label_verdes(None) is None

    def test_pesada_singular_and_plural(self):
        # The farm uses both 'Pesada sin Genealogia' and 'Pesadas sin Genealogia'
        assert normalize_label_verdes('Pesada sin Genealogia') == 'verdes_pesada_sin_genealogia'
        assert normalize_label_verdes('Pesadas sin Genealogia') == 'verdes_pesada_sin_genealogia'


class TestNormalizeLabelEstrellas:

    def test_canonical_form(self):
        assert normalize_label_estrellas('3 Estrellas') == 'estrellas_3'

    def test_venta_reproduccion_casing(self):
        # 'Venta Reproduccion' and 'Venta reproduccion' both appear in source
        assert normalize_label_estrellas('Venta Reproduccion') == 'estrellas_venta_reproduccion'
        assert normalize_label_estrellas('Venta reproduccion') == 'estrellas_venta_reproduccion'

    def test_distinct_from_verdes(self):
        # 'venta' alone maps to estrellas_venta when called via the estrellas
        # normalizer. Critical: should NOT return 'verdes_venta'.
        assert normalize_label_estrellas('Venta') == 'estrellas_venta'
        assert normalize_label_verdes('Venta') == 'verdes_venta'


# ---- Pelaje ----------------------------------------------------------------

class TestNormalizePelaje:

    def test_basic(self):
        assert normalize_pelaje('Negro') == 'negro'
        assert normalize_pelaje('Colorado') == 'colorado'

    def test_parted(self):
        assert normalize_pelaje('P/Negro') == 'p_negro'
        assert normalize_pelaje('P/ Negro') == 'p_negro'

    def test_unknown_returns_none(self):
        assert normalize_pelaje('rosado') is None


# ---- Tipo Padre ------------------------------------------------------------

class TestNormalizeTipoPadre:

    def test_iatf(self):
        assert normalize_tipo_padre('IATF') == 'iatf'
        assert normalize_tipo_padre('iatf') == 'iatf'

    def test_repaso_variants(self):
        # The source uses both 'Toro de Repaso' and 'T. Repaso'
        assert normalize_tipo_padre('Toro de Repaso') == 'repaso'
        assert normalize_tipo_padre('T. Repaso') == 'repaso'

    def test_unknown(self):
        assert normalize_tipo_padre('Desconocido') == 'desconocido'


# ---- IHM scale conversion --------------------------------------------------

class TestToProportion:

    def test_already_proportion(self):
        # New file uses 0–1 scale; pass through unchanged
        assert to_proportion(0.45) == pytest.approx(0.45)
        assert to_proportion(0.30) == pytest.approx(0.30)

    def test_percent_converted(self):
        # Old file uses 0–100 scale; convert to 0–1
        assert to_proportion(45.0) == pytest.approx(0.45)
        assert to_proportion(30.0) == pytest.approx(0.30)

    def test_zero_preserved(self):
        # IHM = 0 means "cow had no calf that year" — semantically real,
        # NOT missing. Must be preserved as 0.0, not converted to NaN.
        assert to_proportion(0) == 0.0
        assert to_proportion(0.0) == 0.0

    def test_string_sd_returns_nan(self):
        # 's/d' (sin dato) is the farm's missing-data marker
        assert math.isnan(to_proportion('s/d'))

    def test_none_returns_nan(self):
        assert math.isnan(to_proportion(None))

    def test_actual_nan_returns_nan(self):
        assert math.isnan(to_proportion(float('nan')))

    def test_out_of_range_returns_nan(self):
        # Values above 100 are not valid IHM
        assert math.isnan(to_proportion(150.0))
        assert math.isnan(to_proportion(-5.0))

    def test_boundary_1_5(self):
        # The boundary between "is this proportion or percent?" is at 1.5.
        # Below 1.5 → assume already proportion. At 1.5 and above → assume percent.
        assert to_proportion(1.4) == pytest.approx(1.4)
        assert to_proportion(1.5) == pytest.approx(0.015)


# ---- Unified tier mapping --------------------------------------------------

class TestUnifiedTier:

    def test_top_tier(self):
        assert to_unified_tier('verdes_3') == 'tier_top'
        assert to_unified_tier('estrellas_3') == 'tier_top'

    def test_fattening_collapse(self):
        # Both 'invernada' (verdes scheme) and 'venta' (estrellas scheme)
        # map to the same tier — because the farm uses 'venta' in 2027 to
        # mean what 'invernada' meant in 2025
        assert to_unified_tier('verdes_invernada') == 'tier_fattening'
        assert to_unified_tier('estrellas_venta') == 'tier_fattening'

    def test_none_passthrough(self):
        assert to_unified_tier(None) is None
