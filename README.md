# Cattle Replacement Heifer Selection — Machine Learning Project

A machine-learning evaluation of replacement-heifer selection at a family beef-cattle farm in Bragado, Buenos Aires. Course project for Machine Learning Foundations, IE University, May 2026.

The notebook `notebooks/00_main_pipeline.ipynb` is the primary deliverable (report) and the integrated analysis. 

## What this project is about

Every year the farm has to decide which female calves (~300–400 per cohort) to keep as replacement mothers, and which to send to fattening for sale. Today this is done with a hand-coded rule table the farm developed over time. Our project asks a precise question:

**Given selection-time information about a heifer, can a data-driven model predict her future productivity well enough to refine the farm's existing rule?**

This is a *decision-support* problem, not pure prediction. We follow a three-layer analysis:

1. **Outcome prediction**: train a regression model on selection-time features, target = mean future IHM (Maternal Ability Index over adult years).
2. **Rule analysis**: programmatically reproduce the farm's documented rule and quantify how it's drifted across years.
3. **Rule vs outcome comparison**: where the model and the rule disagree, which one matches actual outcomes better?

## Data

Four farm Excel files plus DataMars CSV exports plus a WhatsApp alarm log:

| Source | Records | Use |
|---|---|---|
| `Futuras_Madres.xlsx` | 822 + 364 + 881 + 726 | Older IHM history, 2025 cohort, adult cows, weighing sessions |
| `Paricion_2025.xlsx` | 800 | 2025 birth log + cycle tracker |
| `Preseleccio_n_FM_2027.xlsx` | 1208 + 405 + 757 | Adjusted IHM history, 2027 cohort, 205-day weights |
| 4 IATF session CSVs | 696 | Insemination events with semen used per cow |
| WhatsApp alarms log | 79 events | Abortions, sales, health flags |

After reconciliation: **2,728 unique cows**, **5,265 IHM observations** spanning 2022–2026, **337 cows** in the supervised-modeling population.

The data is private — it's hosted inside this private repo, not shared publicly. The `data/raw/` folder contains the 9 source files (Excel + CSV + WhatsApp text export).

## Repository structure

```
cattle-heifer-selection/
├── data/
│   ├── raw/         # Original farm files (private; included in repo)
│   └── processed/   # Generated CSVs — committed to the repo so the grader can run
│                    #   the notebook directly; pipeline scripts regenerate them if deleted
├── src/             # All transformation & modeling code
│   ├── load.py              # File/sheet loaders
│   ├── clean.py             # Normalization (IDVs, labels, IHM scale)
│   ├── lineage.py           # Cow registry and lineage graph
│   ├── events.py            # WhatsApp + IATF event parsing
│   ├── features.py          # Supervised dataset construction
│   ├── rules.py             # Programmatic rule reproduction
│   ├── models.py            # Model definitions
│   ├── evaluation.py        # Selection metrics (precision@k, etc.)
│   ├── reproduction.py      # Reproductive event parsing and outcomes
│   ├── supervised_v2.py     # Multi-target supervised dataset (IHM + pregnancy rate)
│   └── eda.py               # Plotting helpers
├── tests/           # Unit tests for the cleaning layer
├── notebooks/       # Notebooks act as interface; logic lives in src/
├── scripts/         # End-to-end pipeline scripts
│   ├── build_processed.py        # Raw files → processed CSVs (v1)
│   ├── build_processed_v2.py     # Adds reproductive outcomes (v2)
│   ├── run_models.py             # Baseline models + temporal holdout
│   ├── run_models_v2.py          # Multi-target models (IHM, pregnancy, composite)
│   ├── tune_models.py            # RandomizedSearchCV hyperparameter tuning
│   ├── run_shap.py               # SHAP feature importance (tuned model)
│   ├── run_failure_cases.py      # Residual diagnostics
│   ├── run_concept_drift.py      # Rule drift analysis (IHM input: raw→205d adjusted)
│   ├── make_figures.py           # All EDA, ROC, and learning curve figures
│   └── check_reproducibility.py  # End-to-end smoke test
├── reports/         # Data dictionary, EDA writeups, team log
├── outputs/         # Generated figures and tables
└── requirements.txt
```

## Reproduction

**Python 3.10+ required**

1. Clone and create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate     # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the pipeline (use `python3` on Mac if `python` is not found):
   ```bash
   python3 scripts/build_processed.py      # raw → processed CSVs (~10 sec)
   python3 scripts/build_processed_v2.py   # v2 supervised dataset (~5 sec)
   python3 scripts/run_models.py           # baseline models + temporal holdout (~30 sec)
   python3 scripts/run_models_v2.py        # multi-target models, v2 dataset (~30 sec)
   python3 scripts/tune_models.py          # hyperparameter search (~2 min)
   python3 scripts/run_shap.py             # SHAP feature importance (~15 sec)
   python3 scripts/run_failure_cases.py    # residual diagnostics (~15 sec)
   python3 scripts/run_concept_drift.py    # rule drift analysis (~5 sec)
   python3 scripts/make_figures.py         # all EDA + ROC + learning curve figures (~10 sec)
   python3 scripts/check_reproducibility.py  # end-to-end smoke test
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

## Team

| Member | Domain |
|---|---|
| Tatiana Quinn | Project lead, integration, raw data ingestion, pipeline script, temporal holdout, reproducibility smoke test, README, notebook |
| Hari Siva | Source loaders, source inventory, authoritative-field precedence, project presentation |
| Alesia Dako | Cleaning, normalization, 36 unit tests, data dictionary, concept-drift script, failure-case / residual diagnostics |
| Viktoriia Stepanenko | Cow registry, two-generation lineage, event parsing, reproduction module, rule-version drift cohort overlap |
| Kohana Rakipi | Leakage-safe feature engineering, supervised dataset, final notebook and code checks, project report |
| Laura Somogyi | Programmatic rule reproduction, models, evaluation, hyperparameter tuning, SHAP, multi-target modeling |

## Tools

GitHub for code and version control. Python ecosystem: pandas for data wrangling, scikit-learn for pipelines and RandomizedSearchCV, shap for feature importance, matplotlib for figures. The notebook acts as the interface; the actual logic lives in src/ modules. 36 unit tests in tests/ guard the cleaning layer against regressions.

## AI Declaration

We used Claude and Cursor throughout this project to help us with structure, code, and to proofread our work before submitting.