"""Phase 2 modeling: predict three different productivity targets and
compare model performance + ranking quality across them.

Targets:
  1. mean_future_ihm        — milk transfer (Layer 1 from Matteo)
  2. own_pregnancy_rate     — reproductive consistency
  3. composite_productivity — IHM × pregnancy_rate

Run from project root:
    python scripts/run_models_v2.py
"""

import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_predict
from scipy.stats import spearmanr

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.models import build_models
from src.evaluation import (
    regression_metrics,
    evaluate_selection,
    mean_outcome_of_top_k,
)


def main():
    out_tables = ROOT / 'outputs' / 'tables'
    out_tables.mkdir(parents=True, exist_ok=True)

    ds = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset_v2.csv')

    # Selection-time features (NO post-selection info leaking in)
    numeric_features = [
        'anio_nacimiento',
        'peso_al_nacer',
        'madre_n_ihm_pre',
        'madre_mean_ihm_pre',
        'madre_max_ihm_pre',
        'madre_latest_ihm_pre',
        'sire_n_prior_daughters_observed',
        'sire_mean_daughter_ihm_prior',
    ]
    categorical_features = [
        'pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion',
    ]
    numeric_features = [c for c in numeric_features if c in ds.columns]
    categorical_features = [c for c in categorical_features if c in ds.columns]

    targets = {
        'mean_future_ihm':         'IHM target (Layer 1)',
        'own_pregnancy_rate':      'Reproductive consistency',
        'composite_productivity':  'Composite productivity',
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    rows = []

    for target, description in targets.items():
        sub = ds[ds[target].notna()].copy()
        if len(sub) < 50:
            print(f'\nSkipping {target}: only {len(sub)} rows')
            continue
        print(f'\n=== Target: {target} ({description}) ===')
        print(f'   n = {len(sub)}, mean = {sub[target].mean():.3f}, std = {sub[target].std():.3f}')

        X = sub[numeric_features + categorical_features]
        y = sub[target].astype(float).values

        models = build_models(numeric_features, categorical_features)
        for name, pipe in models.items():
            try:
                preds = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)
            except Exception as e:
                print(f'   skipping {name}: {e}')
                continue
            reg = regression_metrics(y, preds)
            sel_30 = evaluate_selection(y, preds, k_fractions=[0.3]).iloc[0].to_dict()
            sel_50 = evaluate_selection(y, preds, k_fractions=[0.5]).iloc[0].to_dict()
            rows.append({
                'target':              target,
                'model':               name,
                'n':                   len(sub),
                'rmse':                reg['rmse'],
                'spearman':            reg['spearman'],
                'precision_at_0.3':    sel_30['precision_at_k'],
                'precision_at_0.5':    sel_50['precision_at_k'],
                'mean_topk_outcome_30':mean_outcome_of_top_k(y, preds, int(len(y)*0.3)),
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(['target', 'precision_at_0.3'], ascending=[True, False])
    df.to_csv(out_tables / 'model_comparison_v2.csv', index=False)
    print('\n=== Full comparison ===')
    for target in targets:
        print(f'\n{target}:')
        sub = df[df['target'] == target][['model', 'spearman', 'precision_at_0.3', 'rmse']]
        print(sub.to_string(index=False))


if __name__ == '__main__':
    main()
