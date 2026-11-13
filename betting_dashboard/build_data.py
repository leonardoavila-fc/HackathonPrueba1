"""
build_data.py — Genera data_betting.json a partir de plays.csv
Se ejecuta automáticamente desde run.sh o manualmente con:
    python3 betting_dashboard/build_data.py
"""

import pandas as pd
import numpy as np
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(BASE, '..', 'data', 'plays.csv')
OUT  = os.path.join(BASE, 'data_betting.json')

df = pd.read_csv(CSV, na_values=['NA', ''])
regular = df[df['isSTPlay'] == False].copy()
regular['score_diff_home'] = regular['HomeScoreBeforePlay'] - regular['VisitorScoreBeforePlay']
regular['is_pass']     = regular['PassResult'].notna()
regular['is_complete'] = regular['PassResult'] == 'C'
regular['is_sack']     = regular['PassResult'] == 'S'

def clock_to_seconds(clock):
    try:
        parts = str(clock).split(':')
        return int(parts[0]) * 60 + int(parts[1])
    except:
        return None

regular['clock_sec'] = regular['GameClock'].apply(clock_to_seconds)
data = {}

# ── KPIs generales ─────────────────────────────────────────────────────────
data['kpis'] = {
    'total_plays': int(len(df)),
    'total_games': int(df['gameId'].nunique()),
    'avg_yards':   round(float(regular['PlayResult'].mean()), 2),
    'comp_rate':   round(float(regular[regular['is_pass']]['is_complete'].mean() * 100), 1),
    'penalty_pct': round(float(df['isPenalty'].sum() / len(df) * 100), 1),
    'td_count':    int(
        ((df['HomeScoreAfterPlay'] - df['HomeScoreBeforePlay']) == 6).sum() +
        ((df['VisitorScoreAfterPlay'] - df['VisitorScoreBeforePlay']) == 6).sum()
    ),
}

# ── Game Script ────────────────────────────────────────────────────────────
state_labels = {
    'ganando_comodo':    'Ganando +8',
    'ganando_ajustado':  'Ganando 1-7',
    'empate':            'Empate',
    'perdiendo_ajustado':'Perdiendo 1-7',
    'perdiendo_comodo':  'Perdiendo +8',
}

def classify(d):
    if d > 7:    return 'ganando_comodo'
    elif d > 0:  return 'ganando_ajustado'
    elif d == 0: return 'empate'
    elif d >= -7:return 'perdiendo_ajustado'
    else:        return 'perdiendo_comodo'

regular['game_state'] = regular['score_diff_home'].apply(classify)
gs_rows = []
for q in [1, 2, 3, 4]:
    qdf = regular[regular['quarter'] == q]
    for sk, sl in state_labels.items():
        sdf = qdf[qdf['game_state'] == sk]
        if len(sdf) < 15:
            continue
        comp = sdf[sdf['is_pass']]['is_complete'].mean() * 100 if sdf['is_pass'].sum() > 0 else 0
        gs_rows.append({
            'quarter':    f'Q{q}',
            'state':      sl,
            'pass_pct':   round(float(sdf['is_pass'].mean() * 100), 1),
            'avg_yards':  round(float(sdf['PlayResult'].mean()), 2),
            'comp_pct':   round(float(comp), 1),
            'n':          int(len(sdf)),
        })
data['game_script'] = gs_rows

# ── Marcador engañoso ──────────────────────────────────────────────────────
enganoso = []
for q in [1, 2, 3, 4]:
    qdf  = regular[regular['quarter'] == q]
    win  = qdf[qdf['score_diff_home'] > 0]
    lose = qdf[qdf['score_diff_home'] < 0]
    enganoso.append({
        'quarter':        f'Q{q}',
        'ganando_yds':    round(float(win['PlayResult'].mean()),  2) if len(win)  > 0 else 0,
        'perdiendo_yds':  round(float(lose['PlayResult'].mean()), 2) if len(lose) > 0 else 0,
        'delta':          round(float(lose['PlayResult'].mean() - win['PlayResult'].mean()), 2)
                          if len(lose) > 0 and len(win) > 0 else 0,
    })
data['marcador_enganoso'] = enganoso

# ── 3er down ───────────────────────────────────────────────────────────────
third = regular[regular['down'] == 3].copy()
third['converted'] = third['PlayResult'] >= third['yardsToGo']
td3 = []
for q in [1, 2, 3, 4]:
    qdf = third[third['quarter'] == q]
    td3.append({
        'quarter':     f'Q{q}',
        'conv_pct':    round(float(qdf['converted'].mean() * 100), 1),
        'avg_ytg':     round(float(qdf['yardsToGo'].mean()), 1),
        'avg_result':  round(float(qdf['PlayResult'].mean()), 2),
        'n':           int(len(qdf)),
    })
data['third_down'] = td3

# ── Trigger 1 ──────────────────────────────────────────────────────────────
t1 = regular[
    (regular['quarter'] == 3) &
    (regular['score_diff_home'] >= -7) &
    (regular['score_diff_home'] <= -4) &
    (regular['offenseFormation'] == 'SHOTGUN')
]
t1_3rd = t1[t1['down'] == 3]
data['trigger1'] = {
    'n':          int(len(t1)),
    'avg_yards':  round(float(t1['PlayResult'].mean()), 2),
    'comp_pct':   round(float(t1[t1['is_pass']]['is_complete'].mean() * 100), 1) if t1['is_pass'].sum() > 0 else 0,
    'conv_3rd':   round(float((t1_3rd['PlayResult'] >= t1_3rd['yardsToGo']).mean() * 100), 1) if len(t1_3rd) > 0 else 0,
    'baseline':   round(float(regular[regular['quarter'] == 3]['PlayResult'].mean()), 2),
}

# ── Trigger 2 ──────────────────────────────────────────────────────────────
def t2_filter(rushers_op, threshold):
    return regular[
        (regular['quarter'] == 2) & regular['clock_sec'].notna() &
        (regular['clock_sec'] <= 300) &
        (regular['score_diff_home'] >= -7) & (regular['score_diff_home'] < 0) &
        regular['numberOfPassRushers'].notna() &
        rushers_op(regular['numberOfPassRushers'], threshold)
    ]

t2hp = t2_filter(lambda x, t: x >= t, 5)
t2lp = t2_filter(lambda x, t: x <= t, 3)
data['trigger2'] = {
    'hp': {
        'n':         int(len(t2hp)),
        'avg_yards': round(float(t2hp['PlayResult'].mean()), 2) if len(t2hp) > 0 else 0,
        'comp_pct':  round(float(t2hp[t2hp['is_pass']]['is_complete'].mean() * 100), 1) if t2hp['is_pass'].sum() > 0 else 0,
        'sack_pct':  round(float(t2hp['is_sack'].mean() * 100), 1) if len(t2hp) > 0 else 0,
    },
    'lp': {
        'n':         int(len(t2lp)),
        'avg_yards': round(float(t2lp['PlayResult'].mean()), 2) if len(t2lp) > 0 else 0,
        'comp_pct':  round(float(t2lp[t2lp['is_pass']]['is_complete'].mean() * 100), 1) if t2lp['is_pass'].sum() > 0 else 0,
        'sack_pct':  0,
    },
}

# ── Trigger 3 ──────────────────────────────────────────────────────────────
t3 = regular[
    (regular['quarter'] == 4) & regular['clock_sec'].notna() &
    (regular['clock_sec'] >= 600) &
    (regular['score_diff_home'] >= -7) & (regular['score_diff_home'] <= -1) &
    (regular['offenseFormation'].isin(['I_FORM', 'SINGLEBACK'])) &
    (~regular['is_pass'])
]
base_q4_run = regular[(regular['quarter'] == 4) & (~regular['is_pass'])]['PlayResult'].mean()
data['trigger3'] = {
    'n':          int(len(t3)),
    'avg_yards':  round(float(t3['PlayResult'].mean()), 2),
    'baseline':   round(float(base_q4_run), 2),
    'edge':       round(float(t3['PlayResult'].mean() - base_q4_run), 2),
}

# ── Presión defensiva ──────────────────────────────────────────────────────
pass_plays = regular[regular['is_pass'] & regular['numberOfPassRushers'].notna()].copy()
pass_plays['numberOfPassRushers'] = pass_plays['numberOfPassRushers'].astype(int)
press_data = []
for q in [1, 2, 3, 4]:
    qdf = pass_plays[pass_plays['quarter'] == q]
    hp  = qdf[qdf['numberOfPassRushers'] >= 5]
    lp  = qdf[qdf['numberOfPassRushers'] <= 3]
    if len(hp) < 5 or len(lp) < 5:
        continue
    press_data.append({
        'quarter':   f'Q{q}',
        'alta_sack': round(float(hp['is_sack'].mean() * 100), 1),
        'alta_comp': round(float(hp['is_complete'].mean() * 100), 1),
        'baja_sack': round(float(lp['is_sack'].mean() * 100), 1),
        'baja_comp': round(float(lp['is_complete'].mean() * 100), 1),
    })
data['presion'] = press_data

# ── Tasa de anotación ──────────────────────────────────────────────────────
anotaciones = df[df['HomeScoreAfterPlay'] > df['HomeScoreBeforePlay']].copy()
scoring = []
for q in [1, 2, 3, 4]:
    jp = df[
        (df['quarter'] == q) &
        (df['HomeScoreBeforePlay'] < df['VisitorScoreBeforePlay']) &
        ((df['VisitorScoreBeforePlay'] - df['HomeScoreBeforePlay']) <= 7)
    ]
    ant = anotaciones[
        (anotaciones['quarter'] == q) &
        (anotaciones['HomeScoreBeforePlay'] < anotaciones['VisitorScoreBeforePlay']) &
        ((anotaciones['VisitorScoreBeforePlay'] - anotaciones['HomeScoreBeforePlay']) <= 7)
    ]
    rate = len(ant) / len(jp) * 100 if len(jp) > 0 else 0
    scoring.append({
        'quarter':        f'Q{q}',
        'rate':           round(float(rate), 2),
        'n_jugadas':      int(len(jp)),
        'n_anotaciones':  int(len(ant)),
    })
data['scoring_rate'] = scoring

# ── Guardar ────────────────────────────────────────────────────────────────
with open(OUT, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✓ {OUT} generado ({len(json.dumps(data))} chars)")
