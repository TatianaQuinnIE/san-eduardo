"""Train and compare all models. Run from project root.

Produces:
  outputs/tables/model_comparison.csv      one row per model
  outputs/tables/cv_predictions.csv        per-cow CV predictions
"""

import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_predict

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.models import build_models
from src.evaluation import (
    regression_metrics,
    evaluate_selection,
    mean_outcome_of_top_k,
    random_baseline_distribution,
    classification_metrics_at_quartile,
)


def main():
    out_tables = ROOT / 'outputs' / 'tables'
    out_tables.mkdir(parents=True, exist_ok=True)

    ds = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset.csv')

    # Filter to rows with the regression target
    ds = ds[ds['mean_future_ihm'].notna()].copy()

    # Define feature sets
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
        'pelaje',
        'tipo_padre',
        'rodeo_nacimiento',
        'rodeo_gestacion',
    ]

    # Keep only features that exist
    numeric_features = [c for c in numeric_features if c in ds.columns]
    categorical_features = [c for c in categorical_features if c in ds.columns]

    X = ds[numeric_features + categorical_features].copy()
    y = ds['mean_future_ihm'].astype(float).values

    print(f'Training population: {len(ds)} cows')
    print(f'Numeric features: {numeric_features}')
    print(f'Categorical features: {categorical_features}')
    print(f'Target stats: mean={y.mean():.3f}, std={y.std():.3f}')

    # K-fold cross-validation (5 folds)
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    cv_splits = list(cv.split(X))

    # Build trivial heuristic baselines that don't fit a model
    heuristic_predictions = {
        'heaviest':       _heuristic_heaviest(ds),
        'mother_ihm':     _heuristic_mother_ihm(ds),
        'random':         _heuristic_random(ds, seed=42),
    }

    models = build_models(numeric_features, categorical_features)

    rows = []

    # 1. Heuristic baselines
    for name, pred in heuristic_predictions.items():
        reg = regression_metrics(y, pred)
        sel_30 = evaluate_selection(y, pred, k_fractions=[0.3]).iloc[0].to_dict()
        sel_50 = evaluate_selection(y, pred, k_fractions=[0.5]).iloc[0].to_dict()
        clf = classification_metrics_at_quartile(y, pred)
        rows.append({
            'model':              f'heuristic_{name}',
            'rmse':               reg['rmse'],
            'mae':                reg['mae'],
            'r2':                 reg['r2'],
            'spearman':           reg['spearman'],
            'cv_r2_std':          float('nan'),
            'precision_at_0.3':   sel_30['precision_at_k'],
            'precision_at_0.5':   sel_50['precision_at_k'],
            'roc_auc':            clf['roc_auc'],
            'f1_top_quartile':    clf['f1_top_quartile'],
            'mean_topk_outcome_30': mean_outcome_of_top_k(y, pred, int(len(y)*0.3)),
            'mean_topk_outcome_50': mean_outcome_of_top_k(y, pred, int(len(y)*0.5)),
        })

    # 2. ML models via CV
    cv_preds = pd.DataFrame({'idv': ds['idv'].values, 'y_true': y})
    for name, pipe in models.items():
        try:
            preds = cross_val_predict(pipe, X, y, cv=cv_splits, n_jobs=-1)
        except Exception as e:
            print(f'  Skipping {name}: {e}')
            continue
        # Per-fold R² to report variance
        fold_r2s = []
        import sklearn.metrics as skm
        for train_idx, val_idx in cv_splits:
            pipe.fit(X.iloc[train_idx], y[train_idx])
            fold_pred = pipe.predict(X.iloc[val_idx])
            fold_r2s.append(skm.r2_score(y[val_idx], fold_pred))
        cv_r2_std = float(np.std(fold_r2s))

        cv_preds[f'pred_{name}'] = preds
        reg = regression_metrics(y, preds)
        sel_30 = evaluate_selection(y, preds, k_fractions=[0.3]).iloc[0].to_dict()
        sel_50 = evaluate_selection(y, preds, k_fractions=[0.5]).iloc[0].to_dict()
        clf = classification_metrics_at_quartile(y, preds)
        rows.append({
            'model':              name,
            'rmse':               reg['rmse'],
            'mae':                reg['mae'],
            'r2':                 reg['r2'],
            'spearman':           reg['spearman'],
            'cv_r2_std':          cv_r2_std,
            'precision_at_0.3':   sel_30['precision_at_k'],
            'precision_at_0.5':   sel_50['precision_at_k'],
            'roc_auc':            clf['roc_auc'],
            'f1_top_quartile':    clf['f1_top_quartile'],
            'mean_topk_outcome_30': mean_outcome_of_top_k(y, preds, int(len(y)*0.3)),
            'mean_topk_outcome_50': mean_outcome_of_top_k(y, preds, int(len(y)*0.5)),
        })

    df = pd.DataFrame(rows).sort_values('precision_at_0.3', ascending=False)
    df.to_csv(out_tables / 'model_comparison.csv', index=False)
    cv_preds.to_csv(out_tables / 'cv_predictions.csv', index=False)

    print('\nModel comparison:')
    print(df.to_string(index=False))

    print('\nRandom baseline (sanity check):')
    rb_30 = random_baseline_distribution(y, k=int(len(y)*0.3), n_trials=2000)
    print(f'  precision@30%: mean={rb_30["mean_precision_at_k"]:.3f}, p95={rb_30["p95_precision_at_k"]:.3f}')

    if 'anio_nacimiento' in ds.columns:
        ds_r = ds.reset_index(drop=True)
        X_r = ds_r[numeric_features + categorical_features].copy()
        y_r = ds_r['mean_future_ihm'].astype(float).values
        year_col = pd.to_numeric(ds_r['anio_nacimiento'], errors='coerce')
        tr_idx = ds_r.index[year_col <= 2020].tolist()
        te_idx = ds_r.index[year_col >= 2021].tolist()
        n_tr, n_te = len(tr_idx), len(te_idx)
        print(f'\n--- Temporal holdout (train ≤2020 n={n_tr}, test 2021-2022 n={n_te}) ---')
        if n_te >= 15:
            import sklearn.metrics as skm
            t_rows = []
            for name, pipe in build_models(numeric_features, categorical_features).items():
                try:
                    pipe.fit(X_r.iloc[tr_idx], y_r[tr_idx])
                    p = pipe.predict(X_r.iloc[te_idx])
                    reg = regression_metrics(y_r[te_idx], p)
                    sel = evaluate_selection(y_r[te_idx], p, k_fractions=[0.3]).iloc[0]
                    t_rows.append({'model': name, 'n_train': n_tr, 'n_test': n_te,
                                   'spearman': reg['spearman'], 'r2': reg['r2'],
                                   'rmse': reg['rmse'],
                                   'precision_at_0.3': sel['precision_at_k']})
                except Exception as e:
                    print(f'  {name}: {e}')
            tdf = pd.DataFrame(t_rows).sort_values('spearman', ascending=False)
            tdf.to_csv(out_tables / 'temporal_holdout_comparison.csv', index=False)
            print(tdf[['model', 'n_train', 'n_test', 'spearman', 'precision_at_0.3', 'r2']].to_string(index=False))
            print('\n  NOTE: test n is small — treat as directional. 5-fold CV std is primary.')
        else:
            print(f'  Skipped — fewer than 15 cows born 2021+ (got {n_te})')


def _heuristic_heaviest(ds):
    """Predict using only birth weight (or zeros if missing)."""
    return ds['peso_al_nacer'].fillna(0).values


def _heuristic_mother_ihm(ds):
    """Predict using only mother's mean IHM history."""
    return ds['madre_mean_ihm_pre'].fillna(ds['madre_mean_ihm_pre'].median() if ds['madre_mean_ihm_pre'].notna().any() else 0).values


def _heuristic_random(ds, seed=42):
    """Random ordering."""
    rng = np.random.default_rng(seed)
    return rng.standard_normal(len(ds))


if __name__ == '__main__':
    main()
