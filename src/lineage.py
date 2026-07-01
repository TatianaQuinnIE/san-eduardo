"""
Cow registry and lineage graph.

The cow registry is a single canonical table — one row per unique cow ever
seen across any source sheet. The lineage graph tracks mother→daughter and
sire→offspring edges, enabling features like 'mother's IHM history up to
year T' without leakage.

Conflict resolution between sources uses precedence ordering. We prefer the
most recent / richest sources for each field but preserve the source list
per cow for auditability.
"""

import pandas as pd
import numpy as np

from src.clean import (
    normalize_idv_column,
    normalize_pelaje,
    normalize_tipo_padre,
)


def build_cow_registry(sources: dict) -> pd.DataFrame:
    """Produce one row per unique cow seen anywhere across all sources.

    Conflict precedence (lower number = higher priority):
      1. terneras_2027 (richest features, most recent)
      2. nacimientos_2025 (field birth log, authoritative for births)
      3. terneros_sesiones (chute pass-through)
      4. vientres (adult cow database)
      5. ihm_historico_new (newer IHM source)
      6. fm_prep_2025 (2025 cohort)
    """
    contributions = []

    # Terneras 2027
    df = sources['terneras_2027'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV']),
        'sex':              df['Sexo'].astype(str).str.strip(),
        'anio_nacimiento':  pd.to_numeric(df['Anio Nacimiento'], errors='coerce'),
        'fecha_nacimiento': pd.to_datetime(df['Fecha Nacimiento'], errors='coerce'),
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['Madre IDV']),
        'nombre_padre':     df['Nombre Padre'],
        'tipo_padre':       df['Tipo Padre'].map(normalize_tipo_padre),
        'peso_al_nacer':    pd.to_numeric(df['Peso al nacer'], errors='coerce'),
        'rodeo_nacimiento': df['Rodeo Nacimiento'],
        'rodeo_gestacion':  df['Rodeo Gestacion'],
        '_source':          'terneras_2027',
        '_priority':        1,
    }))

    # Nacimientos 2025
    df = sources['nacimientos_2025'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV Ternero']),
        'sex':              df['Sexo'].astype(str).str.strip(),
        'anio_nacimiento':  pd.to_datetime(df['Fecha'], errors='coerce').dt.year,
        'fecha_nacimiento': pd.to_datetime(df['Fecha'], errors='coerce'),
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['IDV Madre']),
        'nombre_padre':     pd.NA,
        'tipo_padre':       pd.NA,
        'peso_al_nacer':    pd.to_numeric(df['Peso al nacer'], errors='coerce'),
        'rodeo_nacimiento': pd.NA,
        'rodeo_gestacion':  df['Rodeo de Gestacion'],
        '_source':          'nacimientos_2025',
        '_priority':        2,
    }))

    # Terneros de Sesiones
    df = sources['terneros_sesiones'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV']),
        'sex':              df['Sexo'].astype(str).str.strip(),
        'anio_nacimiento':  pd.to_numeric(df['Anio Nacimiento'], errors='coerce'),
        'fecha_nacimiento': pd.to_datetime(df['Fecha NacImIento'], errors='coerce'),
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['Madre IDV']),
        'nombre_padre':     df['Nombre Padre'],
        'tipo_padre':       df['TIpo Padre'].map(normalize_tipo_padre),
        'peso_al_nacer':    pd.to_numeric(df['Peso al nacer'], errors='coerce'),
        'rodeo_nacimiento': df['Rodeo Nacimiento'],
        'rodeo_gestacion':  df['Rodeo GestacIÃ³n'],   # source mojibake
        '_source':          'terneros_sesiones',
        '_priority':        3,
    }))

    # Vientres
    df = sources['vientres'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV']),
        'sex':              'Hembra',
        'anio_nacimiento':  pd.to_numeric(df['Año Nac.'], errors='coerce'),
        'fecha_nacimiento': pd.NaT,
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['Madre IDV']),
        'nombre_padre':     df['Nombre Padre'],
        'tipo_padre':       df['Tipo Padre'].map(normalize_tipo_padre),
        'peso_al_nacer':    np.nan,
        'rodeo_nacimiento': pd.NA,
        'rodeo_gestacion':  pd.NA,
        '_source':          'vientres',
        '_priority':        4,
    }))

    # IHM Histórico new
    df = sources['ihm_historico_new'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV']),
        'sex':              'Hembra',
        'anio_nacimiento':  pd.to_numeric(df['Anio \nNacimiento'], errors='coerce'),
        'fecha_nacimiento': pd.NaT,
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['Madre IDV']),
        'nombre_padre':     df['Nombre \nPadre'],
        'tipo_padre':       df['Tipo \nPadre'].map(normalize_tipo_padre),
        'peso_al_nacer':    np.nan,
        'rodeo_nacimiento': pd.NA,
        'rodeo_gestacion':  pd.NA,
        '_source':          'ihm_historico_new',
        '_priority':        5,
    }))

    # FM p-rep 2025
    df = sources['fm_prep_2025'].copy()
    contributions.append(pd.DataFrame({
        'idv':              normalize_idv_column(df['IDV']),
        'sex':              df['Sexo'].astype(str).str.strip(),
        'anio_nacimiento':  np.nan,
        'fecha_nacimiento': pd.NaT,
        'pelaje':           df['Pelaje'].map(normalize_pelaje),
        'madre_idv':        normalize_idv_column(df['Madre IDV']),
        'nombre_padre':     df['Nombre Padre'],
        'tipo_padre':       df['TIpo Padre'].map(normalize_tipo_padre),
        'peso_al_nacer':    np.nan,
        'rodeo_nacimiento': df['Rodeo Nacimiento'],
        'rodeo_gestacion':  df['Rodeo Gestación'],
        '_source':          'fm_prep_2025',
        '_priority':        6,
    }))

    long = pd.concat(contributions, ignore_index=True)
    long = long[long['idv'].notna()].copy()
    long = long.sort_values(['idv', '_priority']).reset_index(drop=True)

    fields = ['sex', 'anio_nacimiento', 'fecha_nacimiento', 'pelaje',
              'madre_idv', 'nombre_padre', 'tipo_padre', 'peso_al_nacer',
              'rodeo_nacimiento', 'rodeo_gestacion']

    def _first_non_null(s):
        s = s.dropna()
        return s.iloc[0] if len(s) else np.nan

    registry = (long.groupby('idv', dropna=False)[fields]
                    .agg(_first_non_null)
                    .reset_index())

    sources_per_cow = (long.groupby('idv')['_source']
                           .agg(lambda s: ','.join(sorted(set(s))))
                           .reset_index()
                           .rename(columns={'_source': 'sources'}))
    registry = registry.merge(sources_per_cow, on='idv', how='left')
    return registry


def build_lineage_table(registry: pd.DataFrame) -> pd.DataFrame:
    """Add maternal-grandmother and inferred maternal-grandsire columns."""
    df = registry[['idv', 'madre_idv', 'nombre_padre']].copy()

    mother_links = registry[['idv', 'madre_idv']].rename(
        columns={'idv': 'madre_idv', 'madre_idv': 'abuela_materna_idv'}
    )
    df = df.merge(mother_links, on='madre_idv', how='left')

    sire_of_dam = registry[['idv', 'nombre_padre']].rename(
        columns={'idv': 'madre_idv', 'nombre_padre': 'abuelo_materno_inferred'}
    )
    df = df.merge(sire_of_dam, on='madre_idv', how='left')
    return df


def lineage_summary(registry: pd.DataFrame, lineage: pd.DataFrame) -> dict:
    """Diagnostics: how many cows have known parents/grandparents."""
    return {
        'total_cows': len(registry),
        'with_mother_idv': int(registry['madre_idv'].notna().sum()),
        'mother_in_registry': int(registry['madre_idv'].isin(registry['idv']).sum()),
        'with_grandmother_idv': int(lineage['abuela_materna_idv'].notna().sum()),
        'with_sire_name': int(registry['nombre_padre'].notna().sum()),
        'with_maternal_grandsire': int(lineage['abuelo_materno_inferred'].notna().sum()),
    }
