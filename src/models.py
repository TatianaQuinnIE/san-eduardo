"""
Model definitions for the supervised regression on mean future IHM.

Per project guidance:
  - Single training objective: regression on mean_future_ihm
  - Start with simple, interpretable models (Linear, Ridge, Decision Tree)
  - Tree ensembles (RandomForest, GradientBoosting) as upper-bound checks
  - No neural networks (data too small, too tabular)
  - Report uncertainty via cross-validation variance and bootstrap

All models live inside an sklearn Pipeline so preprocessing is fit only on
the training fold (no leakage into the test set).
"""

from typing import Dict
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.dummy import DummyRegressor


# Features explicitly dropped from the modeling pipeline.
# `peso_al_nacer` is constant at 30.0 kg for every cow in the 2017-2022
# supervised window — a documented default fill value in the older registry,
# not a real per-cow measurement. Documented in notebook section 4.5.
DROP_FEATURES = ['peso_al_nacer']


def make_preprocessor(numeric_features, categorical_features):
    """Standard preprocessing: median-impute + scale numerics; mode-impute +
    one-hot encode categoricals.

    Defensively filters out anything in DROP_FEATURES so that constant or
    sentinel-valued features cannot accidentally leak into the model.
    """
    # Defensive filter: even if a caller forgets to remove dropped features,
    # we filter them here so the model is never trained on them.
    numeric_features = [f for f in numeric_features if f not in DROP_FEATURES]
    categorical_features = [f for f in categorical_features if f not in DROP_FEATURES]

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler',  StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='constant', fill_value='__missing__')),
        ('onehot',  OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])
    return ColumnTransformer([
        ('num', numeric_transformer,     numeric_features),
        ('cat', categorical_transformer, categorical_features),
    ], remainder='drop')


def build_models(numeric_features, categorical_features, random_state=42) -> Dict[str, Pipeline]:
    """Return a dict of name → fitted sklearn Pipeline for each candidate model."""
    pre = lambda: make_preprocessor(numeric_features, categorical_features)

    return {
        # Trivial baselines (don't even use features)
        'baseline_mean': Pipeline([
            ('pre',  pre()),
            ('reg',  DummyRegressor(strategy='mean')),
        ]),
        # Real models
        'linear': Pipeline([
            ('pre',  pre()),
            ('reg',  LinearRegression()),
        ]),
        'ridge': Pipeline([
            ('pre',  pre()),
            ('reg',  Ridge(alpha=1.0, random_state=random_state)),
        ]),
        'decision_tree': Pipeline([
            ('pre',  pre()),
            ('reg',  DecisionTreeRegressor(max_depth=5, min_samples_leaf=10,
                                           random_state=random_state)),
        ]),
        'random_forest': Pipeline([
            ('pre',  pre()),
            ('reg',  RandomForestRegressor(n_estimators=200, max_depth=8,
                                           min_samples_leaf=5,
                                           random_state=random_state, n_jobs=-1)),
        ]),
        'gradient_boost': Pipeline([
            ('pre',  pre()),
            ('reg',  GradientBoostingRegressor(n_estimators=200, max_depth=3,
                                                learning_rate=0.05,
                                                random_state=random_state)),
        ]),
    }