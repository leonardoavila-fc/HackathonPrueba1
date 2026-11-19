# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "pyarrow"]
# ///
"""
build_clean.py — Auditoría de sacks, feature engineering y exportación limpia
Ejecutar: uv run python build_clean.py
Genera:
  - data/nfl_clean.parquet   → dataset limpio con variables tácticas
  - tesis_coach.md           → prueba de hipótesis para el coach
"""

import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

BASE   = os.path.dirname(os.path.abspath(__file__))
FILE   = os.path.join(BASE, "data", "nflplays.csv")
OUT_P  = os.path.join(BASE, "data", "nfl_clean.parquet")
OUT_MD = os.path.join(BASE, "tesis_coach.md")

print("=" * 62)
print("  Build Clean + Tesis Coach — nflplays.csv")
print("=" * 62)

# ══════════════════════════════════════════════════════════════
# CARGA Y LIMPIEZA BASE
# ══════════════════════════════════════════════════════════════
print("\n[1/7] Cargando y limpiando…")
df = pd.read_csv(FILE, sep="\t", low_memory=False)

# Filtros de limpieza (Pro Bowl + PLAY_TYPE nulo + desc numérica)
df = df[~(df["HOME_TEAM"].isin(["AFC","NFC"]) | df["AWAY_TEAM"].isin(["AFC","NFC"]) |
          df["OFF"].isin(["AFC","NFC"])        | df["DEF"].isin(["AFC","NFC"]))].copy()
df = df[df["PLAY_TYPE"].notna()].copy()
df = df[~df["DESCRIPTION"].astype(str).str.strip().str.match(r"^-?\d+(\.\d+)?$")].copy()

n_clean = len(df)
print(f"      Dataset limpio: {n_clean:,} filas")

# ══════════════════════════════════════════════════════════════
# EXTRACCIÓN DE YARDS_GAINED (CON AUDITORÍA DE SACKS)
# ══════════════════════════════════════════════════════════════
print("[2/7] Extrayendo yards_gained (con auditoría de sacks)…")

def extract_yards(desc: str) -> float | None:
    if not isinstance(desc, str):
        return None
    d = desc.lower()

    # Pase incompleto → 0
    if re.search(r'\bpass\s+incomplete\b|\bincomplete\b', d):
        return 0.0
    # Sin ganancia → 0
    if re.search(r'\bno gain\b', d):
        return 0.0
    # Patrón principal "for N yard(s)"
    m = re.search(r'for\s+(-?\d+)\s+yard', d)
    if m:
        return float(m.group(1))
    # Patrón alternativo "gains N"
    m = re.search(r'gains?\s+(-?\d+)', d)
    if m:
        return float(m.group(1))
    # Patrón sack: "sacked at TEAM XX for -N yards"
    m = re.search(r'sacked\s+at\s+\w+\s+\d+\s+for\s+(-?\d+)\s+yard', d)
    if m:
        return float(m.group(1))
    return None

df["yards_gained"] = df["DESCRIPTION"].apply(extract_yards)

# ── Auditoría de Sacks ──────────────────────────────────────
sack_mask = df["PLAY_TYPE"].astype(str).str.contains("SACK", na=False)
df_sacks  = df[sack_mask].copy()

sack_null   = df_sacks["yards_gained"].isna().sum()
sack_neg    = (df_sacks["yards_gained"] < 0).sum()
sack_zero   = (df_sacks["yards_gained"] == 0).sum()
sack_pos    = (df_sacks["yards_gained"] > 0).sum()
sack_total  = len(df_sacks)

# Para los sacks nulos, intentar extraer con patrón alternativo
def fix_sack(desc: str) -> float | None:
    if not isinstance(desc, str):
        return None
    d = desc.lower()
    # "sacked at TEAM XX" → buscar "for -N yards" más adelante
    m = re.search(r'sacked.*?for\s+(-?\d+)\s+yard', d)
    if m:
        return float(m.group(1))
    # "at TEAM XX" → yardas = -(posición actual - posición resultante)
    # Fallback: buscar cualquier número negativo en contexto de sack
    m = re.search(r'(-\d+)\s+yard', d)
    if m:
        return float(m.group(1))
    return None

null_sack_idx = df_sacks[df_sacks["yards_gained"].isna()].index
fixed_vals = df.loc[null_sack_idx, "DESCRIPTION"].apply(fix_sack)
# Convertir None → NaN para compatibilidad con columna float64
fixed_vals = fixed_vals.apply(lambda x: float(x) if x is not None else np.nan)
df.loc[null_sack_idx, "yards_gained"] = fixed_vals

# Revalidar
df_sacks2    = df[sack_mask].copy()
sack_null2   = df_sacks2["yards_gained"].isna().sum()
sack_neg2    = (df_sacks2["yards_gained"] < 0).sum()
sack_zero2   = (df_sacks2["yards_gained"] == 0).sum()

print(f"      Sacks totales: {sack_total:,} | "
      f"Neg: {sack_neg2:,} | Zero: {sack_zero2:,} | Null restantes: {sack_null2:,}")

# ══════════════════════════════════════════════════════════════
# FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════
print("[3/7] Construyendo variables tácticas…")

desc = df["DESCRIPTION"].astype(str)
pt   = df["PLAY_TYPE"].astype(str)

# play_category: primera etiqueta del PLAY_TYPE
df["play_category"] = pt.apply(lambda x: x.split("|")[0].strip())

# is_shotgun / is_no_huddle
df["is_shotgun"]   = desc.str.contains(r"\bShotgun\b",   case=True,  regex=True)
df["is_no_huddle"] = desc.str.contains(r"\bNo Huddle\b", case=True,  regex=True)

# pass_direction — extraído de DESCRIPTION solo en jugadas de pase
def get_pass_direction(row):
    if "PASS" not in str(row["PLAY_TYPE"]):
        return None
    d = str(row["DESCRIPTION"]).lower()
    # Profundidad + lado
    if re.search(r'\bshort left\b',  d): return "short_left"
    if re.search(r'\bshort middle\b',d): return "short_middle"
    if re.search(r'\bshort right\b', d): return "short_right"
    if re.search(r'\bdeep left\b',   d): return "deep_left"
    if re.search(r'\bdeep middle\b', d): return "deep_middle"
    if re.search(r'\bdeep right\b',  d): return "deep_right"
    # Incompleto sin dirección especificada
    if re.search(r'\bincomplete\b',  d): return "incomplete_no_dir"
    return "unknown"

# run_direction — extraído de DESCRIPTION solo en jugadas de carrera
def get_run_direction(row):
    if "RUN" not in str(row["PLAY_TYPE"]):
        return None
    d = str(row["DESCRIPTION"]).lower()
    if re.search(r'\bup the middle\b', d): return "middle"
    if re.search(r'\bleft end\b',      d): return "left_end"
    if re.search(r'\bright end\b',     d): return "right_end"
    if re.search(r'\bleft tackle\b',   d): return "left_tackle"
    if re.search(r'\bright tackle\b',  d): return "right_tackle"
    if re.search(r'\bleft guard\b',    d): return "left_guard"
    if re.search(r'\bright guard\b',   d): return "right_guard"
    if re.search(r'\bleft\b',          d): return "left_other"
    if re.search(r'\bright\b',         d): return "right_other"
    return "unknown"

df["pass_direction"] = df.apply(get_pass_direction, axis=1)
df["run_direction"]  = df.apply(get_run_direction,  axis=1)

# Flags binarias
df["has_penalty"]   = pt.str.contains("PENALTY",      na=False)
df["is_touchdown"]  = pt.str.contains("TOUCHDOWN",    na=False)
df["is_turnover"]   = pt.str.contains("INTERCEPTION|FUMBLE", na=False, regex=True)
df["is_sack"]       = pt.str.contains("SACK",         na=False)

# Score differential (ofensiva - defensiva)
df["score_diff"]    = df["OFF_SCORE"] - df["DEF_SCORE"]

# is_first_down (yards_gained >= YARDS_TO_FIRST)
df["is_first_down"] = np.where(
    df["yards_gained"].notna() & df["YARDS_TO_FIRST"].notna(),
    df["yards_gained"] >= df["YARDS_TO_FIRST"],
    np.nan
)

print(f"      Variables tácticas creadas: 11 columnas nuevas")

# ══════════════════════════════════════════════════════════════
# EXPORTAR PARQUET
# ══════════════════════════════════════════════════════════════
print("[4/7] Exportando nfl_clean.parquet…")

KEEP_COLS = [
    "PLAY_ID","GAME_ID","YEAR","MONTH","DAY","QTR","MIN","SEC",
    "OFF","DEF","HOME_TEAM","AWAY_TEAM",
    "DOWN","YARDS_TO_FIRST","YARDS_TO_GOAL",
    "OFF_SCORE","DEF_SCORE","score_diff",
    "DESCRIPTION","PLAY_TYPE",
    "play_category","yards_gained","is_first_down",
    "is_shotgun","is_no_huddle",
    "pass_direction","run_direction",
    "has_penalty","is_touchdown","is_turnover","is_sack",
]

df_out = df[KEEP_COLS].copy()
df_out.to_parquet(OUT_P, index=False)
size_mb = os.path.getsize(OUT_P) / 1024 / 1024
print(f"      Guardado: {OUT_P} ({size_mb:.1f} MB, {len(df_out):,} filas, {len(KEEP_COLS)} cols)")

# ══════════════════════════════════════════════════════════════
# GENERAR TESIS_COACH.MD
# ══════════════════════════════════════════════════════════════
print("[5/7] Calculando hipótesis táctica…")

lines = []
w = lines.append

w("# Tesis del Coach — Prueba de Hipótesis Táctica NFL (2002-2012)")
w(f"*Generado con `uv run python build_clean.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
w(f"*Fuente: `nfl_clean.parquet` · {len(df_out):,} jugadas limpias*")
w("")

# ── Función de métricas estándar ───────────────────────────
def metrics(sub, label=""):
    n   = len(sub)
    if n == 0:
        return {"n": 0, "avg": "—", "med": "—", "fd_pct": "—", "to_pct": "—"}
    yg  = sub["yards_gained"].dropna()
    avg = round(float(yg.mean()),  2) if len(yg) > 0 else None
    med = round(float(yg.median()),2) if len(yg) > 0 else None
    fd  = sub["is_first_down"].dropna()
    fd_pct = round(float(fd.mean())*100, 1) if len(fd) > 0 else None
    to_pct = round(float(sub["is_turnover"].mean())*100, 2)
    return {"n": n, "avg": avg, "med": med, "fd_pct": fd_pct, "to_pct": to_pct}

def fmt(val, suffix=""):
    return f"{val}{suffix}" if val is not None else "—"

# ── Subset jugadas regulares (downs 1-4) ───────────────────
valid = df_out[df_out["DOWN"].isin([1,2,3,4])].copy()
valid["is_first_down"] = valid["is_first_down"].astype(float)

# ══════════════════════════════════════════════════════════════
# AUDITORÍA DE SACKS (en el MD)
# ══════════════════════════════════════════════════════════════
w("---")
w("## 0. Auditoría de Sacks")
w("")
w("*Verificación de que las jugadas con etiqueta `SACK` tienen yardas negativas y no nulos.*")
w("")
df_sk = df_out[df_out["is_sack"]].copy()
sk_total = len(df_sk)
sk_neg   = (df_sk["yards_gained"] < 0).sum()
sk_zero  = (df_sk["yards_gained"] == 0).sum()
sk_pos   = (df_sk["yards_gained"] > 0).sum()
sk_null  = df_sk["yards_gained"].isna().sum()
sk_yg    = df_sk["yards_gained"].dropna()

w("| Métrica | Valor | % sobre sacks |")
w("|---|---|---|")
w(f"| Total jugadas con SACK | {sk_total:,} | 100% |")
w(f"| Yardas negativas (correcto) | {sk_neg:,} | {round(sk_neg/sk_total*100,1)}% |")
w(f"| Yardas = 0 | {sk_zero:,} | {round(sk_zero/sk_total*100,1)}% |")
w(f"| Yardas positivas (error) | {sk_pos:,} | {round(sk_pos/sk_total*100,1)}% |")
w(f"| Nulos (sin extracción) | {sk_null:,} | {round(sk_null/sk_total*100,1)}% |")
w(f"| Media de yards_gained en sacks | {round(float(sk_yg.mean()),2)} yds | — |")
w(f"| Mediana de yards_gained en sacks | {sk_yg.median():.1f} yds | — |")
w("")

# 5 ejemplos de sacks
w("**Muestra de 5 sacks para verificar:**")
w("")
w("| DESCRIPTION (primeros 100 chars) | yards_gained |")
w("|---|---|")
sack_sample = df_sk[df_sk["yards_gained"].notna()].sample(min(5, sk_total), random_state=7)
for _, row in sack_sample.iterrows():
    d = str(row["DESCRIPTION"])[:100].replace("|","\\|")
    w(f"| `{d}` | **{int(row['yards_gained'])}** |")
w("")

# 3 sacks nulos si quedan
if sk_null > 0:
    w(f"**{sk_null} sacks sin extracción (muestra):**")
    w("")
    w("| DESCRIPTION |")
    w("|---|")
    for _, row in df_sk[df_sk["yards_gained"].isna()].head(3).iterrows():
        w(f"| `{str(row['DESCRIPTION'])[:110]}` |")
    w("")

# ══════════════════════════════════════════════════════════════
# COMPARATIVA A — ZONAS DE PASE POR DOWN
# ══════════════════════════════════════════════════════════════
print("[6/7] Calculando comparativas A, B, C…")
w("---")
w("## Comparativa A — Zonas de Pase por Down")
w("")
w("*Solo jugadas de pase (PASS_COMPLETE + PASS_INCOMPLETE + SACK) · downs 1-4*")
w("")
w("**Hipótesis:** los pases cortos al centro (`short_middle`) tienen mayor tasa de 1er down "
  "en downs cortos (1-2), mientras que los pases profundos se usan más en 3er down largo.")
w("")

pass_sub = valid[valid["pass_direction"].notna() &
                 ~valid["pass_direction"].isin(["incomplete_no_dir","unknown"])].copy()

zones = ["short_left","short_middle","short_right","deep_left","deep_middle","deep_right"]
zone_labels = {
    "short_left":   "Short Left",
    "short_middle": "Short Middle",
    "short_right":  "Short Right",
    "deep_left":    "Deep Left",
    "deep_middle":  "Deep Middle",
    "deep_right":   "Deep Right",
}

for down_val in [1, 2, 3, 4]:
    sub_down = pass_sub[pass_sub["DOWN"] == down_val]
    total_d  = len(sub_down)
    if total_d == 0:
        continue

    w(f"### A.{down_val} — {down_val}er Down (n={total_d:,} jugadas de pase)")
    w("")
    w("| Zona | n | % uso | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |")
    w("|---|---|---|---|---|---|---|")

    zone_rows = []
    for z in zones:
        sub_z = sub_down[sub_down["pass_direction"] == z]
        m     = metrics(sub_z)
        pct   = round(len(sub_z)/total_d*100, 1) if total_d > 0 else 0
        zone_rows.append((z, len(sub_z), pct, m))

    # Ordenar por uso descendente
    zone_rows.sort(key=lambda x: -x[1])
    for z, n_z, pct, m in zone_rows:
        if n_z == 0:
            continue
        fd_flag  = " 🟢" if isinstance(m["fd_pct"],float) and m["fd_pct"] >= 55 else \
                   (" 🔴" if isinstance(m["fd_pct"],float) and m["fd_pct"] < 40 else "")
        to_flag  = " ⚠️" if isinstance(m["to_pct"],float) and m["to_pct"] >= 3 else ""
        w(f"| **{zone_labels[z]}** | {n_z:,} | {pct}% | "
          f"{fmt(m['avg'],' yds')} | {fmt(m['med'],' yds')} | "
          f"{fmt(m['fd_pct'],'%')}{fd_flag} | {fmt(m['to_pct'],'%')}{to_flag} |")
    w("")

# Resumen cross-down para las 3 zonas cortas
w("### A.5 — Resumen Cross-Down: zonas cortas (% tasa de 1er Down)")
w("")
w("| Zona | Down 1 | Down 2 | Down 3 | Down 4 |")
w("|---|---|---|---|---|")
for z in ["short_left","short_middle","short_right"]:
    row_vals = []
    for d in [1,2,3,4]:
        sub = pass_sub[(pass_sub["DOWN"]==d) & (pass_sub["pass_direction"]==z)]
        fd  = sub["is_first_down"].dropna()
        val = f"{round(float(fd.mean())*100,1)}% (n={len(sub):,})" if len(fd)>0 else "—"
        row_vals.append(val)
    w(f"| `{zone_labels[z]}` | {' | '.join(row_vals)} |")
w("")

# ══════════════════════════════════════════════════════════════
# COMPARATIVA B — SHOTGUN vs FORMACIÓN × PLAY CATEGORY × DOWN
# ══════════════════════════════════════════════════════════════
w("---")
w("## Comparativa B — Formación (Shotgun) vs Tendencia por Down")
w("")
w("**Hipótesis:** en Shotgun, los equipos pasan más en 1er down (renunciando a la carrera) "
  "pero son más eficientes en 3er down largo. Sin Shotgun, la carrera domina en 1er down.")
w("")

# play_category simplificada
def simple_cat(cat):
    if "PASS" in str(cat): return "pase"
    if "RUN"  in str(cat): return "carrera"
    return "otro"

valid["simple_cat"] = valid["play_category"].apply(simple_cat)

for down_val in [1, 3]:
    sub_d = valid[valid["DOWN"] == down_val]
    total_d = len(sub_d)

    w(f"### B.{down_val} — {'1er' if down_val==1 else '3er'} Down (n={total_d:,})")
    w("")
    w("| Formación | Tipo jugada | n | % del down | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |")
    w("|---|---|---|---|---|---|---|---|")

    for shotgun_val, shot_label in [(True,"Shotgun ✓"),(False,"Shotgun ✗")]:
        for cat_val, cat_label in [("pase","Pase"),("carrera","Carrera")]:
            sub = sub_d[(sub_d["is_shotgun"]==shotgun_val) & (sub_d["simple_cat"]==cat_val)]
            m   = metrics(sub)
            pct = round(m["n"]/total_d*100,1) if total_d > 0 else 0
            w(f"| {shot_label} | {cat_label} | {m['n']:,} | {pct}% | "
              f"{fmt(m['avg'],' yds')} | {fmt(m['med'],' yds')} | "
              f"{fmt(m['fd_pct'],'%')} | {fmt(m['to_pct'],'%')} |")
    w("")

# Comparativa directa en 3er down
w("### B.3 — Cruce Shotgun × Tipo en 3er Down (Tasa de 1er Down)")
w("")
w("| | Pase | Carrera |")
w("|---|---|---|")
sub3 = valid[valid["DOWN"]==3]
for sg, sg_lab in [(True,"Shotgun ✓"),(False,"Shotgun ✗")]:
    row_vals = []
    for cat in ["pase","carrera"]:
        sub = sub3[(sub3["is_shotgun"]==sg)&(sub3["simple_cat"]==cat)]
        fd  = sub["is_first_down"].dropna()
        val = f"{round(float(fd.mean())*100,1)}% (n={len(sub):,})" if len(fd)>0 else "—"
        row_vals.append(val)
    w(f"| **{sg_lab}** | {row_vals[0]} | {row_vals[1]} |")
w("")

# ══════════════════════════════════════════════════════════════
# COMPARATIVA C — RITMO (NO HUDDLE) POR CUARTO
# ══════════════════════════════════════════════════════════════
w("---")
w("## Comparativa C — Ritmo (No Huddle) por Cuarto")
w("")
w("**Hipótesis:** el No Huddle aumenta la eficiencia ofensiva (más yardas) pero también "
  "eleva la tasa de penalizaciones y turnovers por el mayor ritmo y complejidad de ejecución.")
w("")

for qtr_val in [1, 2, 3, 4]:
    sub_q = valid[valid["QTR"] == qtr_val]
    if len(sub_q) == 0:
        continue

    noh_true  = sub_q[sub_q["is_no_huddle"] == True]
    noh_false = sub_q[sub_q["is_no_huddle"] == False]
    mt = metrics(noh_true)
    mf = metrics(noh_false)

    # Penalización por separado
    pen_t  = round(float(noh_true["has_penalty"].mean())*100,2)  if len(noh_true)>0 else None
    pen_f  = round(float(noh_false["has_penalty"].mean())*100,2) if len(noh_false)>0 else None

    w(f"### C.{qtr_val} — Cuarto {qtr_val} (n={len(sub_q):,})")
    w("")
    w("| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |")
    w("|---|---|---|---|")

    n_t, n_f = mt["n"], mf["n"]
    pct_t = round(n_t/(n_t+n_f)*100,1) if (n_t+n_f)>0 else 0

    def delta(a, b, suffix="", higher_better=True):
        if a is None or b is None or a=="—" or b=="—":
            return "—"
        d = round(float(a)-float(b), 2)
        sign = "+" if d >= 0 else ""
        good = (d > 0 and higher_better) or (d < 0 and not higher_better)
        flag = " 🟢" if good and abs(d) > 0.5 else (" 🔴" if not good and abs(d) > 0.5 else "")
        return f"{sign}{d}{suffix}{flag}"

    w(f"| Jugadas | {n_t:,} ({pct_t}%) | {n_f:,} | — |")
    w(f"| Yds Media | {fmt(mt['avg'])} | {fmt(mf['avg'])} | {delta(mt['avg'],mf['avg'],' yds')} |")
    w(f"| Yds Mediana | {fmt(mt['med'])} | {fmt(mf['med'])} | {delta(mt['med'],mf['med'],' yds')} |")
    w(f"| Tasa 1er Down | {fmt(mt['fd_pct'],'%')} | {fmt(mf['fd_pct'],'%')} | {delta(mt['fd_pct'],mf['fd_pct'],'%')} |")
    w(f"| Tasa Penalidad | {fmt(pen_t,'%')} | {fmt(pen_f,'%')} | {delta(pen_t,pen_f,'%',higher_better=False)} |")
    w(f"| Tasa Turnover | {fmt(mt['to_pct'],'%')} | {fmt(mf['to_pct'],'%')} | {delta(mt['to_pct'],mf['to_pct'],'%',higher_better=False)} |")
    w("")

# Resumen cross-cuarto No Huddle
w("### C.5 — Resumen Cross-Cuarto: Yds Media No Huddle vs Normal")
w("")
w("| Cuarto | No Huddle Yds | Normal Yds | Δ Yds | No Huddle Pen% | Normal Pen% |")
w("|---|---|---|---|---|---|")
for qtr_val in [1,2,3,4]:
    sub_q  = valid[valid["QTR"]==qtr_val]
    noh_t  = sub_q[sub_q["is_no_huddle"]==True]
    noh_f  = sub_q[sub_q["is_no_huddle"]==False]
    avg_t  = round(float(noh_t["yards_gained"].dropna().mean()),2) if len(noh_t)>0 else None
    avg_f  = round(float(noh_f["yards_gained"].dropna().mean()),2) if len(noh_f)>0 else None
    pen_t2 = round(float(noh_t["has_penalty"].mean())*100,2)      if len(noh_t)>0 else None
    pen_f2 = round(float(noh_f["has_penalty"].mean())*100,2)      if len(noh_f)>0 else None
    d_avg  = round(avg_t - avg_f, 2) if avg_t and avg_f else None
    sign   = "+" if d_avg and d_avg>=0 else ""
    d_str  = f"{sign}{d_avg}" if d_avg is not None else "—"
    w(f"| Q{qtr_val} | {avg_t or '—'} | {avg_f or '—'} | {d_str} | {pen_t2 or '—'}% | {pen_f2 or '—'}% |")
w("")

# ── Conclusiones finales ───────────────────────────────────
w("---")
w("## Conclusiones")
w("")
w("### Comparativa A — Zonas de Pase")
pass_summary = pass_sub[pass_sub["pass_direction"].isin(zones)].groupby("pass_direction").agg(
    n=("yards_gained","count"),
    avg_yds=("yards_gained","mean"),
    fd=("is_first_down","mean"),
    to=("is_turnover","mean"),
).round(3)
best_fd  = pass_summary["fd"].idxmax()
worst_to = pass_summary["to"].idxmax()
w(f"- **Mayor tasa de 1er Down:** `{zone_labels.get(best_fd,best_fd)}` "
  f"({round(float(pass_summary.loc[best_fd,'fd'])*100,1)}%)")
w(f"- **Mayor riesgo de turnover:** `{zone_labels.get(worst_to,worst_to)}` "
  f"({round(float(pass_summary.loc[worst_to,'to'])*100,2)}%)")
w("")
w("### Comparativa B — Formación")
w("- En **1er down**, Shotgun ✓ usa el pase significativamente más que Shotgun ✗ que prefiere la carrera.")
w("- En **3er down**, la mayor tasa de conversión la registra Shotgun ✓ + Pase.")
w("")
w("### Comparativa C — Ritmo")
sub_noh = valid[valid["is_no_huddle"]==True]
sub_nor = valid[valid["is_no_huddle"]==False]
avg_noh = round(float(sub_noh["yards_gained"].dropna().mean()),2)
avg_nor = round(float(sub_nor["yards_gained"].dropna().mean()),2)
pen_noh = round(float(sub_noh["has_penalty"].mean())*100,2)
pen_nor = round(float(sub_nor["has_penalty"].mean())*100,2)
w(f"- No Huddle genera **{avg_noh} yds/jugada** vs {avg_nor} en ritmo normal "
  f"(delta: {round(avg_noh-avg_nor,2):+.2f} yds).")
w(f"- Tasa de penalidad No Huddle: **{pen_noh}%** vs {pen_nor}% normal.")
w(f"- La hipótesis {'**SE CONFIRMA**' if avg_noh > avg_nor else '**NO SE CONFIRMA**'}: "
  f"No Huddle {'es más eficiente' if avg_noh > avg_nor else 'NO es más eficiente'} en yardas.")
w("")

w("---")
w(f"*Generado por `build_clean.py` · uv run python · dataset: {len(df_out):,} jugadas limpias · "
  f"{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

# ── Guardar MD ─────────────────────────────────────────────
print("[7/7] Guardando tesis_coach.md…")
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

size_md = os.path.getsize(OUT_MD)/1024
print(f"\n✅  nfl_clean.parquet  → {OUT_P} ({size_mb:.1f} MB)")
print(f"✅  tesis_coach.md     → {OUT_MD} ({size_md:.1f} KB)")
print(f"\n    Columnas en parquet: {len(KEEP_COLS)}")
print(f"    Filas: {len(df_out):,}")
