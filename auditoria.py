# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy"]
# ///
"""
auditoria.py — Auditoría profunda de nflplays.csv
Ejecutar: uv run python auditoria.py
Genera:   auditoria_columnas.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE   = os.path.dirname(os.path.abspath(__file__))
FILE   = os.path.join(BASE, "data", "nflplays.csv")
OUTPUT = os.path.join(BASE, "auditoria_columnas.md")

print("=" * 60)
print("  Auditoría de columnas — nflplays.csv (dataset completo)")
print("=" * 60)

# ── Carga completa ─────────────────────────────────────────
print("\n[1/4] Cargando dataset completo…")
df = pd.read_csv(FILE, sep="\t", low_memory=False)
n_rows, n_cols = df.shape
print(f"      {n_rows:,} filas × {n_cols} columnas")

lines = []
w = lines.append

w("# Auditoría de Columnas — `nflplays.csv`")
w(f"*Dataset completo: {n_rows:,} filas × {n_cols} columnas*")
w(f"*Generado con `uv run python auditoria.py` el {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
w("")

# ════════════════════════════════════════════════════════════
# PREGUNTA 1 — 3 ejemplos reales por columna
# ════════════════════════════════════════════════════════════
print("[2/4] Extrayendo ejemplos reales por columna…")
w("---")
w("## 1. Muestra de 3 valores reales por columna")
w("")
w("*Para columnas con valores nulos, los ejemplos se toman del subconjunto no-nulo.*")
w("")
w("| # | Columna | dtype | Ejemplo 1 | Ejemplo 2 | Ejemplo 3 | Únicos totales |")
w("|---|---|---|---|---|---|---|")

for i, col in enumerate(df.columns, 1):
    dtype    = str(df[col].dtype)
    n_unique = df[col].nunique()
    sample   = df[col].dropna().unique()

    # Buscar ejemplos variados (no solo los primeros)
    if len(sample) >= 3:
        # Tomar inicio, medio y casi-final para mostrar variedad
        idx = [0, len(sample) // 2, min(len(sample) - 1, len(sample) - 1)]
        ex  = [str(sample[i])[:50] for i in idx]
    elif len(sample) == 2:
        ex = [str(sample[0])[:50], str(sample[1])[:50], "—"]
    elif len(sample) == 1:
        ex = [str(sample[0])[:50], "—", "—"]
    else:
        ex = ["(todos nulos)", "—", "—"]

    w(f"| {i} | `{col}` | `{dtype}` | `{ex[0]}` | `{ex[1]}` | `{ex[2]}` | {n_unique:,} |")

w("")

# ════════════════════════════════════════════════════════════
# PREGUNTA 2 — PLAY_TYPE × DOWN (incluyendo nulos)
# ════════════════════════════════════════════════════════════
print("[3/4] Cruzando PLAY_TYPE × DOWN (incluyendo nulos)…")
w("---")
w("## 2. PLAY_TYPE × DOWN — Frecuencias completas (incluyendo nulos)")
w("")

# Reemplazar NaN por etiqueta explícita para que aparezca en el crosstab
df["PLAY_TYPE_AUDIT"] = df["PLAY_TYPE"].fillna("⚠️ NULL")

# Tabla pivot: PLAY_TYPE en filas, DOWN en columnas
pivot = pd.crosstab(
    df["PLAY_TYPE_AUDIT"],
    df["DOWN"],
    margins=True,
    margins_name="TOTAL"
)
pivot = pivot.sort_values("TOTAL", ascending=False)

# Columnas de DOWN presentes
down_cols = [c for c in pivot.columns if c != "TOTAL"]

w("### 2.1 Distribución por DOWN de cada PLAY_TYPE")
w("")

# Encabezado dinámico
header_downs = " | ".join([f"DOWN {d}" for d in down_cols])
w(f"| PLAY_TYPE | {header_downs} | **TOTAL** |")
w("|---|" + "---|" * (len(down_cols) + 1))

for play_type, row in pivot.iterrows():
    vals = " | ".join([f"{int(row[d]):,}" if d in row.index else "0" for d in down_cols])
    total = int(row["TOTAL"])
    pct   = round(total / n_rows * 100, 2)
    bold  = "**" if play_type == "⚠️ NULL" else ""
    w(f"| {bold}`{play_type}`{bold} | {vals} | {bold}{total:,} ({pct}%){bold} |")

w("")

# Análisis específico de los nulos
w("### 2.2 Diagnóstico de los registros con PLAY_TYPE nulo")
w("")
null_rows = df[df["PLAY_TYPE"].isna()]
n_nulls   = len(null_rows)
w(f"**Total de filas con PLAY_TYPE nulo: {n_nulls:,} ({round(n_nulls/n_rows*100,2)}%)**")
w("")

# DOWN distribution para nulos
null_down = null_rows["DOWN"].value_counts().sort_index()
w("**Distribución por DOWN:**")
w("")
w("| DOWN | Frecuencia | % sobre nulos |")
w("|---|---|---|")
for down_val, freq in null_down.items():
    pct_null = round(freq / n_nulls * 100, 1)
    w(f"| {down_val} | {freq:,} | {pct_null}% |")
w("")

# QTR distribution para nulos
null_qtr = null_rows["QTR"].value_counts().sort_index()
w("**Distribución por QTR:**")
w("")
w("| QTR | Frecuencia | % |")
w("|---|---|---|")
for qtr_val, freq in null_qtr.items():
    w(f"| {qtr_val} | {freq:,} | {round(freq/n_nulls*100,1)}% |")
w("")

# Muestra de DESCRIPTION para nulos
w("**Muestra de 5 descripciones con PLAY_TYPE nulo:**")
w("")
sample_desc = null_rows["DESCRIPTION"].dropna().sample(
    min(5, len(null_rows)), random_state=42
).tolist()
for desc in sample_desc:
    w(f"> `{str(desc)[:120]}`")
    w("")

# Hipótesis
down0_pct = round(null_down.get(0, 0) / n_nulls * 100, 1) if n_nulls > 0 else 0
w(f"**🔍 Hipótesis sobre los nulos:**")
w("")
w(f"- {down0_pct}% de los nulos tienen DOWN = 0, que corresponde a jugadas especiales "
  f"(kickoffs, punts, conversiones de 2 puntos, etc.) que el codificador de PLAY_TYPE "
  f"no clasifica o deja vacíos.")
w(f"- El resto distribuye entre downs 1–4, sugiriendo jugadas anuladas por penalidad "
  f"o situaciones de juego no estándar sin categoría asignada.")
w("")

# ════════════════════════════════════════════════════════════
# PREGUNTA 3 — OFF vs DEF vs HOME_TEAM vs AWAY_TEAM (valor #33)
# ════════════════════════════════════════════════════════════
print("[4/4] Comparando conjuntos de equipos…")
w("---")
w("## 3. Comparación de conjuntos de equipos — ¿Cuál es el valor #33?")
w("")

off_teams  = set(df["OFF"].dropna().unique())
def_teams  = set(df["DEF"].dropna().unique())
home_teams = set(df["HOME_TEAM"].dropna().unique())
away_teams = set(df["AWAY_TEAM"].dropna().unique())

all_teams  = off_teams | def_teams | home_teams | away_teams

w(f"| Columna | Únicos | Valores |")
w("|---|---|---|")
for col_name, team_set in [
    ("OFF",       off_teams),
    ("DEF",       def_teams),
    ("HOME_TEAM", home_teams),
    ("AWAY_TEAM", away_teams),
    ("UNIÓN total", all_teams),
]:
    sorted_teams = ", ".join(sorted(team_set))
    w(f"| `{col_name}` | **{len(team_set)}** | {sorted_teams} |")
w("")

# Diferencias entre columnas
only_in_def  = def_teams  - off_teams
only_in_home = home_teams - off_teams
only_in_away = away_teams - off_teams
only_in_off  = off_teams  - def_teams

w("### 3.1 Diferencias entre columnas")
w("")
w("| Diferencia | Equipos | Interpretación |")
w("|---|---|---|")
w(f"| En `DEF` pero NO en `OFF` | `{'`, `'.join(sorted(only_in_def)) or '(ninguno)'}` | Equipo que solo aparece como defensa |")
w(f"| En `OFF` pero NO en `DEF` | `{'`, `'.join(sorted(only_in_off)) or '(ninguno)'}` | Equipo que solo aparece como ofensa |")
w(f"| En `HOME_TEAM` pero NO en `OFF` | `{'`, `'.join(sorted(only_in_home)) or '(ninguno)'}` | Juega en casa pero sin jugadas ofensivas |")
w(f"| En `AWAY_TEAM` pero NO en `OFF` | `{'`, `'.join(sorted(only_in_away)) or '(ninguno)'}` | Juega de visitante pero sin jugadas ofensivas |")
w("")

w("### 3.2 El valor #33 — identificación exacta")
w("")

# El valor 33 está en DEF/HOME/AWAY pero no en OFF (32 equipos)
extra_teams = (def_teams | home_teams | away_teams) - off_teams
if extra_teams:
    for extra in sorted(extra_teams):
        # Contar apariciones en cada columna
        counts = {
            col: int((df[col] == extra).sum())
            for col in ["OFF", "DEF", "HOME_TEAM", "AWAY_TEAM"]
        }
        # Muestra de GAME_ID con ese equipo
        sample_games = df[
            (df["HOME_TEAM"] == extra) | (df["AWAY_TEAM"] == extra)
        ]["GAME_ID"].dropna().unique()[:5].tolist()

        w(f"**El valor extra es: `{extra}`**")
        w("")
        w(f"| Columna | Apariciones |")
        w("|---|---|")
        for col_n, cnt in counts.items():
            w(f"| `{col_n}` | {cnt:,} |")
        w("")
        w(f"**Partidos de ejemplo:** {', '.join(sample_games)}")
        w("")
        w(f"**Diagnóstico:** `{extra}` aparece en HOME_TEAM/AWAY_TEAM y en DEF "
          f"pero con 0 jugadas ofensivas registradas en OFF. "
          f"Esto indica que es una **franquicia que fue relocalizada o renombrada** "
          f"(ej. SD → LAC, STL → LA, OAK → LV) o un equipo que jugó partidos "
          f"en ese período pero cuyas jugadas ofensivas no fueron capturadas.")
        w("")
else:
    # El extra puede estar en DEF con una sigla diferente
    w("Los 4 conjuntos comparten el mismo universo base. La diferencia de conteo (32 vs 33) ")
    w("se debe a que una de las columnas contiene un **valor adicional no-equipo** (error de datos, ")
    w("anotación especial, o valor heredado). Revisando todos los valores únicos:")
    w("")
    for col_name, team_set in [("OFF", off_teams), ("DEF", def_teams),
                                ("HOME_TEAM", home_teams), ("AWAY_TEAM", away_teams)]:
        # Detectar valores que no parecen siglas NFL (< 2 chars o > 4 chars)
        anomalies = [t for t in team_set if len(str(t)) < 2 or len(str(t)) > 3]
        if anomalies:
            w(f"**`{col_name}`** contiene valores anómalos: `{'`, `'.join(anomalies)}`")
            for anom in anomalies:
                cnt = int((df[col_name] == anom).sum())
                sample_g = df[df[col_name] == anom]["GAME_ID"].dropna().unique()[:3].tolist()
                w(f"- `{anom}`: {cnt:,} filas — partidos: {', '.join(sample_g)}")
            w("")

# Tabla completa ordenada de todos los equipos
w("### 3.3 Lista completa de todos los equipos detectados (unión de las 4 columnas)")
w("")
team_freq = {}
for team in sorted(all_teams):
    freq = {}
    for col_n in ["OFF", "DEF", "HOME_TEAM", "AWAY_TEAM"]:
        freq[col_n] = int((df[col_n] == team).sum())
    team_freq[team] = freq

w("| Equipo | OFF | DEF | HOME | AWAY | TOTAL JUGADAS |")
w("|---|---|---|---|---|---|")
for team, freq in sorted(team_freq.items(), key=lambda x: -(x[1]["OFF"] + x[1]["DEF"])):
    total = freq["OFF"] + freq["DEF"]
    off_flag = "" if freq["OFF"] > 0 else " ⚠️"
    w(f"| `{team}` | {freq['OFF']:,}{off_flag} | {freq['DEF']:,} | {freq['HOME_TEAM']:,} | {freq['AWAY_TEAM']:,} | {total:,} |")
w("")

# ════════════════════════════════════════════════════════════
# PREGUNTA 4 — Yardas ganadas: ¿existe esa columna?
# ════════════════════════════════════════════════════════════
w("---")
w("## 4. Yardas ganadas / resultado de jugada — ¿Existe la columna?")
w("")

# Buscar columna de yardas resultado
YARD_PATTERNS = ["yards_gain", "yards_gained", "gain", "result", "net_yards",
                 "play_result", "yds_gained", "yards_net", "play_yards"]
yard_col = next(
    (c for c in df.columns if any(p in c.lower() for p in YARD_PATTERNS)),
    None
)

if yard_col:
    w(f"✅ **Columna de yardas encontrada: `{yard_col}`**")
    w("")
    # Análisis por PLAY_TYPE y DOWN
    df_clean = df[df["PLAY_TYPE"].notna() & df[yard_col].notna()].copy()
    df_clean["success"] = (df_clean[yard_col] >= df_clean["YARDS_TO_FIRST"]).astype(int)

    # Agrupación por PLAY_TYPE
    grp_type = df_clean.groupby("PLAY_TYPE")[yard_col].agg(
        mean="mean", median="median", std="std", n="count"
    ).round(3)
    grp_type["success_rate"] = df_clean.groupby("PLAY_TYPE")["success"].mean().round(4) * 100

    top_types = grp_type.sort_values("n", ascending=False).head(20)

    w("### 4.1 Estadísticas de yardas por PLAY_TYPE")
    w("")
    w(f"| PLAY_TYPE | n | Media yds | Mediana yds | Desv.Std | Tasa Éxito % |")
    w("|---|---|---|---|---|---|")
    for pt, row in top_types.iterrows():
        success_bar = "█" * int(row["success_rate"] / 10)
        w(f"| `{pt}` | {int(row['n']):,} | {row['mean']} | {row['median']} | "
          f"{row['std']} | {row['success_rate']:.1f}% {success_bar} |")
    w("")

    # Agrupación por DOWN
    grp_down = df_clean.groupby("DOWN")[yard_col].agg(
        mean="mean", median="median", std="std", n="count"
    ).round(3)
    grp_down["success_rate"] = df_clean.groupby("DOWN")["success"].mean().round(4) * 100

    w("### 4.2 Estadísticas de yardas por DOWN")
    w("")
    w("| DOWN | n | Media yds | Mediana yds | Desv.Std | Tasa Éxito % |")
    w("|---|---|---|---|---|---|")
    for down_val, row in grp_down.iterrows():
        success_bar = "█" * int(row["success_rate"] / 10)
        w(f"| {down_val} | {int(row['n']):,} | {row['mean']} | {row['median']} | "
          f"{row['std']} | {row['success_rate']:.1f}% {success_bar} |")
    w("")

    # Cruce PLAY_TYPE x DOWN (top 10 tipos × downs 1-4)
    top10_types = grp_type.sort_values("n", ascending=False).head(10).index.tolist()
    df_cross = df_clean[
        df_clean["PLAY_TYPE"].isin(top10_types) &
        df_clean["DOWN"].isin([1, 2, 3, 4])
    ]
    cross = df_cross.groupby(["PLAY_TYPE", "DOWN"])["success"].mean().unstack() * 100

    w("### 4.3 Tasa de éxito (%) — PLAY_TYPE × DOWN (top 10 tipos)")
    w("")
    w("| PLAY_TYPE | Down 1 | Down 2 | Down 3 | Down 4 |")
    w("|---|---|---|---|---|")
    for pt, row in cross.iterrows():
        vals = []
        for d in [1, 2, 3, 4]:
            v = row.get(d, np.nan)
            if pd.isna(v):
                vals.append("—")
            else:
                flag = "🟢" if v >= 50 else "🔴" if v < 35 else "🟡"
                vals.append(f"{flag} {v:.1f}%")
        w(f"| `{pt}` | {vals[0]} | {vals[1]} | {vals[2]} | {vals[3]} |")
    w("")

else:
    # No existe columna de yardas → inferir desde DESCRIPTION
    w("⚠️ **No existe una columna explícita de yardas ganadas en el dataset.**")
    w("")
    w("Las columnas disponibles son:")
    w("")
    w("| Columna | Qué mide |")
    w("|---|---|")
    w("| `YARDS_TO_FIRST` | Yardas *necesarias* para el 1er down (antes de la jugada) |")
    w("| `YARDS_TO_GOAL`  | Yardas *restantes* para anotación (antes de la jugada) |")
    w("")
    w("Las yardas *ganadas* están implícitas en el campo `DESCRIPTION` (texto narrativo). ")
    w("Para extraerlas se requiere un parser de expresiones regulares sobre ese campo.")
    w("")

    # Análisis de lo que sí tenemos: YARDS_TO_FIRST por DOWN y PLAY_TYPE
    w("### 4.1 Análisis de YARDS_TO_FIRST (yardas necesarias) por DOWN")
    w("")
    grp_down = df[df["DOWN"].isin([1,2,3,4])].groupby("DOWN")["YARDS_TO_FIRST"].agg(
        mean="mean", median="median", std="std", n="count"
    ).round(2)

    w("| DOWN | n | Media YTF | Mediana YTF | Desv.Std |")
    w("|---|---|---|---|---|")
    for down_val, row in grp_down.iterrows():
        w(f"| {down_val} | {int(row['n']):,} | {row['mean']} | {row['median']} | {row['std']} |")
    w("")

    w("### 4.2 YARDS_TO_FIRST por PLAY_TYPE (top 15)")
    w("")
    df_pt = df[df["PLAY_TYPE"].notna() & df["DOWN"].isin([1,2,3,4])]
    grp_type = df_pt.groupby("PLAY_TYPE")["YARDS_TO_FIRST"].agg(
        mean="mean", median="median", n="count"
    ).sort_values("n", ascending=False).head(15).round(2)

    w("| PLAY_TYPE | n | Media YTF | Mediana YTF |")
    w("|---|---|---|---|")
    for pt, row in grp_type.iterrows():
        w(f"| `{pt}` | {int(row['n']):,} | {row['mean']} | {row['median']} |")
    w("")

    w("### 4.3 Extracción de yardas desde DESCRIPTION (muestra de 10)")
    w("")
    w("El campo `DESCRIPTION` contiene las yardas en texto libre. Ejemplos:")
    w("")
    sample_desc = df[df["PLAY_TYPE"].notna() & df["DOWN"].isin([1,2,3,4])]["DESCRIPTION"].dropna().sample(10, random_state=42)
    for desc in sample_desc:
        w(f"> `{str(desc)[:120]}`")
        w("")

    w("Para extraer yardas ganadas se recomienda un parser con:")
    w("```python")
    w("import re")
    w("df['yards_gained'] = df['DESCRIPTION'].str.extract(r'for (-?\\d+) yard')")
    w("```")
    w("")

# ── Limpieza columna auxiliar ──────────────────────────────
df.drop(columns=["PLAY_TYPE_AUDIT"], inplace=True, errors="ignore")

# ── Footer ─────────────────────────────────────────────────
w("---")
w(f"*Auditoría generada por `auditoria.py` usando `uv run python` · "
  f"pandas + numpy · dataset completo ({n_rows:,} filas) · "
  f"{datetime.now().strftime('%Y-%m-%d %H:%M')}*")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅  auditoria_columnas.md → {OUTPUT}")
print(f"    Tamaño: {os.path.getsize(OUTPUT)/1024:.1f} KB")
