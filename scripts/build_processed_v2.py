"""End-to-end pipeline v2: includes reproductive event extraction.

Outputs additional CSVs to data/processed/:
  reproduction_events.csv     all sessions in long form
  reproduction_outcomes.csv   one row per cow-year with cycle outcome
  cow_reproductive_summary.csv per-cow reproductive history aggregate
  supervised_dataset_v2.csv   extended supervised dataset with repro features

Run from project root:
    python scripts/build_processed_v2.py
"""

import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.load import load_all_sources
from src.lineage import build_cow_registry
from src.features import build_ihm_history
from src.reproduction import (
    build_reproduction_events,
    build_reproduction_outcomes,
    cow_reproductive_summary,
)
from src.supervised_v2 import build_supervised_dataset_v2, supervised_summary


def main():
    raw = ROOT / 'data' / 'raw'
    out = ROOT / 'data' / 'processed'
    out.mkdir(exist_ok=True, parents=True)

    print('Loading sources (v1)...')
    sources = load_all_sources(raw)
    registry = build_cow_registry(sources)
    ihm_history = build_ihm_history(sources)
    print(f'  registry: {len(registry)} cows')
    print(f'  ihm_history: {len(ihm_history)} cow-year rows')

    print('\nReproductive events...')
    events = build_reproduction_events(raw)
    events.to_csv(out / 'reproduction_events.csv', index=False)
    print(f'  {len(events)} events')
    print(f'  by kind:\n{events["session_kind"].value_counts().to_string()}')

    print('\nReproductive outcomes (one per cow per breeding cycle)...')
    outcomes = build_reproduction_outcomes(events)
    outcomes.to_csv(out / 'reproduction_outcomes.csv', index=False)
    print(f'  {len(outcomes)} cow-year outcomes across years '
          f'{sorted(outcomes["breeding_year"].unique())}')
    print(f'  outcome distribution:\n{outcomes["gestation_outcome"].value_counts().to_string()}')

    print('\nPer-cow reproductive summary...')
    own_summary = cow_reproductive_summary(outcomes, registry)
    own_summary.to_csv(out / 'cow_reproductive_summary.csv', index=False)
    print(f'  {len(own_summary)} cows with reproductive history')
    print(f'  {(own_summary["n_cycles_observed"] >= 2).sum()} with 2+ cycles')

    print('\nSupervised dataset v2...')
    ds = build_supervised_dataset_v2(sources, registry, ihm_history, raw,
                                       min_birth_year=2017, max_birth_year=2022)
    ds.to_csv(out / 'supervised_dataset_v2.csv', index=False)

    summary = supervised_summary(ds)
    print('  Coverage:')
    for k, v in summary.items():
        print(f'    {k}: {v}')

    print('\nDone.')


if __name__ == '__main__':
    main()
