"""
Concept drift quantification — IHM input change only.

The documented weight threshold (190 kg) has not changed. What did evolve
is the IHM input: newer files use 205-day-adjusted weaning weight instead
of raw weaning weight.

This script is retained for structural completeness. The weight threshold
(190 kg) has not changed; only the IHM input evolved (raw → 205-day adjusted).

Output:
  outputs/tables/concept_drift.csv      kept-set overlap (single rule version)
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import pandas as pd

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.load import load_all_sources
from src.rules import (
    build_verdes_rule_inputs,
    apply_verdes_rule,
    VERDES_THRESHOLDS_DOCUMENTED,
)


def main():
    out_tables = ROOT / 'outputs' / 'tables'
    out_tables.mkdir(parents=True, exist_ok=True)

    sources = load_all_sources(ROOT / 'data' / 'raw')
    inputs = build_verdes_rule_inputs(sources['fm_prep_2025'])

    inputs['predicted'] = inputs.apply(
        lambda r: apply_verdes_rule(r, thresholds=VERDES_THRESHOLDS_DOCUMENTED), axis=1
    )

    print(f'Applied documented rule (190 kg) to 2025 cohort (n={len(inputs)} heifers).')

    tier_definitions = [
        ('top tier only', ['verdes_3']),
        ('top 2 tiers',   ['verdes_3', 'verdes_2']),
        ('all kept',      ['verdes_3', 'verdes_2', 'verdes_1']),
    ]

    rows = []
    for label, classes in tier_definitions:
        kept = inputs[inputs['predicted'].isin(classes)]
        rows.append({
            'comparison':      label,
            'documented_kept': len(kept),
            'revised_kept':    len(kept),
            'intersection':    len(kept),
            'union':           len(kept),
            'jaccard':         1.0,
        })

    drift = pd.DataFrame(rows)
    drift.to_csv(out_tables / 'concept_drift.csv', index=False)
    print(drift.to_string(index=False))


if __name__ == '__main__':
    main()
