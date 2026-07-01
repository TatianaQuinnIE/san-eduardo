"""Plotting helpers used by figure-generation scripts."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def missingness_profile(df: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame({
        'n_null':   df.isnull().sum(),
        'pct_null': df.isnull().mean() * 100,
        'n_unique': df.nunique(),
        'dtype':    df.dtypes.astype(str),
    }).sort_values('pct_null', ascending=False)
