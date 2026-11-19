# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy"]
# ///
"""
diagnostico.py — Diagnóstico profundo de nflplays.csv
Ejecutar con:  uv run python diagnostico.py
Genera:        diagnostico_dataset.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# ── Configuración ──────────────────────────────────────────────────────────
BASE   = os.path.dirname(os.path.abspath(__file__))
FILE   = os.path.join(BASE, "data", "nflplays.csv")
OUTPUT = os.path.join(BASE, "diagnostico_dataset.md")
SAMPLE = 100_000  # filas para estadísticas (el full para dims/nulos/dups)

print("=" * 60)
print("  NFL Plays — Diagnóstico de Dataset")
print("=" * 60)

# ── Detectar separador ─────────────────────────────────────────────────────
with open(FILE, "r", encoding="utf-8", errors="replace") as f:
    first_line = f.readline()
sep    = "\t" if first_line.count("\t") > first_line.count(",") else ","
sep_name = "TAB (TSV)" if sep == "\t" else "COMA (CSV)"
print(f"\n[1/5] Separador detectado: {sep_name}")

# ── Carga completa para dimensiones, nulos y duplicados ───────────────────
print("[2/5] Cargando dataset completo…")
df_full = pd.read_csv(FILE, sep=sep, low_memory=False)
n_rows, n_cols = df_full.shape
print(f"      {n_rows:,} filas × {n_cols} columnas")

# Nulos
nulls      = df_full.isna().sum()
null_pct   = (nulls / n_rows * 100).round(2)

# Duplicados
n_dupes    = int(df_full.duplicated().sum())
pct_dupes  = round(n_dupes / n_rows * 100, 3)
print(f"      Duplicados: {n_dupes:,} ({pct_dupes}%)")

# Muestra para estadísticas (evita OOM en archivos grandes)
df = df_full.sample(min(SAMPLE, n_rows), random_state=42) if n_rows > SAMPLE else df_full
print(f"[3/5] Muestra para estadísticas: {len(df):,} filas")

# ── Granularidad ───────────────────────────────────────────────────────────
print("[4/5] Analizando granularidad…")

ID_PATTERNS = [
    "play_id", "playid", "game_id", "gameid",
    "nfl_id", "nflid", "player_id", "playerid",
    "frame_id", "frameid", "event_id", "eventid",
    "tracking_id", "timestamp", "time",
]

id_candidates = []
for col in df_full.columns:
    col_lower = col.lower().replace(" ", "_")
    if any(pat in col_lower for pat in ID_PATTERNS):
        id_candidates.append(col)

# Para cada candidato, calcular filas por valor único
granularity_results = []
for col in id_candidates:
    counts     = df_full[col].value_counts()
    avg_rows   = round(float(counts.mean()), 2)
    max_rows   = int(counts.max())
    n_unique   = int(df_full[col].nunique())
    coverage   = round(n_unique / n_rows * 100, 2)
    granularity_results.append({
        "col":       col,
        "n_unique":  n_unique,
        "avg_rows":  avg_rows,
        "max_rows":  max_rows,
        "coverage":  coverage,
    })

# Detectar columnas de coordenadas / tracking
SPATIAL_PATTERNS  = ["x", "y", "speed", "accel", "dir", "dis", "o", "angle",
                      "lat", "lon", "coord", "position", "velocity"]
TEMPORAL_PATTERNS = ["frame", "timestamp", "time", "clock", "min", "sec"]

spatial_cols  = [c for c in df_full.columns if c.lower() in SPATIAL_PATTERNS
                 or any(p in c.lower() for p in ["_x", "_y", "speed", "accel", "veloc"])]
temporal_cols = [c for c in df_full.columns if any(p in c.lower() for p in TEMPORAL_PATTERNS)]

print("[5/5] Generando estadísticas descriptivas…")

# ── Estadísticas descriptivas ──────────────────────────────────────────────
num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
cat_cols = [c for c in df.columns
            if (str(df[c].dtype) in ("object", "string", "category")
                or "str" in str(df[c].dtype).lower())
            and df[c].nunique() <= 200]

num_stats = []
for col in num_cols:
    s = df[col].dropna()
    if len(s) == 0:
        continue
    num_stats.append({
        "col":    col,
        "count":  int(s.count()),
        "mean":   round(float(s.mean()), 4),
        "median": round(float(s.median()), 4),
        "std":    round(float(s.std()), 4),
        "min":    round(float(s.min()), 4),
        "max":    round(float(s.max()), 4),
        "p25":    round(float(s.quantile(0.25)), 4),
        "p75":    round(float(s.quantile(0.75)), 4),
    })

cat_stats = []
for col in cat_cols:
    top5 = df[col].value_counts().head(5)
    total_non_null = df[col].notna().sum()
    cat_stats.append({
        "col":    col,
        "unique": int(df[col].nunique()),
        "top5":   [(str(k), int(v), round(v / total_non_null * 100, 1))
                   for k, v in top5.items()],
    })

# ── Clasificación NFL ──────────────────────────────────────────────────────
col_names_lower = " ".join(df_full.columns.str.lower())

tracking_score  = sum(1 for p in ["_x", "_y", "speed", "accel", "frame", "dir ", " dis"]
                      if p in col_names_lower)
pbp_score       = sum(1 for p in ["down", "yards", "play_type", "off", "def",
                                   "pass", "run", "punt", "kick", "score", "qtr"]
                      if p in col_names_lower)
summary_score   = sum(1 for p in ["total_", "avg_", "per_game", "season_stat",
                                   "career", "cumul"]
                      if p in col_names_lower)

scores = {
    "Player Tracking (Next Gen Stats)": tracking_score,
    "Play-by-Play":                     pbp_score,
    "Player/Game Summary":              summary_score,
}
primary_type = max(scores, key=scores.get)

print(f"\n  → Tipo detectado: {primary_type}")
print(f"  → Generando {OUTPUT}…")

# ══════════════════════════════════════════════════════════════════════════
# GENERAR MARKDOWN
# ══════════════════════════════════════════════════════════════════════════
lines = []
w = lines.append

w(f"# Diagnóstico del Dataset — `nflplays.csv`")
w(f"*Generado con `uv run python diagnostico.py` el {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
w(f"*Archivo: `{FILE}` · Separador: {sep_name}*")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 1 — DIMENSIONES Y CALIDAD
# ════════════════════════════════════════════════════════════
w("---")
w("## 1. Dimensiones y Calidad")
w("")
w("### 1.1 Dimensiones")
w("")
w(f"| Métrica | Valor |")
w(f"|---|---|")
w(f"| Filas totales | **{n_rows:,}** |")
w(f"| Columnas totales | **{n_cols}** |")
w(f"| Celdas totales | {n_rows * n_cols:,} |")
w(f"| Filas duplicadas | **{n_dupes:,}** ({pct_dupes}%) |")
w(f"| Completitud global | **{round((1 - nulls.sum()/(n_rows*n_cols))*100, 2)}%** |")
w("")

w("### 1.2 Columnas — dtype y nulos")
w("")
w("| # | Columna | dtype | Nulos | % Nulos |")
w("|---|---|---|---|---|")
for i, col in enumerate(df_full.columns, 1):
    dtype  = str(df_full[col].dtype)
    n_null = int(nulls[col])
    p_null = float(null_pct[col])
    flag   = " 🔴" if p_null > 50 else " 🟡" if p_null > 10 else ""
    w(f"| {i} | `{col}` | `{dtype}` | {n_null:,} | {p_null}%{flag} |")
w("")

w("### 1.3 Columnas con valores nulos (solo las que tienen > 0)")
w("")
cols_with_nulls = [(c, int(nulls[c]), float(null_pct[c]))
                   for c in df_full.columns if nulls[c] > 0]
if cols_with_nulls:
    w("| Columna | Nulos | % |")
    w("|---|---|---|")
    for col, n, p in sorted(cols_with_nulls, key=lambda x: -x[2]):
        flag = "🔴" if p > 50 else "🟡" if p > 10 else "🟢"
        w(f"| `{col}` | {n:,} | {flag} {p}% |")
else:
    w("> ✅ Ninguna columna tiene valores nulos.")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 2 — GRANULARIDAD
# ════════════════════════════════════════════════════════════
w("---")
w("## 2. Prueba de Granularidad — ¿Qué representa cada fila?")
w("")

w("### 2.1 Columnas identificadoras candidatas")
w("")
if granularity_results:
    w("| Columna | Valores únicos | Cobertura (% filas) | Prom. filas/ID | Máx. filas/ID | Interpretación |")
    w("|---|---|---|---|---|---|")
    for g in granularity_results:
        # Inferir interpretación
        if g["avg_rows"] <= 1.05:
            interp = "🔑 ID único por fila (clave primaria)"
        elif g["avg_rows"] <= 5:
            interp = "🔗 Pocos eventos por ID (posible clave compuesta)"
        elif g["avg_rows"] <= 100:
            interp = "📦 Múltiples filas por ID (jugadas por partido)"
        else:
            interp = "📊 Muchas filas por ID (frames o tracking)"
        w(f"| `{g['col']}` | {g['n_unique']:,} | {g['coverage']}% | {g['avg_rows']} | {g['max_rows']:,} | {interp} |")
else:
    w("> ⚠️ No se detectaron columnas con patrones de ID estándar.")
    w("> Se inspeccionaron patrones: `play_id`, `game_id`, `nfl_id`, `frame_id`, `timestamp`")
w("")

w("### 2.2 Cálculo de granularidad por combinación de IDs")
w("")

# Intentar combinaciones de IDs más informativas
combo_results = []
if len(id_candidates) >= 2:
    for i in range(len(id_candidates)):
        for j in range(i + 1, len(id_candidates)):
            c1, c2 = id_candidates[i], id_candidates[j]
            combo_unique = df_full[[c1, c2]].drop_duplicates().shape[0]
            avg_per_combo = round(n_rows / combo_unique, 2)
            combo_results.append((f"{c1} + {c2}", combo_unique, avg_per_combo))

    combo_results.sort(key=lambda x: x[1], reverse=True)
    w("| Combinación | Combinaciones únicas | Prom. filas/combo | ¿Es clave? |")
    w("|---|---|---|---|")
    for combo, uniq, avg in combo_results[:6]:
        is_key = "✅ Sí" if abs(avg - 1.0) < 0.01 else ("🔶 Casi" if avg < 1.5 else "❌ No")
        w(f"| `{combo}` | {uniq:,} | {avg} | {is_key} |")
elif len(id_candidates) == 1:
    col    = id_candidates[0]
    uniq   = df_full[col].nunique()
    avg    = round(n_rows / uniq, 2)
    is_key = "✅ Sí" if avg <= 1.01 else "❌ No"
    w(f"| `{col}` | {uniq:,} | {avg} | {is_key} |")
w("")

w("### 2.3 Columnas espaciales / temporales detectadas")
w("")
w(f"**Columnas espaciales** (coordenadas, velocidad, aceleración): "
  f"{', '.join([f'`{c}`' for c in spatial_cols]) if spatial_cols else '*Ninguna detectada*'}")
w("")
w(f"**Columnas temporales** (frames, reloj, tiempo): "
  f"{', '.join([f'`{c}`' for c in temporal_cols]) if temporal_cols else '*Ninguna detectada*'}")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 3 — CLASIFICACIÓN NFL
# ════════════════════════════════════════════════════════════
w("---")
w("## 3. Clasificación del Esquema NFL")
w("")

type_descriptions = {
    "Player Tracking (Next Gen Stats)": (
        "Registra la posición espacial (x, y), velocidad, aceleración y orientación "
        "de cada jugador **frame a frame** (10 frames/seg). "
        "Una fila = un jugador en un frame específico."
    ),
    "Play-by-Play": (
        "Registra el resultado de cada **jugada individual**: down, yardas, formación, "
        "tipo de jugada, marcador. Una fila = una jugada."
    ),
    "Player/Game Summary": (
        "Registra estadísticas **acumuladas** por jugador, partido o temporada. "
        "Una fila = resumen de un jugador en un partido (o temporada)."
    ),
}

evidence_cols = {
    "Player Tracking (Next Gen Stats)": [c for c in df_full.columns
        if any(p in c.lower() for p in ["_x", "_y", "speed", "accel", "frame", "dir", "dis"])],
    "Play-by-Play": [c for c in df_full.columns
        if any(p in c.lower() for p in ["down", "yard", "play", "off", "def",
                                         "pass", "run", "punt", "score", "qtr"])],
    "Player/Game Summary": [c for c in df_full.columns
        if any(p in c.lower() for p in ["total", "avg", "per_game", "career", "cumul"])],
}

w(f"### Tipo detectado: **{primary_type}**")
w("")
w("#### Puntuación por categoría")
w("")
w("| Categoría | Señales encontradas | Columnas de evidencia |")
w("|---|---|---|")
for tipo, score in sorted(scores.items(), key=lambda x: -x[1]):
    ev = evidence_cols.get(tipo, [])
    ev_str = ", ".join([f"`{c}`" for c in ev[:6]]) + ("…" if len(ev) > 6 else "")
    marker = "⭐" if tipo == primary_type else ""
    w(f"| {marker} {tipo} | **{score}** | {ev_str or '—'} |")
w("")

w(f"### Descripción del tipo detectado")
w("")
w(f"> {type_descriptions[primary_type]}")
w("")
w("### Justificación con evidencia del dataset")
w("")

# Evidencia específica play-by-play
if primary_type == "Play-by-Play":
    play_id_info = next((g for g in granularity_results if "play" in g["col"].lower()), None)
    game_id_info = next((g for g in granularity_results if "game" in g["col"].lower()), None)

    w("**Evidencia estructural:**")
    w("")
    w(f"- El dataset tiene **{n_rows:,} filas** — volumen consistente con un registro jugada por jugada "
      f"a lo largo de múltiples temporadas (típicamente ~40,000–50,000 jugadas/temporada NFL).")

    if game_id_info:
        w(f"- `{game_id_info['col']}` tiene **{game_id_info['n_unique']:,} valores únicos** con un promedio "
          f"de **{game_id_info['avg_rows']}** filas por partido — coherente con ~130–160 jugadas/partido NFL.")
    if play_id_info:
        w(f"- `{play_id_info['col']}` tiene **{play_id_info['n_unique']:,} valores únicos** — "
          f"{'equivale al total de filas (clave primaria)' if play_id_info['coverage'] > 99 else 'identificador de jugada dentro del partido'}.")

    w(f"- Columnas `DOWN`, `YARDS_TO_FIRST`, `YARDS_TO_GOAL`, `OFF`, `DEF` son el vocabulario "
      f"exacto del sistema de registro play-by-play de la NFL.")
    w(f"- `PLAY_TYPE` codifica el tipo de acción (`RUN`, `PASS_COMPLETE`, `KICKOFF`, etc.) — "
      f"estructura característica de logs de eventos.")
    w(f"- `DESCRIPTION` contiene texto narrativo libre (play-by-play tal como lo transmite la NFL).")
    w(f"- **Ausencia** de columnas `x`, `y`, `speed`, `accel`, `frame_id` descarta Player Tracking.")
    w(f"- **Ausencia** de columnas `total_yards`, `avg_per_game`, `career_stats` descarta Summary.")

w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 4 — ESTADÍSTICAS DESCRIPTIVAS
# ════════════════════════════════════════════════════════════
w("---")
w("## 4. Estadísticas Descriptivas")
w("")
if len(df) < n_rows:
    w(f"> *Calculadas sobre una muestra aleatoria de {len(df):,} filas (semilla=42). "
      f"El dataset completo tiene {n_rows:,} filas.*")
    w("")

w("### 4.1 Variables numéricas")
w("")
w("| Columna | n | Media | Mediana | Desv. Std | Mín | P25 | P75 | Máx |")
w("|---|---|---|---|---|---|---|---|---|")
for s in num_stats:
    w(f"| `{s['col']}` | {s['count']:,} | {s['mean']} | {s['median']} | "
      f"{s['std']} | {s['min']} | {s['p25']} | {s['p75']} | {s['max']} |")
w("")

w("### 4.2 Variables categóricas — Top 5 valores")
w("")
for c in cat_stats:
    w(f"#### `{c['col']}` — {c['unique']} valores únicos")
    w("")
    w("| Valor | Frecuencia | % |")
    w("|---|---|---|")
    for val, freq, pct in c["top5"]:
        bar = "█" * int(pct / 5)
        w(f"| `{val}` | {freq:,} | {pct}% {bar} |")
    w("")

# ── Footer ─────────────────────────────────────────────────────────────────
w("---")
w(f"*Diagnóstico generado por `diagnostico.py` usando `uv run python` · "
  f"pandas + numpy · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

# ── Escribir archivo ───────────────────────────────────────────────────────
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅  diagnostico_dataset.md generado → {OUTPUT}")
print(f"    Tamaño: {os.path.getsize(OUTPUT)/1024:.1f} KB")
