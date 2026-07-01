"""
Hyperparameter tuning via RandomizedSearchCV.

Why RandomizedSearchCV (not GridSearchCV):
  At our dataset size (337 trainable rows), exhaustive grid search would
  spend most of its budget on combinations that are obviously bad. Random
  search samples the space more efficiently and lets us cap the budget
  explicitly. The rubric accepts any of GridSearchCV / RandomizedSearchCV /
  BayesSearchCV — we choose Randomized.

Tuning budget: 30 candidate combinations × 5-fold CV = 150 fits per model.
At our scale, each fit is ~0.5 sec, so ~75 sec per model, ~5 min total.

We tune three of the substantive models:
  - Ridge          (one hyperparameter, alpha)
  - RandomForest   (key hyperparameters: n_estimators, max_depth, min_samples_leaf)
  - GradientBoost  (key hyperparameters: n_estimators, max_depth, learning_rate)

We do NOT tune Linear (no hyperparameters) or DecisionTree (single tree
mostly used for interpretability anchor, less worth tuning).

Output:
  outputs/tables/tuning_results.csv     all candidate scores per model
  outputs/tables/best_hyperparameters.json    the chosen params per model
"""

import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold, RandomizedSearchCV
from scipy.stats import loguniform, randint

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.models import build_models


def main():
    out_tables = ROOT / 'outputs' / 'tables'
    out_tables.mkdir(parents=True, exist_ok=True)

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

    X = ds[numeric_features + categorical_features]
    y = ds['mean_future_ihm'].astype(float).values

    print(f'Tuning on {len(ds)} rows. Target: mean_future_ihm.')
    print(f'  CV: 5-fold KFold (random_state=42)')
    print(f'  Budget: 30 candidates per model × 5 folds = 150 fits per model')

    models = build_models(numeric_features, categorical_features)
    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    # Hyperparameter spaces — documented choices, not defaults
    spaces = {
        'ridge': {
            # Ridge alpha: regularization strength. Wider range than default to
            # explore both very weak (linear-like) and strong regularization.
            'reg__alpha': loguniform(0.01, 100.0),
        },
        'random_forest': {
            'reg__n_estimators':       randint(100, 500),
            'reg__max_depth':          [3, 5, 8, 12, None],   # None = unrestricted
            'reg__min_samples_leaf':   randint(2, 20),
            'reg__max_features':       ['sqrt', 'log2', 1.0],
        },
        'gradient_boost': {
            'reg__n_estimators':       randint(50, 400),
            'reg__max_depth':          randint(2, 6),
            'reg__learning_rate':      loguniform(0.01, 0.3),
            'reg__subsample':          [0.7, 0.85, 1.0],
        },
    }

    all_results = []
    best_params = {}

    for name, space in spaces.items():
        print(f'\n=== Tuning {name} ===')
        pipe = models[name]
        search = RandomizedSearchCV(
            pipe,
            param_distributions=space,
            n_iter=30,
            cv=cv,
            scoring='r2',           # primary metric; we'll re-evaluate selection metrics later
            n_jobs=-1,
            random_state=42,
            return_train_score=True,
        )
        search.fit(X, y)

        cv_results = pd.DataFrame(search.cv_results_)
        cv_results['model'] = name
        # Keep the columns we'll inspect later
        keep_cols = ['model', 'mean_test_score', 'std_test_score',
                     'mean_train_score', 'rank_test_score', 'params']
        all_results.append(cv_results[keep_cols])

        best_params[name] = {
            'params': {k.replace('reg__', ''): _to_native(v)
                       for k, v in search.best_params_.items()},
            'best_cv_r2':       float(search.best_score_),
            'best_cv_r2_std':   float(search.cv_results_['std_test_score']
                                      [search.best_index_]),
        }
        print(f'  best CV R²:  {search.best_score_:.4f} '
              f'± {search.cv_results_["std_test_score"][search.best_index_]:.4f}')
        print(f'  best params: {best_params[name]["params"]}')

    # Save outputs
    pd.concat(all_results, ignore_index=True).to_csv(
        out_tables / 'tuning_results.csv', index=False
    )
    with open(out_tables / 'best_hyperparameters.json', 'w') as f:
        json.dump(best_params, f, indent=2)

    print('\nTuning complete.')
    print(f'  results: outputs/tables/tuning_results.csv')
    print(f'  best params: outputs/tables/best_hyperparameters.json')


def _to_native(v):
    """JSON-serializable form for numpy/sklearn types."""
    if isinstance(v, (np.integer, int)): return int(v)
    if isinstance(v, (np.floating, float)): return float(v)
    if isinstance(v, np.ndarray): return v.tolist()
    return v


if __name__ == '__main__':
    main()
