"""Generate all figures for poster, slides, and report.

Run from project root:
    python scripts/make_figures.py
"""

import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import learning_curve

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

PROCESSED = ROOT / 'data' / 'processed'
TABLES = ROOT / 'outputs' / 'tables'
FIGS = ROOT / 'outputs' / 'figures'
FIGS.mkdir(parents=True, exist_ok=True)

mpl.rcParams['font.size'] = 10
mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False

GREEN = '#6BA368'
ORANGE = '#E89B3C'
RED = '#C8553D'
BLUE = '#4F7CAC'
GRAY = '#808080'
GOLD = '#D4A017'


def main():
    ihm_history = pd.read_csv(PROCESSED / 'ihm_history.csv')
    outcomes = pd.read_csv(PROCESSED / 'outcomes.csv')
    rule_doc = pd.read_csv(PROCESSED / 'rule_predictions_documented.csv')
    supervised = pd.read_csv(PROCESSED / 'supervised_dataset.csv')
    registry = pd.read_csv(PROCESSED / 'cow_registry.csv')
    events = pd.read_csv(PROCESSED / 'events.csv')

    fig_01_ihm_distribution(ihm_history)
    fig_02_outcome_richness(outcomes)
    fig_03_rule_confusion(rule_doc)
    fig_04_class_vs_mother_ihm(rule_doc)
    fig_05_cohort_sizes(registry)
    fig_06_event_summary(events)

    if (TABLES / 'model_comparison.csv').exists():
        comp = pd.read_csv(TABLES / 'model_comparison.csv')
        fig_07_model_comparison(comp)

    if (TABLES / 'cv_predictions.csv').exists():
        cv = pd.read_csv(TABLES / 'cv_predictions.csv')
        fig_08_predicted_vs_actual(cv)
        fig_13_roc_curve(cv)

    fig_14_learning_curves(supervised)

    print(f'\nAll figures saved to {FIGS}')


def fig_01_ihm_distribution(ihm_history):
    real = ihm_history[ihm_history['ihm'] > 0]
    years = sorted(real['year'].unique())
    fig, axes = plt.subplots(1, len(years), figsize=(2.8*len(years), 3.5),
                              sharey=True)
    if len(years) == 1:
        axes = [axes]
    for ax, year in zip(axes, years):
        s = real[real['year'] == year]['ihm']
        ax.hist(s, bins=25, color=GREEN, edgecolor='white', alpha=0.85)
        ax.axvline(0.40, color=RED, ls='--', lw=1.4, label='40% threshold')
        ax.set_title(f'{year}\n(n={len(s)})')
        ax.set_xlabel('IHM')
        ax.set_xlim(0.1, 0.7)
        if ax is axes[0]:
            ax.legend(fontsize=8, loc='upper left')
            ax.set_ylabel('# observations')
    fig.suptitle('IHM distribution by year', y=1.02)
    fig.tight_layout()
    fig.savefig(FIGS / '01_ihm_distribution.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  01_ihm_distribution.png')


def fig_02_outcome_richness(outcomes):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    counts = outcomes['n_outcome_years'].value_counts().sort_index()
    bars = ax.bar(counts.index, counts.values, color=BLUE, edgecolor='white')
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width()/2, v + 5, str(v),
                ha='center', va='bottom', fontsize=9)
    ax.set_xlabel('# adult IHM years per cow')
    ax.set_ylabel('# cows')
    ax.set_title("Outcome richness — how many years of adult IHM per cow?")
    ax.set_xticks(counts.index)
    fig.tight_layout()
    fig.savefig(FIGS / '02_outcome_richness.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  02_outcome_richness.png')


def fig_03_rule_confusion(rule_doc):
    df = rule_doc[rule_doc['recorded_label'].notna()].copy()
    labels_r = sorted(df['recorded_label'].unique())
    labels_p = sorted(df['predicted'].unique())
    cm = pd.crosstab(df['recorded_label'], df['predicted']).reindex(
        index=labels_r, columns=labels_p, fill_value=0)
    match_rate = (df['predicted'] == df['recorded_label']).mean() * 100

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(cm.values, cmap='Greens', aspect='auto')
    ax.set_xticks(range(len(labels_p)))
    ax.set_xticklabels(labels_p, rotation=30, ha='right', fontsize=8)
    ax.set_yticks(range(len(labels_r)))
    ax.set_yticklabels(labels_r, fontsize=8)
    ax.set_xlabel('Predicted by documented rule')
    ax.set_ylabel('Actual recorded label')
    ax.set_title(f'Documented rule reproduces only {match_rate:.0f}% of farm decisions\n'
                 f'top tier perfect, lower tiers diverge → unwritten criteria exist')
    for i in range(len(labels_r)):
        for j in range(len(labels_p)):
            v = cm.values[i, j]
            if v > 0:
                ax.text(j, i, str(v), ha='center', va='center',
                        color='white' if v > cm.values.max()*0.4 else 'black',
                        fontsize=10, fontweight='bold')
    fig.tight_layout()
    fig.savefig(FIGS / '03_rule_confusion.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  03_rule_confusion.png')


def fig_04_class_vs_mother_ihm(rule_doc):
    df = rule_doc[rule_doc['ihm_madre'].notna() &
                   rule_doc['recorded_label'].notna()].copy()
    order = ['verdes_3', 'verdes_2', 'verdes_1', 'verdes_venta']
    order = [o for o in order if o in df['recorded_label'].unique()]
    data = [df[df['recorded_label'] == o]['ihm_madre'].values for o in order]

    fig, ax = plt.subplots(figsize=(7, 4))
    bp = ax.boxplot(data, labels=order, patch_artist=True, widths=0.55)
    colors = [GREEN, '#A4C77F', '#D9D266', GRAY]
    for patch, c in zip(bp['boxes'], colors[:len(order)]):
        patch.set_facecolor(c)
        patch.set_alpha(0.75)
    ax.axhline(0.40, color=RED, ls='--', lw=1, alpha=0.7, label='40% threshold')
    ax.set_ylabel("Mother's most recent IHM")
    ax.set_xlabel("Recorded class label (2025 cohort)")
    ax.set_title("Class label vs. mother's IHM:\ndirectional but noisy → ML may add value")
    ax.legend(fontsize=8)
    plt.xticks(rotation=15, ha='right')
    fig.tight_layout()
    fig.savefig(FIGS / '04_class_vs_mother_ihm.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  04_class_vs_mother_ihm.png')


def fig_05_cohort_sizes(registry):
    ay = registry['anio_nacimiento'].dropna().astype(int).value_counts().sort_index()
    ay = ay[ay.index.isin(range(2010, 2028))]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.bar(ay.index, ay.values, color=BLUE, edgecolor='white')
    for x, v in zip(ay.index, ay.values):
        ax.text(x, v + 5, str(v), ha='center', va='bottom', fontsize=8)
    ax.set_xlabel('Birth year')
    ax.set_ylabel('# cows in registry')
    ax.set_title('Cohort sizes by birth year')
    fig.tight_layout()
    fig.savefig(FIGS / '05_cohort_sizes.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  05_cohort_sizes.png')


def fig_06_event_summary(events):
    counts = events['event_type'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.barh(counts.index[::-1], counts.values[::-1], color=ORANGE, edgecolor='white')
    for i, v in enumerate(counts.values[::-1]):
        ax.text(v + 5, i, str(v), va='center', fontsize=9)
    ax.set_xlabel('# events')
    ax.set_title('Event log: WhatsApp + IATF sessions')
    fig.tight_layout()
    fig.savefig(FIGS / '06_event_summary.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  06_event_summary.png')


def fig_07_model_comparison(comp):
    comp = comp.copy().sort_values('precision_at_0.3', ascending=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    colors = [GREEN if 'random_forest' in m or 'gradient' in m or 'tree' in m
              else BLUE if 'linear' in m or 'ridge' in m
              else GRAY for m in comp['model']]

    axes[0].barh(comp['model'], comp['precision_at_0.3'], color=colors, edgecolor='white')
    axes[0].axvline(0.30, color=RED, ls='--', lw=1, label='Random baseline (~0.30)')
    axes[0].set_xlabel('Precision @ top 30%')
    axes[0].set_title('Selection precision: model vs heuristic baselines')
    axes[0].legend(fontsize=8)

    axes[1].barh(comp['model'], comp['spearman'], color=colors, edgecolor='white')
    axes[1].axvline(0, color='black', ls='-', lw=0.5)
    axes[1].set_xlabel('Spearman ρ vs true future IHM')
    axes[1].set_title('Ranking quality')

    fig.tight_layout()
    fig.savefig(FIGS / '07_model_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  07_model_comparison.png')


def fig_08_predicted_vs_actual(cv):
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    if 'pred_random_forest' in cv.columns:
        ax.scatter(cv['y_true'], cv['pred_random_forest'],
                    alpha=0.5, color=GREEN, edgecolor='white', s=30)
    lo = min(cv['y_true'].min(), cv['pred_random_forest'].min()) - 0.02
    hi = max(cv['y_true'].max(), cv['pred_random_forest'].max()) + 0.02
    ax.plot([lo, hi], [lo, hi], color=GRAY, ls='--', lw=1, label='perfect prediction')
    ax.set_xlabel('Actual mean future IHM')
    ax.set_ylabel('Predicted mean future IHM (5-fold CV, Random Forest)')
    ax.set_title('Predicted vs actual — out-of-fold cross-validation')
    ax.legend(fontsize=8)
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(FIGS / '08_predicted_vs_actual.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  08_predicted_vs_actual.png')


def fig_13_roc_curve(cv):
    """ROC curve for top-quartile classification using CV predictions."""
    if 'pred_random_forest' not in cv.columns:
        return
    y_true = cv['y_true'].values
    threshold = np.quantile(y_true, 0.75)
    y_binary = (y_true >= threshold).astype(int)

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    model_cols = [c for c in cv.columns if c.startswith('pred_')]
    palette = [GREEN, BLUE, ORANGE, RED, GRAY, GOLD]
    for col, color in zip(model_cols, palette):
        fpr, tpr, _ = roc_curve(y_binary, cv[col].values)
        roc_auc = auc(fpr, tpr)
        label = col.replace('pred_', '').replace('_', ' ')
        ax.plot(fpr, tpr, color=color, lw=1.8, label=f'{label} (AUC={roc_auc:.2f})')
    ax.plot([0, 1], [0, 1], color=GRAY, ls='--', lw=1, label='random')
    ax.set_xlabel('False positive rate')
    ax.set_ylabel('True positive rate')
    ax.set_title('ROC curve — top-quartile IHM identification\n(5-fold CV out-of-fold predictions)')
    ax.legend(fontsize=8, loc='lower right')
    fig.tight_layout()
    fig.savefig(FIGS / '13_roc_curve.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  13_roc_curve.png')


def fig_14_learning_curves(supervised):
    """Learning curves for random forest — diagnoses bias vs variance."""
    ds = supervised[supervised['mean_future_ihm'].notna()].copy()
    if len(ds) < 50:
        return

    numeric_features = [c for c in [
        'anio_nacimiento', 'peso_al_nacer', 'madre_n_ihm_pre',
        'madre_mean_ihm_pre', 'madre_max_ihm_pre', 'madre_latest_ihm_pre',
        'sire_n_prior_daughters_observed', 'sire_mean_daughter_ihm_prior',
    ] if c in ds.columns]
    categorical_features = [c for c in [
        'pelaje', 'tipo_padre', 'rodeo_nacimiento', 'rodeo_gestacion',
    ] if c in ds.columns]

    X = ds[numeric_features + categorical_features]
    y = ds['mean_future_ihm'].astype(float).values

    sys.path.insert(0, str(ROOT))
    from src.models import build_models
    models = build_models(numeric_features, categorical_features)
    pipe = models.get('random_forest')
    if pipe is None:
        return

    train_sizes, train_scores, val_scores = learning_curve(
        pipe, X, y, cv=5, scoring='r2',
        train_sizes=np.linspace(0.2, 1.0, 7),
        random_state=42, n_jobs=-1
    )
    train_mean = train_scores.mean(axis=1)
    train_std  = train_scores.std(axis=1)
    val_mean   = val_scores.mean(axis=1)
    val_std    = val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    ax.plot(train_sizes, train_mean, color=GREEN, marker='o', label='Training R²')
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                    color=GREEN, alpha=0.15)
    ax.plot(train_sizes, val_mean, color=BLUE, marker='s', label='Validation R² (CV)')
    ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std,
                    color=BLUE, alpha=0.15)
    ax.axhline(0, color=GRAY, ls='--', lw=1)
    ax.set_xlabel('Training set size')
    ax.set_ylabel('R²')
    ax.set_title('Learning curves — Random Forest\n(gap = variance; low ceiling = bias)')
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(FIGS / '14_learning_curves.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  14_learning_curves.png')


if __name__ == '__main__':
    main()
