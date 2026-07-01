"""
Modelo 2 — Forward predictions for the 2027 heifer cohort.

Applies the tuned Gradient Boosting model (trained on 2018-2022 cows with adult IHM)
to the 405 heifers born in 2025 who will be selected in 2027.

This is a genuine out-of-sample prediction: no adult IHM exists for these animals yet.
The prediction will be verifiable when the farmer completes the 2027 selection.

Also applies the documented verdes rule to each heifer using available data.

Output:
  outputs/tables/model2_predictions_2027.csv
"""

import json
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.load import load_all_sources
from src.lineage import build_cow_registry
from src.features import build_ihm_history, mother_ihm_at_selection, sire_average_outcome
from src.models import build_models
from src.clean import normalize_idv_column, normalize_tipo_padre, to_proportion
from src.rules import apply_verdes_rule, VERDES_THRESHOLDS_DOCUMENTED


def build_2027_cohort_features(sources, registry, ihm_history):
    """Build selection-time features for the 2027 cohort heifers."""
    t27 = sources['terneras_2027'].copy()

    # Normalise IDV
    t27['idv'] = normalize_idv_column(t27['IDV'])
    heifers = t27[t27['Sexo'] == 'Hembra'][['idv']].drop_duplicates()

    # Filter registry to just these heifers (born 2025, selection year 2027)
    reg_2027 = registry[registry['idv'].isin(heifers['idv'])].copy()
    print(f"  Heifers in registry: {len(reg_2027)}")
    print(f"  With anio_nacimiento: {reg_2027['anio_nacimiento'].notna().sum()}")
    print(f"  With madre_idv: {reg_2027['madre_idv'].notna().sum()}")
    print(f"  With tipo_padre: {reg_2027['tipo_padre'].notna().sum()}")

    # Mother IHM features (leakage-safe: IHM strictly before 2027)
    mom_feat = mother_ihm_at_selection(ihm_history, registry, selection_year_offset=2)
    mom_feat = mom_feat[mom_feat['idv'].isin(heifers['idv'])]
    print(f"  With madre_mean_ihm_pre: {mom_feat['madre_mean_ihm_pre'].notna().sum()} / {len(mom_feat)}")

    # Sire features
    sire_feat = sire_average_outcome(ihm_history, registry)
    sire_feat = sire_feat[sire_feat['idv'].isin(heifers['idv'])]

    # Assemble feature matrix
    df = (reg_2027[['idv', 'anio_nacimiento', 'peso_al_nacer',
                     'pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion',
                     'madre_idv', 'nombre_padre']]
          .merge(mom_feat.drop(columns='madre_idv', errors='ignore'), on='idv', how='left')
          .merge(sire_feat, on='idv', how='left'))

    return df


def build_rule_inputs_2027(sources, registry, ihm_history):
    """Build inputs for the documented verdes rule for the 2027 cohort."""
    t27 = sources['terneras_2027'].copy()
    t27['idv'] = normalize_idv_column(t27['IDV'])
    t27 = t27[t27['Sexo'] == 'Hembra'].copy()

    p27 = sources['peso_terneros_2027'].copy()
    p27['idv'] = normalize_idv_column(p27['IDV'])
    p27 = p27[p27['Sexo'] == 'Hembra'].copy()

    # Use raw weaning weight for the rule threshold (190 kg was set for raw destete weight)
    p27['peso_destete'] = pd.to_numeric(p27['Peso Destete'], errors='coerce')
    # Store 205-day adjusted weight separately for reference
    p27['peso_205d'] = pd.to_numeric(p27['Peso 205 días'], errors='coerce')

    # Build rule input table
    reg_cols = registry[['idv', 'madre_idv', 'tipo_padre']].copy()

    out = (p27[['idv', 'peso_destete', 'peso_205d']]
           .merge(reg_cols, on='idv', how='left'))

    out['madre_conocida'] = out['madre_idv'].notna()
    out['padre_conocido'] = out['tipo_padre'].notna() & (out['tipo_padre'] != 'desconocido')
    out['padre_iatf'] = out['tipo_padre'] == 'iatf'

    # Most recent mother IHM strictly before 2027
    real_ihm = ihm_history[ihm_history['ihm'].notna() & (ihm_history['ihm'] > 0)]
    ihm_pre2027 = real_ihm[real_ihm['year'] < 2027]
    latest_madre_ihm = (ihm_pre2027.sort_values('year')
                        .groupby('idv')['ihm'].last()
                        .reset_index()
                        .rename(columns={'idv': 'madre_idv', 'ihm': 'ihm_madre'}))

    out = out.merge(latest_madre_ihm, on='madre_idv', how='left')
    return out


def main():
    out_dir = ROOT / 'outputs' / 'tables'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('Loading sources...')
    sources = load_all_sources(ROOT / 'data' / 'raw')
    registry = build_cow_registry(sources)
    ihm_history = build_ihm_history(sources)

    print('\nBuilding 2027 cohort features...')
    cohort = build_2027_cohort_features(sources, registry, ihm_history)

    # Train on the full supervised dataset (337 cows with adult IHM)
    print('\nLoading training data...')
    ds_train = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset_v2.csv')
    ds_train = ds_train[ds_train['mean_future_ihm'].notna()].copy()
    print(f'  Training cows: {len(ds_train)}')

    numeric_features = [
        'anio_nacimiento', 'peso_al_nacer',
        'madre_n_ihm_pre', 'madre_mean_ihm_pre',
        'madre_max_ihm_pre', 'madre_latest_ihm_pre',
        'sire_n_prior_daughters_observed', 'sire_mean_daughter_ihm_prior',
    ]
    categorical_features = ['pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion']
    numeric_features = [c for c in numeric_features if c in ds_train.columns]
    categorical_features = [c for c in categorical_features if c in ds_train.columns]

    # Load tuned hyperparameters
    best_path = ROOT / 'outputs' / 'tables' / 'best_hyperparameters.json'
    models = build_models(numeric_features, categorical_features)
    pipe = models['gradient_boost']
    if best_path.exists():
        with open(best_path) as f:
            gb_params = json.load(f)['gradient_boost']['params']
        pipe.set_params(**{f'reg__{k}': v for k, v in gb_params.items()})

    X_train = ds_train[numeric_features + categorical_features]
    y_train = ds_train['mean_future_ihm'].astype(float).values
    pipe.fit(X_train, y_train)
    print('  Model trained.')

    # Predict on 2027 cohort
    X_2027 = cohort[numeric_features + categorical_features]
    cohort['model_predicted_ihm'] = pipe.predict(X_2027)

    # Rank within cohort
    cohort['rank'] = cohort['model_predicted_ihm'].rank(ascending=False, method='min').astype(int)
    cohort['top_30pct'] = cohort['model_predicted_ihm'] >= cohort['model_predicted_ihm'].quantile(0.70)
    cohort['top_50pct'] = cohort['model_predicted_ihm'] >= cohort['model_predicted_ihm'].quantile(0.50)

    print(f'\n  Predictions generated for {len(cohort)} heifers')
    print(f'  IHM predicted: mean={cohort["model_predicted_ihm"].mean():.3f}, '
          f'range={cohort["model_predicted_ihm"].min():.3f}–{cohort["model_predicted_ihm"].max():.3f}')

    # Apply documented rule
    print('\nApplying documented rule to 2027 cohort...')
    rule_inputs = build_rule_inputs_2027(sources, registry, ihm_history)
    rule_inputs['rule_prediction'] = rule_inputs.apply(
        lambda r: apply_verdes_rule(r, thresholds=VERDES_THRESHOLDS_DOCUMENTED), axis=1
    )
    print('  Rule distribution:')
    print(rule_inputs['rule_prediction'].value_counts().to_string())

    # Join model + rule
    result = (cohort[['idv', 'anio_nacimiento', 'madre_idv', 'nombre_padre',
                       'tipo_padre', 'pelaje', 'rodeo_nacimiento',
                       'madre_mean_ihm_pre', 'madre_max_ihm_pre',
                       'model_predicted_ihm', 'rank', 'top_30pct', 'top_50pct']]
              .merge(rule_inputs[['idv', 'peso_destete', 'peso_205d', 'ihm_madre',
                                   'madre_conocida', 'padre_iatf', 'rule_prediction']],
                     on='idv', how='left'))

    result = result.sort_values('rank')
    result.to_csv(out_dir / 'model2_predictions_2027.csv', index=False)
    print(f'\nSaved → {out_dir / "model2_predictions_2027.csv"}')
    print(f'  {len(result)} heifers scored and ranked.')
    print(f'  Top-30% (recommended by model): {result["top_30pct"].sum()} heifers')
    print(f'  Rule predicts verdes_3: {(result["rule_prediction"]=="verdes_3").sum()} heifers')
    print(f'  Both model top-30% AND rule verdes_3: '
          f'{((result["top_30pct"]) & (result["rule_prediction"]=="verdes_3")).sum()} heifers')


if __name__ == '__main__':
    main()
