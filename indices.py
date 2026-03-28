"""
indices.py — Calcolo degli indici nutrizionali lipidici
========================================================
Implementa gli indici più usati nella letteratura scientifica
per la valutazione del profilo qualitativo degli acidi grassi.

Riferimenti:
- Ulbricht & Southgate (1991) - AI e TI
- Santos-Silva et al. (2002) - h/H ratio
- WHO/FAO (2010) - PUFA/SFA recommendation
"""

import pandas as pd
import numpy as np


def calculate_indices(df: pd.DataFrame) -> dict:
    """
    Calcola gli indici nutrizionali lipidici da un DataFrame di acidi grassi.

    Parameters
    ----------
    df : pd.DataFrame
        Colonne attese: abbreviation, category, n_type, percentage

    Returns
    -------
    dict
        Dizionario con tutti gli indici calcolati
    """
    indices = {}

    # --- Somme per categoria ---
    sfa  = df[df['category'] == 'SFA']['percentage'].sum()
    mufa = df[df['category'] == 'MUFA']['percentage'].sum()
    pufa = df[df['category'] == 'PUFA']['percentage'].sum()

    indices['SFA_pct']  = round(sfa,  3)
    indices['MUFA_pct'] = round(mufa, 3)
    indices['PUFA_pct'] = round(pufa, 3)

    # --- Rapporto PUFA / SFA ---
    if sfa > 0:
        indices['PUFA_SFA'] = round(pufa / sfa, 4)

    # --- Acidi grassi n-3 e n-6 ---
    has_ntype = 'n_type' in df.columns

    if has_ntype:
        n3 = df[df['n_type'] == 'n-3']['percentage'].sum()
        n6 = df[df['n_type'] == 'n-6']['percentage'].sum()
        indices['n3_pct'] = round(n3, 3)
        indices['n6_pct'] = round(n6, 3)

        if n6 > 0:
            indices['n3_n6'] = round(n3 / n6, 4)

    # --- Acidi grassi singoli utili per gli indici ---
    c12  = _get_fa(df, 'C12:0')
    c14  = _get_fa(df, 'C14:0')
    c16  = _get_fa(df, 'C16:0')
    c18_0 = _get_fa(df, 'C18:0')
    c18_1 = _get_fa(df, 'C18:1')  # somma tutti i C18:1

    # --- Indice di Aterogenicità (AI) — Ulbricht & Southgate, 1991 ---
    # AI = (C12:0 + 4×C14:0 + C16:0) / (ΣMUFA + Σn-6 PUFA + Σn-3 PUFA)
    if has_ntype:
        denom_ai = mufa + n6 + n3
        if denom_ai > 0:
            ai = (c12 + 4 * c14 + c16) / denom_ai
            indices['AI'] = round(ai, 4)

    # --- Indice di Trombogenicità (TI) — Ulbricht & Southgate, 1991 ---
    # TI = (C14:0 + C16:0 + C18:0) / [(0.5×ΣMUFA) + (0.5×Σn-6) + (3×Σn-3) + (n-3/n-6)]
    if has_ntype:
        n3_n6_ratio = n3 / n6 if n6 > 0 else 0
        denom_ti = (0.5 * mufa) + (0.5 * n6) + (3 * n3) + n3_n6_ratio
        if denom_ti > 0:
            ti = (c14 + c16 + c18_0) / denom_ti
            indices['TI'] = round(ti, 4)

    # --- Rapporto h/H (ipocolesterolemizzanti / ipercolesterolemizzanti) ---
    # h = C18:1 n-9 + PUFA n-6 + PUFA n-3
    # H = C12:0 + C14:0 + C16:0
    if has_ntype:
        h_lower = c18_1 + n6 + n3
        H_upper = c12 + c14 + c16
        if H_upper > 0:
            indices['hH'] = round(h_lower / H_upper, 4)

    # --- Indice di Salute (HI) = MUFA + PUFA / SFA ---
    if sfa > 0:
        indices['HI'] = round((mufa + pufa) / sfa, 4)

    return indices


def _get_fa(df: pd.DataFrame, abbreviation: str) -> float:
    """
    Recupera la percentuale di un acido grasso tramite corrispondenza
    parziale sull'abbreviazione (es. 'C18:1' cattura tutti i C18:1 isomeri).
    """
    mask = df['abbreviation'].str.startswith(abbreviation)
    result = df.loc[mask, 'percentage'].sum()
    return float(result) if not pd.isna(result) else 0.0


def interpret_index(key: str, value: float) -> tuple[str, str]:
    """
    Restituisce (giudizio, colore_hex) per un dato indice.
    
    Returns
    -------
    tuple
        (label stringa, colore hex per UI)
    """
    rules = {
        'AI':       (1.0,  False, 'basso = ottimo',    'alto = attenzione'),
        'TI':       (1.5,  False, 'basso = ottimo',    'alto = attenzione'),
        'PUFA_SFA': (0.45, True,  'ottimo (≥0.45)',    'sotto soglia WHO'),
        'n3_n6':    (0.25, True,  'equilibrato',       'sbilanciato verso n-6'),
        'hH':       (1.0,  True,  'profilo favorevole','profilo sfavorevole'),
        'HI':       (1.0,  True,  'indice alto',       'indice basso'),
    }
    if key not in rules:
        return ('—', '#a0a0c0')

    threshold, higher_better, label_good, label_bad = rules[key]
    good = value >= threshold if higher_better else value <= threshold
    label = label_good if good else label_bad
    color = '#7bed9f' if good else '#ff6b9d'
    return label, color
