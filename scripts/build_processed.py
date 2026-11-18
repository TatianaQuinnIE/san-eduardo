"""End-to-end pipeline: raw files → analysis-ready CSVs in data/processed/.

Run from project root:
    python scripts/build_processed.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.load import load_all_sources
from src.lineage import build_cow_registry, build_lineage_table, lineage_summary
from src.events import build_event_table
from src.features import build_ihm_history, build_supervised_dataset, compute_future_ihm
from src.rules import (
    build_verdes_rule_inputs,
    evaluate_rule_reproduction,
    apply_verdes_rule,
    VERDES_THRESHOLDS_DOCUMENTED,
)


def main():
    raw = ROOT / 'data' / 'raw'
    out = ROOT / 'data' / 'processed'
    out.mkdir(exist_ok=True, parents=True)

    print('Loading sources...')
    sources = load_all_sources(raw)
    for k, v in sources.items():
        if hasattr(v, 'shape'):
            print(f'  {k}: {v.shape}')
        else:
            print(f'  {k}: text, {len(v)} chars')

    print('\nCow registry...')
    registry = build_cow_registry(sources)
    registry.to_csv(out / 'cow_registry.csv', index=False)
    print(f'  {len(registry)} cows')

    print('\nLineage...')
    lineage = build_lineage_table(registry)
    lineage.to_csv(out / 'lineage.csv', index=False)
    summary = lineage_summary(registry, lineage)
    for k, v in summary.items():
        print(f'  {k}: {v}')

    print('\nEvents (WhatsApp + IATF)...')
    events = build_event_table(sources)
    events.to_csv(out / 'events.csv', index=False)
    print(f'  {len(events)} events')

    print('\nIHM history...')
    ihm_history = build_ihm_history(sources)
    ihm_history.to_csv(out / 'ihm_history.csv', index=False)
    print(f'  {len(ihm_history)} cow-year observations')

    print('\nFuture-IHM outcomes...')
    outcomes = compute_future_ihm(ihm_history, registry)
    outcomes.to_csv(out / 'outcomes.csv', index=False)
    print(f'  {len(outcomes)} cows with future-IHM outcomes')

    print('\nSupervised dataset...')
    ds = build_supervised_dataset(sources, registry, ihm_history,
                                    min_birth_year=2017, max_birth_year=2022)
    ds.to_csv(out / 'supervised_dataset.csv', index=False)
    trainable = ds[ds['mean_future_ihm'].notna()]
    print(f'  {len(ds)} candidate rows ({len(trainable)} with outcomes)')

    print('\nRule reproduction (documented thresholds)...')
    inputs_doc = build_verdes_rule_inputs(sources['fm_prep_2025'])
    eval_doc = evaluate_rule_reproduction(
        inputs_doc, thresholds=VERDES_THRESHOLDS_DOCUMENTED
    )
    eval_doc['predictions'].to_csv(out / 'rule_predictions_documented.csv', index=False)
    print(f"  Match rate: {eval_doc['match_rate']*100:.1f}%  ({eval_doc['n_match']}/{eval_doc['n_evaluable']})")


    print('\nDone.')
    return {
        'registry': registry,
        'lineage': lineage,
        'events': events,
        'ihm_history': ihm_history,
        'outcomes': outcomes,
        'supervised': ds,
        'rule_doc': eval_doc,
    }


if __name__ == '__main__':
    main()
