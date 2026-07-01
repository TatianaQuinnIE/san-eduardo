"""
Reproducibility smoke check.

Runs every pipeline step in order and asserts the key outputs exist and
have the expected shape. This is what someone runs from a fresh clone to
verify the project actually works.

Failure here = grade = 0 per Matteo's warning. So we check this before
final submission.

Usage from project root:
    python scripts/check_reproducibility.py
"""

import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

import pandas as pd

ROOT = Path(__file__).parent.parent


def step(label, fn):
    print(f'\n=== {label} ===')
    try:
        fn()
        print(f'   ✓ ok')
        return True
    except AssertionError as e:
        print(f'   ✗ FAILED: {e}')
        return False
    except Exception as e:
        print(f'   ✗ ERROR: {type(e).__name__}: {e}')
        return False


def check_imports():
    """All key modules import without error."""
    sys.path.insert(0, str(ROOT))
    from src import load, clean, lineage, events, features, rules, models, evaluation, reproduction, supervised_v2, eda
    assert load and clean and lineage and events and features
    assert rules and models and evaluation and reproduction
    assert supervised_v2 and eda


def check_unit_tests():
    """All unit tests pass."""
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', 'tests/', '-q'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'pytest failed:\n{result.stdout}\n{result.stderr}'


def check_pipeline_v1():
    """build_processed.py runs without error and produces expected outputs."""
    result = subprocess.run(
        [sys.executable, 'scripts/build_processed.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'pipeline failed:\n{result.stderr}'
    expected = [
        'cow_registry.csv', 'lineage.csv', 'events.csv',
        'ihm_history.csv', 'outcomes.csv', 'supervised_dataset.csv',
        'rule_predictions_documented.csv',
    ]
    for fn in expected:
        path = ROOT / 'data' / 'processed' / fn
        assert path.exists(), f'missing {fn}'


def check_pipeline_v2():
    """build_processed_v2.py adds reproductive outputs."""
    result = subprocess.run(
        [sys.executable, 'scripts/build_processed_v2.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'v2 pipeline failed:\n{result.stderr}'
    for fn in ['reproduction_events.csv', 'reproduction_outcomes.csv',
               'cow_reproductive_summary.csv', 'supervised_dataset_v2.csv']:
        path = ROOT / 'data' / 'processed' / fn
        assert path.exists(), f'missing {fn}'


def check_supervised_shape():
    """Supervised dataset has the expected columns and reasonable size."""
    ds = pd.read_csv(ROOT / 'data' / 'processed' / 'supervised_dataset_v2.csv')
    assert len(ds) > 100, f'too few rows: {len(ds)}'
    required_cols = ['idv', 'mean_future_ihm', 'own_pregnancy_rate',
                     'composite_productivity', 'madre_mean_ihm_pre']
    for c in required_cols:
        assert c in ds.columns, f'missing column: {c}'
    trainable = ds[ds['mean_future_ihm'].notna()]
    assert len(trainable) > 50, f'too few trainable rows: {len(trainable)}'


def check_models():
    """run_models.py produces a comparison table."""
    result = subprocess.run(
        [sys.executable, 'scripts/run_models.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'modeling failed:\n{result.stderr}'
    comp = pd.read_csv(ROOT / 'outputs' / 'tables' / 'model_comparison.csv')
    assert len(comp) >= 7, f'expected 7+ models, got {len(comp)}'


def check_models_v2():
    """run_models_v2.py produces a multi-target comparison table."""
    result = subprocess.run(
        [sys.executable, 'scripts/run_models_v2.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'v2 modeling failed:\n{result.stderr}'
    comp = pd.read_csv(ROOT / 'outputs' / 'tables' / 'model_comparison_v2.csv')
    targets = comp['target'].unique()
    assert 'mean_future_ihm' in targets
    assert 'own_pregnancy_rate' in targets


def check_tuning():
    """tune_models.py produces best_hyperparameters.json."""
    result = subprocess.run(
        [sys.executable, 'scripts/tune_models.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'tuning failed:\n{result.stderr}'
    assert (ROOT / 'outputs' / 'tables' / 'best_hyperparameters.json').exists()


def check_shap():
    """run_shap.py generates SHAP plots."""
    result = subprocess.run(
        [sys.executable, 'scripts/run_shap.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'SHAP failed:\n{result.stderr}'
    assert (ROOT / 'outputs' / 'figures' / '09_shap_summary.png').exists()
    assert (ROOT / 'outputs' / 'figures' / '10_shap_beeswarm.png').exists()


def check_failure_cases():
    """run_failure_cases.py runs."""
    result = subprocess.run(
        [sys.executable, 'scripts/run_failure_cases.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'failure-cases failed:\n{result.stderr}'
    assert (ROOT / 'outputs' / 'tables' / 'largest_residuals.csv').exists()


def check_concept_drift():
    """run_concept_drift.py runs."""
    result = subprocess.run(
        [sys.executable, 'scripts/run_concept_drift.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'concept-drift failed:\n{result.stderr}'
    assert (ROOT / 'outputs' / 'tables' / 'concept_drift.csv').exists()


def check_figures():
    """make_figures.py generates the core figures."""
    result = subprocess.run(
        [sys.executable, 'scripts/make_figures.py'],
        cwd=ROOT, capture_output=True, text=True
    )
    assert result.returncode == 0, f'figures failed:\n{result.stderr}'


def main():
    checks = [
        ('imports',           check_imports),
        ('unit tests',        check_unit_tests),
        ('pipeline v1',       check_pipeline_v1),
        ('pipeline v2',       check_pipeline_v2),
        ('supervised shape',  check_supervised_shape),
        ('models v1',         check_models),
        ('models v2',         check_models_v2),
        ('tuning',            check_tuning),
        ('SHAP',              check_shap),
        ('failure cases',     check_failure_cases),
        ('concept drift',     check_concept_drift),
        ('figures',           check_figures),
    ]
    results = {}
    for name, fn in checks:
        results[name] = step(name, fn)

    failed = [n for n, ok in results.items() if not ok]
    print('\n' + '='*60)
    if failed:
        print(f'FAILED: {len(failed)} of {len(results)} checks')
        for f in failed:
            print(f'  ✗ {f}')
        sys.exit(1)
    else:
        print(f'ALL {len(results)} CHECKS PASSED')


if __name__ == '__main__':
    main()
