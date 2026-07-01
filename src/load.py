"""
Source loaders.

One function per source sheet/file. Loaders only read; they don't transform.
Cleaning lives in clean.py. Lineage and event parsing live in their own modules.

Why per-sheet: keeps the file-system dependency in one place, makes it
trivial to swap a source file when the farm sends an updated version,
and lets the rest of the codebase pretend that "source X" is just a
DataFrame with known columns.
"""

import warnings
from pathlib import Path

import pandas as pd

# Files received from the farm (April-May 2026).
SOURCES = {
    'futuras_madres':       'Futuras_Madres.xlsx',
    'futuras_madres_xr':    'Futuras_Madres_a_xr5000.xlsx',
    'paricion_2025':        'Paricion_2025.xlsx',
    'preseleccion_2027':    'Preseleccio_n_FM_2027.xlsx',
}

# IATF session CSVs exported from DataMars (semicolon-separated, mojibake in headers)
IATF_SESSION_FILES = {
    'iatf_1ra_2da':   'IATF_Rodeo_1ra_y_2da__18_set__2025_.csv',
    'iatf_cab_mixto': 'IATF_Rodeo_Cabeza_Mixto__27_set__2025_.csv',
    'iatf_cab_negro': 'IATF_Rodeo_Cabeza_Negro__29_set__2025_.csv',
    'iatf_fm':        'IATF_Rodeo_FM__13_set__2025___1_.csv',
}

WHATSAPP_LOG = 'whatsapp_alarms.txt'


def _read_xlsx(raw_dir, source_key, sheet_name):
    """Read one sheet from one Excel source, suppress style warnings."""
    path = Path(raw_dir) / SOURCES[source_key]
    if not path.exists():
        raise FileNotFoundError(
            f"Source file not found: {path}. "
            f"Check that data/raw/ contains all farm files (see README)."
        )
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return pd.read_excel(path, sheet_name=sheet_name)


# -- IHM history -------------------------------------------------------------

def load_historial_ihm_old(raw_dir):
    """Older IHM history. 822 cows. IHM is in PERCENT (0-100), unadjusted."""
    return _read_xlsx(raw_dir, 'futuras_madres', 'Historial IHM')


def load_ihm_historico_new(raw_dir):
    """Newer IHM history. 1208 cows. IHM in PROPORTION (0-1), 205-day adjusted.
    PREFERRED source. The farm confirmed (May 2026) that ALL years in this
    file are 205-day adjusted."""
    return _read_xlsx(raw_dir, 'preseleccion_2027', 'IHM Histórico')


# -- Cohorts -----------------------------------------------------------------

def load_terneras_2027(raw_dir):
    """2027 preselection cohort. 405 female calves born 2025.
    Uses 'estrellas' label scheme. Confirmed equivalent to 'verdes' scheme
    (verdes_3 = estrellas_3) per farm conversation May 2026.
    Has engineered binary flags."""
    return _read_xlsx(raw_dir, 'preseleccion_2027', 'Terneras')


def load_fm_prep_2025(raw_dir):
    """2025 preselection cohort. ~346 female heifers.
    Uses 'verdes' label scheme. Mother's IHM joined."""
    return _read_xlsx(raw_dir, 'futuras_madres', 'FM p-rep.')


# -- Cow / calf records ------------------------------------------------------

def load_vientres(raw_dir):
    """Adult cow database. 881 records. Has gestation history columns."""
    return _read_xlsx(raw_dir, 'futuras_madres', 'Vientres')


def load_terneros_sesiones(raw_dir):
    """Calves through chute, weighing-session records. 726 rows."""
    return _read_xlsx(raw_dir, 'futuras_madres', 'Terneros de Sesiones')


def load_nacimientos_2025(raw_dir):
    """Field birth log for 2025. 800 events. Notas column has rich qualitative info."""
    df = _read_xlsx(raw_dir, 'paricion_2025', 'Nacimientos')
    # Source has trailing whitespace in the 'Fecha' header
    df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
    return df


def load_base_madres(raw_dir):
    """Mother-side cycle tracker for 2025. 792 cows."""
    return _read_xlsx(raw_dir, 'paricion_2025', 'Base de Madres')


def load_peso_terneros_2027(raw_dir):
    """Weaning weights for the 2025 calf cohort. 757 calves, both sexes.
    Has both Peso Destete and Peso 205 días."""
    return _read_xlsx(raw_dir, 'preseleccion_2027', 'Peso Terneros')


# -- IATF session exports (DataMars CSV) -------------------------------------

def load_iatf_sessions(raw_dir):
    """Load all four 2025 IATF session CSVs and concatenate.

    These are exports from the DataMars XR5000 cloud, one per rodeo.
    Format: semicolon-separated, with mojibake in some column headers
    (e.g. 'Rodeo GestacIÃ³n' for 'Rodeo Gestación').

    Returns a single DataFrame with a 'session_file' column tracking origin.
    Total ~696 IATF events with semen-used per cow.
    """
    raw_dir = Path(raw_dir)
    frames = []
    for key, fn in IATF_SESSION_FILES.items():
        path = raw_dir / fn
        if not path.exists():
            warnings.warn(f"IATF session file missing: {path}")
            continue
        df = pd.read_csv(path, sep=';', encoding='utf-8')
        df['session_file'] = key
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    # Concat with sort=False to preserve column order from the first frame
    combined = pd.concat(frames, ignore_index=True, sort=False)
    return combined


# -- WhatsApp alarm log ------------------------------------------------------

def load_whatsapp_log_raw(raw_dir):
    """Read the WhatsApp chat export as raw text. Parsing happens in events.py."""
    path = Path(raw_dir) / WHATSAPP_LOG
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8', errors='replace')


# -- Bulk loader -------------------------------------------------------------

def load_all_sources(raw_dir):
    """Load every source we use. Returns a dict keyed by source name."""
    return {
        'historial_ihm_old':   load_historial_ihm_old(raw_dir),
        'ihm_historico_new':   load_ihm_historico_new(raw_dir),
        'terneras_2027':       load_terneras_2027(raw_dir),
        'fm_prep_2025':        load_fm_prep_2025(raw_dir),
        'vientres':            load_vientres(raw_dir),
        'terneros_sesiones':   load_terneros_sesiones(raw_dir),
        'nacimientos_2025':    load_nacimientos_2025(raw_dir),
        'base_madres':         load_base_madres(raw_dir),
        'peso_terneros_2027':  load_peso_terneros_2027(raw_dir),
        'iatf_sessions':       load_iatf_sessions(raw_dir),
        'whatsapp_raw':        load_whatsapp_log_raw(raw_dir),
    }
