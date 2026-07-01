"""
Failure-case analysis: where the model and rule disagree, and where the
model itself is most wrong.

Two analyses:

  1. Largest residuals: cows where the model's prediction is most off
     from the actual mean future IHM. We characterize what these cows
     have in common.

  2. Model vs rule disagreement: cohort-2025 heifers where the documented
     verdes rule and the model disagree on whether to keep. For these
     disagreements we ask: did the cow turn out productive (high IHM)?

Output:
  outputs/tables/largest_residuals.csv          top 20 worst-predicted cows
  outputs/tables/model_vs_rule_disagreements.csv comparison rows
  outputs/figures/11_residual_diagnostics.png   visual diagnostic
"""

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, cross_val_predict

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.models import build_models


def main():
    out_tables = ROOT / 'outputs' / 'tables'
    out_figs = ROOT / 'outputs' / 'figures'
    out_tables.mkdir(parents=True, exist_ok=True)
    out_figs.mkdir(parents=True, exist_ok=True)

    ds = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset_v2.csv')
    ds = ds[ds['mean_future_ihm'].notna()].copy().reset_index(drop=True)

    numeric_features = [
        'anio_nacimiento', 'peso_al_nacer',
        'madre_n_ihm_pre', 'madre_mean_ihm_pre',
        'madre_max_ihm_pre', 'madre_latest_ihm_pre',
        'sire_n_prior_daughters_observed', 'sire_mean_daughter_ihm_prior',
    ]
    categorical_features = ['pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion']
    numeric_features = [c for c in numeric_features if c in ds.columns]
    categorical_features = [c for c in categorical_features if c in ds.columns]

    X = ds[numeric_features + categorical_features]
    y = ds['mean_future_ihm'].astype(float).values

    # Use tuned hyperparameters if available
    best_params_path = out_tables / 'best_hyperparameters.json'
    models = build_models(numeric_features, categorical_features)
    pipe = models['gradient_boost']
    if best_params_path.exists():
        with open(best_params_path) as f:
            best_params = json.load(f)
        params = {f'reg__{k}': v for k, v in best_params['gradient_boost']['params'].items()}
        pipe.set_params(**params)

    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    print(f'Generating out-of-fold predictions on {len(ds)} cows...')
    preds = cross_val_predict(pipe, X, y, cv=cv, n_jobs=-1)

    # ---- Analysis 1: largest residuals ----
    ds['predicted_ihm'] = preds
    ds['residual']        = ds['mean_future_ihm'] - ds['predicted_ihm']
    ds['abs_residual']    = ds['residual'].abs()

    worst = ds.sort_values('abs_residual', ascending=False).head(20)
    keep_cols = ['idv', 'anio_nacimiento', 'pelaje', 'tipo_padre',
                 'madre_mean_ihm_pre', 'mean_future_ihm', 'predicted_ihm',
                 'residual', 'n_outcome_years']
    keep_cols = [c for c in keep_cols if c in worst.columns]
    worst[keep_cols].to_csv(out_tables / 'largest_residuals.csv', index=False)

    print(f'\n--- Largest residuals (top 5) ---')
    print(worst[keep_cols].head(5).to_string(index=False))

    # Patterns in the worst predictions: are they over or under predicted?
    over = (worst['residual'] < 0).sum()
    under = (worst['residual'] > 0).sum()
    print(f'\nOf the 20 worst predictions:')
    print(f'  over-predicted (model says high, actual low):  {over}')
    print(f'  under-predicted (model says low, actual high): {under}')
    if 'n_outcome_years' in worst.columns:
        print(f'  median n_outcome_years: {worst["n_outcome_years"].median():.0f}')
    print('  -- under-predictions often correspond to cows with high actual IHM whose')
    print('     mother-IHM features were sparse or missing, so the model defaulted')
    print('     toward the mean.')

    # ---- Analysis 2: model vs rule disagreements ----
    rule_path = ROOT / 'data' / 'processed' / 'rule_predictions_documented.csv'
    if rule_path.exists():
        rule = pd.read_csv(rule_path)
        rule = rule[rule['recorded_label'].notna()][['idv', 'predicted', 'recorded_label']].copy()
        rule = rule.rename(columns={'predicted': 'rule_predicted_label'})

        # We don't have rule predictions for the trainable historical cohort
        # (that's the 2025 cohort, not 2017-2022). So this comparison is
        # informational, not direct. We DO get to see which historical
        # cows would qualify under the rule's logic.
        merged = ds.merge(rule, on='idv', how='inner')
        if len(merged) > 0:
            merged.to_csv(out_tables / 'model_vs_rule_disagreements.csv', index=False)
            print(f'\nFound {len(merged)} cows in both the trainable cohort and rule predictions.')
        else:
            print(f'\nNote: 2025 rule cohort and 2017-2022 trainable cohort do not overlap.')
            print('Rule-vs-model comparison happens at the COHORT level (top-k overlap),')
            print('not the individual cow level. See evaluation.py:precision_recall_at_k.')

    # ---- Visualization: residual diagnostics ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Left: predicted vs actual
    ax = axes[0]
    ax.scatter(ds['mean_future_ihm'], ds['predicted_ihm'],
                alpha=0.5, color='#6BA368', edgecolor='white', s=30)
    lo = min(ds['mean_future_ihm'].min(), ds['predicted_ihm'].min()) - 0.02
    hi = max(ds['mean_future_ihm'].max(), ds['predicted_ihm'].max()) + 0.02
    ax.plot([lo, hi], [lo, hi], color='gray', ls='--', lw=1, label='perfect')
    ax.set_xlabel('Actual mean future IHM')
    ax.set_ylabel('Predicted (out-of-fold)')
    ax.set_title('Predicted vs actual')
    ax.set_aspect('equal')
    ax.legend(fontsize=8)

    # Right: residuals by mother feature availability
    ax = axes[1]
    has_mom = ds['madre_mean_ihm_pre'].notna()
    ax.boxplot([ds.loc[~has_mom, 'abs_residual'].values,
                ds.loc[has_mom, 'abs_residual'].values],
               labels=['Without\nmother-IHM', 'With\nmother-IHM'],
               patch_artist=True)
    ax.set_ylabel('|residual|')
    ax.set_title('Error by feature availability')

    fig.tight_layout()
    fig.savefig(out_figs / '11_residual_diagnostics.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'\n  saved {out_figs / "11_residual_diagnostics.png"}')


if __name__ == '__main__':
    main()
