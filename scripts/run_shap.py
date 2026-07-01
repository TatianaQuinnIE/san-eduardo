"""
SHAP feature importance for the best model.

We fit the tuned best model on the full supervised dataset and compute
SHAP values to understand which features the model is actually relying on.

Generates two plots:
  outputs/figures/09_shap_summary.png    bar plot, mean |SHAP| per feature
  outputs/figures/10_shap_beeswarm.png   beeswarm: distribution of impacts

Implementation notes:
  - We use TreeExplainer for the gradient-boosted model (fast, exact)
  - We compute SHAP on the full dataset, not just CV folds, since this is
    interpretation of the model we'd actually deploy
  - The model is fit on imputed features (median for numeric, mode for
    categorical) to avoid SHAP failing on NaNs
"""

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.models import build_models


def main():
    out_figs = ROOT / 'outputs' / 'figures'
    out_figs.mkdir(parents=True, exist_ok=True)

    ds = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset_v2.csv')
    ds = ds[ds['mean_future_ihm'].notna()].copy()

    numeric_features = [
        'anio_nacimiento', 'peso_al_nacer',
        'madre_n_ihm_pre', 'madre_mean_ihm_pre',
        'madre_max_ihm_pre', 'madre_latest_ihm_pre',
        'sire_n_prior_daughters_observed', 'sire_mean_daughter_ihm_prior',
    ]
    categorical_features = ['pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion']
    numeric_features = [c for c in numeric_features if c in ds.columns]
    categorical_features = [c for c in categorical_features if c in ds.columns]

    # Load tuned hyperparameters if available, otherwise use defaults
    best_params_path = ROOT / 'outputs' / 'tables' / 'best_hyperparameters.json'
    if best_params_path.exists():
        with open(best_params_path) as f:
            best_params = json.load(f)
        gb_params = best_params['gradient_boost']['params']
        print(f'Using tuned gradient_boost params: {gb_params}')
    else:
        gb_params = {}
        print('Tuning results not found — using defaults. Run scripts/tune_models.py first.')

    # Build the gradient_boost pipeline; refit with tuned params
    models = build_models(numeric_features, categorical_features)
    pipe = models['gradient_boost']
    if gb_params:
        # Translate flat dict back to pipeline param names
        params = {f'reg__{k}': v for k, v in gb_params.items()}
        pipe.set_params(**params)

    X = ds[numeric_features + categorical_features]
    y = ds['mean_future_ihm'].astype(float).values

    print(f'Fitting on {len(ds)} rows...')
    pipe.fit(X, y)

    # Apply preprocessing to get transformed features for SHAP
    pre = pipe.named_steps['pre']
    reg = pipe.named_steps['reg']
    X_transformed = pre.transform(X)

    # Derive feature names from the fitted preprocessor so they always match
    # X_transformed exactly. The preprocessor silently drops DROP_FEATURES
    # (e.g. peso_al_nacer), so building feat_names from the original input
    # lists produces a length mismatch with shap_values.
    raw_names = pre.get_feature_names_out()
    feat_names = [n.split('__', 1)[-1] for n in raw_names]

    print(f'Transformed feature dimensionality: {X_transformed.shape}')
    print('Computing SHAP values (TreeExplainer)...')
    explainer = shap.TreeExplainer(reg)
    shap_values = explainer.shap_values(X_transformed)

    # Summary bar plot — mean |SHAP|
    print('Generating summary plot...')
    plt.figure(figsize=(8, 6))
    shap.summary_plot(shap_values, X_transformed, feature_names=feat_names,
                       plot_type='bar', show=False, max_display=15)
    plt.title('Mean |SHAP| per feature — what does the model rely on?', fontsize=11)
    plt.tight_layout()
    plt.savefig(out_figs / '09_shap_summary.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  saved {out_figs / "09_shap_summary.png"}')

    # Beeswarm — distribution of impact
    plt.figure(figsize=(9, 6))
    shap.summary_plot(shap_values, X_transformed, feature_names=feat_names,
                       show=False, max_display=15)
    plt.title('SHAP value distribution — direction and spread of feature impact', fontsize=11)
    plt.tight_layout()
    plt.savefig(out_figs / '10_shap_beeswarm.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f'  saved {out_figs / "10_shap_beeswarm.png"}')

    # Save the importance ranking as a CSV too
    mean_abs = np.abs(shap_values).mean(axis=0)
    importance = (pd.DataFrame({'feature': feat_names, 'mean_abs_shap': mean_abs})
                    .sort_values('mean_abs_shap', ascending=False))
    importance.to_csv(ROOT / 'outputs' / 'tables' / 'shap_feature_importance.csv',
                       index=False)
    print(f'\nTop 10 features by mean |SHAP|:')
    print(importance.head(10).to_string(index=False))


if __name__ == '__main__':
    main()
