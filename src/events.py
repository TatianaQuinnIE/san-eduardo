"""
Event extraction.

Two sources of timestamped per-cow events:

  1. WhatsApp alarm log: free-text messages from the field team about
     individual cows (aborto, posible aborto, cesárea, descarte, etc).
     Parsed into structured event records.

  2. IATF session CSVs from DataMars: each row records an artificial
     insemination event (date, cow, semen used, weight at insemination).

Both feed into the master event table that the feature layer uses to
compute leakage-safe time-bounded features.
"""

import re
from typing import List, Dict
import pandas as pd
import numpy as np

from src.clean import normalize_idv

# ---------------------------------------------------------------------------
# WhatsApp log parser
# ---------------------------------------------------------------------------
# Lines look like:
#   13/6/2024, 10:50 - Dario Ríos: K180 aborto
#   24/12/2024, 09:07 - Dario Ríos: I553 negro
#   K965 fm
#   L376 fm
#
# Some messages span multiple lines and contain multiple cow IDs.
# IDV format on the farm has two patterns:
#   - Full: BE099L322 (national tag)
#   - Short visual: I553, K386, L376 (just letter + 3 digits, the visible
#     yellow tag). To match these against the registry we prefix with BE099.

# Event keywords mapped to canonical event types
EVENT_KEYWORDS = {
    'aborto':            'aborto',
    'abortada':          'aborto',
    'posible aborto':    'posible_aborto',
    'cesarea':           'cesarea',
    'cesárea':           'cesarea',
    'alzada':            'alzada',
    'alzadas':           'alzada',
    'montada':           'montada',
    'descarte':          'descarte',
    'venta':             'venta',
    'fm':                'fm_flagged',
    'cancer':            'salud_grave',
    'cáncer':            'salud_grave',
    'paratuberculocis':  'salud_grave',
    'paratuberculosis':  'salud_grave',
    'mala ubre':         'mala_ubre',
    'sin dientes':       'sin_dientes',
    'no dejar para madre': 'descarte',
}

# Pattern to match lines that start a new message
_MSG_START_RE = re.compile(
    r'^(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*(?P<time>\d{1,2}:\d{1,2})\s*-\s*'
    r'(?P<sender>[^:]+):\s*(?P<body>.*)$'
)

# IDV patterns: full (BE099X999) or short (X999, single letter + 3 digits/letters)
_IDV_FULL_RE = re.compile(r'\bBE0?99([A-Z]\d{3})\b', re.IGNORECASE)
_IDV_SHORT_RE = re.compile(r'\b([A-Z]\d{3})\b')


def parse_whatsapp_log(raw_text: str) -> pd.DataFrame:
    """Parse the WhatsApp alarms log into a long-form events table.

    Returns columns:
        date         - datetime
        sender       - who sent the message
        idv          - canonical cow IDV (BE099X999) — best effort
        event_type   - canonical event keyword
        raw_text     - the full message body for audit

    One row per (cow, event_type, message). Messages mentioning multiple
    cows produce multiple rows. Messages with no IDV match are skipped.
    """
    if not raw_text:
        return pd.DataFrame(
            columns=['date', 'sender', 'idv', 'event_type', 'raw_text']
        )

    # Group multi-line messages: a message starts at a header line and
    # continues until the next header line.
    messages: List[Dict] = []
    current = None
    for line in raw_text.splitlines():
        m = _MSG_START_RE.match(line)
        if m:
            if current is not None:
                messages.append(current)
            current = {
                'date_raw': m.group('date'),
                'time_raw': m.group('time'),
                'sender':   m.group('sender').strip(),
                'body':     [m.group('body')],
            }
        elif current is not None:
            current['body'].append(line)
    if current is not None:
        messages.append(current)

    rows = []
    for msg in messages:
        body = '\n'.join(msg['body']).lower()
        # Find IDVs mentioned anywhere in body
        idvs = set()
        # Full-pattern matches
        for m in _IDV_FULL_RE.finditer(body):
            idvs.add(normalize_idv(f'BE099{m.group(1)}'))
        # Short-pattern matches that aren't already captured as full
        for m in _IDV_SHORT_RE.finditer(body.upper()):
            short = m.group(1)
            # Avoid matching things like "292 días" or page numbers
            # Heuristic: short IDV first char must be a letter only (already enforced by regex)
            idvs.add(normalize_idv(f'BE099{short}'))
        idvs.discard(None)

        if not idvs:
            continue

        # Find event type(s) mentioned
        event_types = set()
        for kw, canonical in EVENT_KEYWORDS.items():
            if kw in body:
                event_types.add(canonical)
        if not event_types:
            event_types = {'unknown'}

        # Parse the date
        try:
            date = pd.to_datetime(
                f"{msg['date_raw']} {msg['time_raw']}",
                format='mixed', dayfirst=True, errors='coerce'
            )
        except Exception:
            date = pd.NaT

        for idv in idvs:
            for et in event_types:
                rows.append({
                    'date':       date,
                    'sender':     msg['sender'],
                    'idv':        idv,
                    'event_type': et,
                    'raw_text':   '\n'.join(msg['body'])[:200],
                })

    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# IATF session parser
# ---------------------------------------------------------------------------

def parse_iatf_sessions(iatf_raw: pd.DataFrame) -> pd.DataFrame:
    """Normalize the concatenated IATF session DataFrame into events.

    Returns columns:
        idv               cow IDV (canonical)
        date              session date
        peso              cow weight at insemination (kg)
        semen_utilizado   bull/semen name used on this cow
        rodeo             rodeo this session covers (from session_file or column)
        session_file      origin file key
    """
    if iatf_raw is None or len(iatf_raw) == 0:
        return pd.DataFrame(
            columns=['idv', 'date', 'peso', 'semen_utilizado',
                     'rodeo', 'session_file']
        )

    df = iatf_raw.copy()

    # IDV column is consistently named 'IDV'
    df['idv'] = df['IDV'].map(normalize_idv) if 'IDV' in df.columns else None

    # Date: 'Fecha' column, format like '18 sep. 2025'
    if 'Fecha' in df.columns:
        df['date'] = pd.to_datetime(
            df['Fecha'].astype(str).str.replace('.', '', regex=False),
            format='mixed', dayfirst=True, errors='coerce'
        )
    else:
        df['date'] = pd.NaT

    # Weight at insemination
    df['peso'] = (pd.to_numeric(df['Peso'], errors='coerce')
                  if 'Peso' in df.columns else np.nan)

    # Semen used
    df['semen_utilizado'] = (df['Semen utilizado']
                              if 'Semen utilizado' in df.columns
                              else pd.NA)

    # Rodeo: try 'Rodeo Gestacion' first, fallback to inferring from filename
    if 'Rodeo Gestacion' in df.columns:
        df['rodeo'] = df['Rodeo Gestacion']
    else:
        df['rodeo'] = pd.NA

    out = df[['idv', 'date', 'peso', 'semen_utilizado', 'rodeo', 'session_file']].copy()
    out = out[out['idv'].notna()].reset_index(drop=True)
    return out


# ---------------------------------------------------------------------------
# Master event table
# ---------------------------------------------------------------------------

def build_event_table(sources: dict) -> pd.DataFrame:
    """Combine WhatsApp + IATF events into one long-form per-cow event table."""
    wa = parse_whatsapp_log(sources.get('whatsapp_raw', ''))
    if len(wa):
        wa = wa[['date', 'idv', 'event_type']].copy()
        wa['source'] = 'whatsapp'
        wa['detail'] = pd.NA

    iatf = parse_iatf_sessions(sources.get('iatf_sessions', pd.DataFrame()))
    iatf_events = pd.DataFrame({
        'date':       iatf['date'],
        'idv':        iatf['idv'],
        'event_type': 'iatf',
        'source':     'iatf_session',
        'detail':     iatf['semen_utilizado'],
    })

    combined = pd.concat([wa, iatf_events], ignore_index=True, sort=False)
    combined = combined[combined['idv'].notna()].reset_index(drop=True)
    return combined
