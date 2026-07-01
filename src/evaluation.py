"""
Evaluation: regression metrics, ranking metrics, and selection-based metrics.

Per Matteo's last email: precision@k and recall@k are the primary lens
because they correspond to the actual decision (the farm keeps the top k
animals from each cohort).
"""

from typing import List, Dict
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, roc_auc_score, f1_score
from scipy.stats import spearmanr


def regression_metrics(y_true, y_pred) -> Dict[str, float]:
    """Standard regression metrics."""
    return {
        'rmse':      float(np.sqrt(mean_squared_error(y_true, y_pred))),
        'mae':       float(mean_absolute_error(y_true, y_pred)),
        'r2':        float(r2_score(y_true, y_pred)),
        'spearman':  float(spearmanr(y_true, y_pred).correlation),
    }


def precision_recall_at_k(y_true, y_pred, k: int) -> Dict[str, float]:
    """Top-k selection metrics.

    Treat 'positive' as cows whose true mean_future_ihm is in the top-k of
    the true distribution. Compare against the model's top-k predictions.

    precision@k : of the k animals the model picks, how many are in the
                   true top-k?
    recall@k    : of the k true top-k animals, how many does the model find?
    (Note: precision@k == recall@k when both selection sizes equal k, so we
     only return one canonical value.)
    """
    n = len(y_true)
    k = min(k, n)
    if k == 0:
        return {'k': 0, 'precision_at_k': float('nan'),
                'recall_at_k': float('nan'), 'overlap': 0}

    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    true_topk = set(np.argsort(-y_true)[:k])
    pred_topk = set(np.argsort(-y_pred)[:k])
    overlap = len(true_topk & pred_topk)
    precision = overlap / k
    return {
        'k':              k,
        'precision_at_k': precision,
        'recall_at_k':    precision,
        'overlap':        overlap,
    }


def evaluate_selection(y_true, y_pred, k_fractions: List[float] = [0.3, 0.5]) -> pd.DataFrame:
    """Compute selection metrics at multiple k-fractions of the cohort."""
    n = len(y_true)
    rows = []
    for f in k_fractions:
        k = max(1, int(round(n * f)))
        m = precision_recall_at_k(y_true, y_pred, k)
        m['k_fraction'] = f
        rows.append(m)
    return pd.DataFrame(rows)


def mean_outcome_of_top_k(y_true, y_pred, k: int) -> float:
    """The mean true outcome among the model's top-k picks. Higher = better
    model, capped at the mean of the true top-k."""
    n = len(y_true)
    k = min(k, n)
    if k == 0:
        return float('nan')
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    pred_topk = np.argsort(-y_pred)[:k]
    return float(y_true[pred_topk].mean())


def classification_metrics_at_quartile(y_true, y_pred, quartile: float = 0.75) -> Dict[str, float]:
    """ROC-AUC and F1 treating the top quartile of true IHM as the positive class.

    This gives a classification view of the ranking problem: 'would the model
    correctly identify the top 25% most productive cows?'
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    threshold = np.quantile(y_true, quartile)
    y_binary = (y_true >= threshold).astype(int)
    if y_binary.sum() == 0 or y_binary.sum() == len(y_binary):
        return {'roc_auc': float('nan'), 'f1_top_quartile': float('nan')}
    roc_auc = float(roc_auc_score(y_binary, y_pred))
    k = y_binary.sum()
    pred_topk = set(np.argsort(-y_pred)[:k])
    y_pred_binary = np.zeros(len(y_pred), dtype=int)
    y_pred_binary[list(pred_topk)] = 1
    f1 = float(f1_score(y_binary, y_pred_binary, zero_division=0))
    return {'roc_auc': roc_auc, 'f1_top_quartile': f1}


def random_baseline_distribution(y_true, k: int, n_trials: int = 1000,
                                   random_state: int = 42) -> Dict[str, float]:
    """Sampling distribution for a random selection strategy.
    Useful as a sanity-check lower bound on precision@k."""
    rng = np.random.default_rng(random_state)
    n = len(y_true)
    y_true = np.asarray(y_true)
    true_topk = set(np.argsort(-y_true)[:k])
    overlaps = []
    for _ in range(n_trials):
        rand_pick = set(rng.choice(n, size=k, replace=False))
        overlaps.append(len(rand_pick & true_topk) / k)
    return {
        'mean_precision_at_k': float(np.mean(overlaps)),
        'std_precision_at_k':  float(np.std(overlaps)),
        'p95_precision_at_k':  float(np.quantile(overlaps, 0.95)),
    }
