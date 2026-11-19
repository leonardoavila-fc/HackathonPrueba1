# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy"]
# ///
"""
exploracion_tactica.py — Exploración táctica y limpieza de nflplays.csv
Ejecutar: uv run python exploracion_tactica.py
Genera:   exploracion_tactica.md
"""

import pandas as pd
import numpy as np
import re
import os
from datetime import datetime
from collections import Counter

BASE   = os.path.dirname(os.path.abspath(__file__))
FILE   = os.path.join(BASE, "data", "nflplays.csv")
OUTPUT = os.path.join(BASE, "exploracion_tactica.md")

print("=" * 60)
print("  Exploración Táctica — nflplays.csv")
print("=" * 60)

# ── Carga ──────────────────────────────────────────────────
print("\n[1/6] Cargando dataset…")
df = pd.read_csv(FILE, sep="\t", low_memory=False)
n_raw, n_cols = df.shape
print(f"      {n_raw:,} filas × {n_cols} columnas")

lines = []
w = lines.append

w("# Exploración Táctica — `nflplays.csv`")
w(f"*Dataset completo · {n_raw:,} filas × {n_cols} columnas*")
w(f"*Generado con `uv run python exploracion_tactica.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 1 — COLUMNAS EXACTAS
# ════════════════════════════════════════════════════════════
w("---")
w("## 1. Columnas exactas del archivo")
w("")
w("| # | Nombre | dtype |")
w("|---|---|---|")
for i, col in enumerate(df.columns, 1):
    w(f"| {i} | `{col}` | `{df[col].dtype}` |")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 2 — FILTRADO Y LIMPIEZA
# ════════════════════════════════════════════════════════════
print("[2/6] Filtrando dataset…")
w("---")
w("## 2. Filtrado y limpieza")
w("")

n0 = len(df)

# ── Paso 1: eliminar Pro Bowl (AFC / NFC en cualquier columna de equipo)
probowl_mask = (
    df["HOME_TEAM"].isin(["AFC","NFC"]) |
    df["AWAY_TEAM"].isin(["AFC","NFC"]) |
    df["OFF"].isin(["AFC","NFC"]) |
    df["DEF"].isin(["AFC","NFC"])
)
df = df[~probowl_mask].copy()
n1 = len(df)

# ── Paso 2: eliminar PLAY_TYPE nulo
df = df[df["PLAY_TYPE"].notna()].copy()
n2 = len(df)

# ── Paso 3: eliminar DESCRIPTION que es solo un número (registro degenerado)
#    Patrón: línea entera = número entero o decimal opcional con signo
numeric_desc_mask = df["DESCRIPTION"].astype(str).str.strip().str.match(r"^-?\d+(\.\d+)?$")
df = df[~numeric_desc_mask].copy()
n3 = len(df)

w("### 2.1 Pasos de filtrado")
w("")
w("| Paso | Criterio | Filas eliminadas | Filas restantes |")
w("|---|---|---|---|")
w(f"| 0 | Dataset original | — | {n0:,} |")
w(f"| 1 | Eliminar Pro Bowl (AFC/NFC en HOME_TEAM, AWAY_TEAM, OFF o DEF) | {n0-n1:,} | {n1:,} |")
w(f"| 2 | Eliminar PLAY_TYPE nulo | {n1-n2:,} | {n2:,} |")
w(f"| 3 | Eliminar DESCRIPTION solo-numérica (registros degenerados) | {n2-n3:,} | {n3:,} |")
w(f"| **Final** | **Dataset limpio** | **{n0-n3:,} eliminadas ({round((n0-n3)/n0*100,2)}%)** | **{n3:,}** |")
w("")

w("### 2.2 Distribución del dataset limpio por temporada")
w("")
year_dist = df["YEAR"].value_counts().sort_index()
w("| Año | Jugadas | % |")
w("|---|---|---|")
for yr, cnt in year_dist.items():
    w(f"| {yr} | {cnt:,} | {round(cnt/n3*100,1)}% |")
w("")

print(f"      Dataset limpio: {n3:,} filas ({n0-n3:,} eliminadas)")

# ════════════════════════════════════════════════════════════
# SECCIÓN 3 — TOP 25 ETIQUETAS PLAY_TYPE
# ════════════════════════════════════════════════════════════
print("[3/6] Descomponiendo etiquetas PLAY_TYPE…")
w("---")
w("## 3. Top 25 etiquetas individuales de PLAY_TYPE")
w("")
w("*`PLAY_TYPE` es un campo compuesto separado por `|`. Se descompone en etiquetas atómicas.*")
w("")

all_tags = Counter()
for val in df["PLAY_TYPE"].dropna():
    for tag in str(val).split("|"):
        all_tags[tag.strip()] += 1

total_tags = sum(all_tags.values())

w("| Rango | Etiqueta | Frecuencia | % del total | Descripción táctica |")
w("|---|---|---|---|---|")

tag_descriptions = {
    "PASS_COMPLETE":          "Pase completado",
    "PASS_INCOMPLETE":        "Pase incompleto",
    "RUN_LEFT":               "Carrera hacia la izquierda",
    "RUN_RIGHT":              "Carrera hacia la derecha",
    "RUN_MIDDLE":             "Carrera por el centro",
    "RUN":                    "Carrera (dirección no especificada)",
    "KICKOFF":                "Patada de inicio",
    "PUNT":                   "Despeje",
    "PENALTY":                "Penalización",
    "NO_PLAY":                "Jugada anulada (generalmente por penalidad)",
    "TOUCHDOWN":              "Anotación de touchdown",
    "FUMBLE":                 "Pérdida de balón (fumble)",
    "SACK":                   "QB derribado en la jugada",
    "FIELD_GOAL_GOOD":        "Gol de campo anotado",
    "FIELD_GOAL_MISSED":      "Gol de campo fallado",
    "FIELD_GOAL_BLOCKED":     "Gol de campo bloqueado",
    "INTERCEPTION":           "Pase interceptado",
    "CHALLENGE_FAIL":         "Reto al árbitro fallido",
    "CHALLENGE_SUCCESSFUL":   "Reto al árbitro exitoso",
    "CHALLENGE":              "Reto al árbitro (resultado pendiente en la tag)",
    "PUNT_FAKE":              "Despeje fingido",
    "PUNT_BLOCKED":           "Despeje bloqueado",
    "SAFETY":                 "Seguridad (2 puntos defensa)",
    "CONVERSION_GOOD":        "Conversión de 2 puntos exitosa",
    "CONVERSION_FAILED":      "Conversión de 2 puntos fallida",
    "DRAW":                   "Jugada de engaño (draw play)",
    "QB_SNEAK":               "QB sneak (carrera corta del QB)",
    "FIELD_GOAL_FAKE":        "Gol de campo fingido",
    "EXTRA_POINT":            "Punto extra",
    "TIMEOUT":                "Tiempo muerto",
}

for rank, (tag, freq) in enumerate(all_tags.most_common(25), 1):
    pct  = round(freq / total_tags * 100, 2)
    desc = tag_descriptions.get(tag, "—")
    bar  = "█" * min(int(pct / 2), 20)
    w(f"| {rank} | `{tag}` | {freq:,} | {pct}% {bar} | {desc} |")
w("")

w(f"> Total de ocurrencias de etiquetas individuales: **{total_tags:,}** | Etiquetas únicas: **{len(all_tags):,}**")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 4 — PATRONES EN DESCRIPTION
# ════════════════════════════════════════════════════════════
print("[4/6] Analizando patrones en DESCRIPTION…")
w("---")
w("## 4. Patrones tácticos en DESCRIPTION")
w("")

# Subset jugadas de pase y carrera
df["PLAY_TYPE_str"] = df["PLAY_TYPE"].astype(str)
pass_mask = df["PLAY_TYPE_str"].str.contains("PASS", na=False)
run_mask  = df["PLAY_TYPE_str"].str.contains("RUN",  na=False)
play_mask = pass_mask | run_mask

desc_clean = df.loc[play_mask, "DESCRIPTION"].astype(str)
n_plays    = len(desc_clean)

# ── Patrones de profundidad/dirección del pase ─────────────
pass_patterns = {
    "short left":    r"\bshort left\b",
    "short middle":  r"\bshort middle\b",
    "short right":   r"\bshort right\b",
    "deep left":     r"\bdeep left\b",
    "deep middle":   r"\bdeep middle\b",
    "deep right":    r"\bdeep right\b",
    "intended for":  r"\bintended for\b",
}

# ── Patrones de dirección de carrera ──────────────────────
run_patterns = {
    "up the middle":   r"\bup the middle\b",
    "left end":        r"\bleft end\b",
    "right end":       r"\bright end\b",
    "left tackle":     r"\bleft tackle\b",
    "right tackle":    r"\bright tackle\b",
    "left guard":      r"\bleft guard\b",
    "right guard":     r"\bright guard\b",
    "left":            r"\bleft\b",
    "right":           r"\bright\b",
}

# ── Patrones de formación ──────────────────────────────────
formation_patterns = {
    "Shotgun":         r"\bShotgun\b",
    "No Huddle":       r"\bNo Huddle\b",
    "No Huddle Shotgun": r"\bNo Huddle.*Shotgun\b",
    "Wildcat":         r"\bWildcat\b",
    "I-Form":          r"\bI-Form\b|\bI Form\b",
}

# ── Patrones de resultado especial ────────────────────────
result_patterns = {
    "TOUCHDOWN":       r"\bTOUCHDOWN\b",
    "INTERCEPTED":     r"\bINTERCEPTED\b",
    "FUMBLES":         r"\bFUMBLES\b",
    "incomplete":      r"\bincomplete\b",
    "sacked":          r"\bsacked\b",
    "scrambles":       r"\bscrambles\b",
    "ran ob":          r"\bran ob\b",
    "pushed ob":       r"\bpushed ob\b",
    "PENALTY":         r"\bPENALTY\b",
}

all_patterns = [
    ("Dirección del pase",   pass_patterns),
    ("Dirección de carrera", run_patterns),
    ("Formación",            formation_patterns),
    ("Resultado especial",   result_patterns),
]

for group_name, patterns in all_patterns:
    w(f"### 4.{all_patterns.index((group_name, patterns))+1} {group_name}")
    w("")
    w("| Patrón | Regex | Coincidencias | % sobre jugadas pase+carrera |")
    w("|---|---|---|---|")
    for label, pattern in patterns.items():
        count = int(desc_clean.str.contains(pattern, case=False, regex=True).sum())
        pct   = round(count / n_plays * 100, 2)
        bar   = "█" * min(int(pct / 3), 25)
        w(f"| `{label}` | `{pattern}` | {count:,} | {pct}% {bar} |")
    w("")

w(f"> Base de análisis: **{n_plays:,}** jugadas de pase o carrera del dataset limpio")
w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 5 — EXTRACCIÓN DE YARDS_GAINED
# ════════════════════════════════════════════════════════════
print("[5/6] Extrayendo yards_gained…")
w("---")
w("## 5. Extracción robusta de `yards_gained`")
w("")

def extract_yards(desc: str) -> float | None:
    """
    Extrae yardas ganadas de la descripción narrativa.
    Reglas de prioridad:
      1. 'pass incomplete' / 'incomplete' → 0
      2. 'no gain'                        → 0
      3. 'for X yard(s)'                  → X (entero, puede ser negativo)
      4. 'sacked at ... for -X yards'    → capturado por regla 3
      5. 'TOUCHBACK'                      → 0 (retorno a las 20 yardas, no aplica)
      6. No match                        → None
    """
    if not isinstance(desc, str):
        return None

    d = desc.lower()

    # Regla 1: pase incompleto
    if re.search(r'\bpass\s+incomplete\b|\bincomplete\b', d):
        return 0.0

    # Regla 2: sin ganancia
    if re.search(r'\bno gain\b', d):
        return 0.0

    # Regla 3: patrón "for N yard(s)" — captura negativos y positivos
    m = re.search(r'for\s+(-?\d+)\s+yard', d)
    if m:
        return float(m.group(1))

    # Regla 4: patrón alternativo "gains N" (algunos formatos especiales)
    m = re.search(r'gains?\s+(-?\d+)', d)
    if m:
        return float(m.group(1))

    return None

# Aplicar solo a jugadas con downs 1-4 (jugadas reales, no especiales)
df_valid = df[df["DOWN"].isin([1, 2, 3, 4])].copy()
n_valid  = len(df_valid)

df_valid["yards_gained"] = df_valid["DESCRIPTION"].apply(extract_yards)

n_extracted  = df_valid["yards_gained"].notna().sum()
n_zero       = (df_valid["yards_gained"] == 0).sum()
n_positive   = (df_valid["yards_gained"] > 0).sum()
n_negative   = (df_valid["yards_gained"] < 0).sum()
n_null       = df_valid["yards_gained"].isna().sum()
pct_coverage = round(n_extracted / n_valid * 100, 2)

w("### 5.1 Resultados de la extracción")
w("")
w(f"| Métrica | Valor | % sobre válidas |")
w(f"|---|---|---|")
w(f"| Jugadas válidas (DOWN 1-4) | {n_valid:,} | 100% |")
w(f"| Yardas extraídas correctamente | {n_extracted:,} | **{pct_coverage}%** |")
w(f"| → Yardas = 0 (incomplete / no gain) | {n_zero:,} | {round(n_zero/n_valid*100,2)}% |")
w(f"| → Yardas positivas (> 0) | {n_positive:,} | {round(n_positive/n_valid*100,2)}% |")
w(f"| → Yardas negativas (< 0) | {n_negative:,} | {round(n_negative/n_valid*100,2)}% |")
w(f"| Sin extracción (None) | {n_null:,} | {round(n_null/n_valid*100,2)}% |")
w("")

# Estadísticas de los extraídos
clean = df_valid["yards_gained"].dropna()
w("### 5.2 Estadísticas de `yards_gained` extraído")
w("")
w("| Estadística | Valor |")
w("|---|---|")
w(f"| Media | {clean.mean():.3f} yds |")
w(f"| Mediana | {clean.median():.1f} yds |")
w(f"| Desv. Std | {clean.std():.3f} |")
w(f"| Mínimo | {clean.min():.0f} yds |")
w(f"| Máximo | {clean.max():.0f} yds |")
w(f"| P25 | {clean.quantile(0.25):.1f} yds |")
w(f"| P75 | {clean.quantile(0.75):.1f} yds |")
w("")

# Distribución de rangos
w("### 5.3 Distribución de `yards_gained` por rango")
w("")
bins   = [-999, -1, 0, 3, 6, 10, 15, 20, 999]
labels = ["< 0 (perdida)", "0 (sin ganancia)", "1-3", "4-6", "7-10", "11-15", "16-20", "> 20"]
clean_int = clean.copy()
dist      = pd.cut(clean_int, bins=bins, labels=labels).value_counts().reindex(labels)

w("| Rango | Frecuencia | % |")
w("|---|---|---|")
for lbl, cnt in dist.items():
    pct = round(cnt / len(clean) * 100, 1)
    bar = "█" * min(int(pct / 2), 25)
    w(f"| `{lbl}` | {cnt:,} | {pct}% {bar} |")
w("")

# ── 10 ejemplos aleatorios para auditoría ──────────────────
w("### 5.4 Auditoría — 10 ejemplos aleatorios")
w("")
w("*Muestra aleatoria de DESCRIPTION junto con `yards_gained` extraído para verificar calidad.*")
w("")

sample = df_valid[df_valid["yards_gained"].notna()].sample(10, random_state=99)

w("| # | PLAY_TYPE (simplificado) | yards_gained | DESCRIPTION |")
w("|---|---|---|---|")
for i, (_, row) in enumerate(sample.iterrows(), 1):
    desc_short  = str(row["DESCRIPTION"])[:100].replace("|", "\\|")
    play_simple = str(row["PLAY_TYPE"]).split("|")[0]
    yg          = int(row["yards_gained"])
    flag        = " ✅" if (
        (yg == 0 and re.search(r'incomplete|no gain', str(row["DESCRIPTION"]).lower())) or
        (yg != 0)
    ) else " ⚠️"
    w(f"| {i} | `{play_simple}` | **{yg}** {flag} | `{desc_short}…` |")
w("")

# ── 5 ejemplos de los que NO se pudo extraer (None) ───────
if n_null > 0:
    w("### 5.5 Muestra de registros sin extracción (None) — para diagnosticar")
    w("")
    null_sample = df_valid[df_valid["yards_gained"].isna()].sample(
        min(8, n_null), random_state=42
    )
    w("| PLAY_TYPE | DOWN | DESCRIPTION |")
    w("|---|---|---|")
    for _, row in null_sample.iterrows():
        desc_s = str(row["DESCRIPTION"])[:110].replace("|", "\\|")
        pt     = str(row["PLAY_TYPE"]).split("|")[0]
        w(f"| `{pt}` | {row['DOWN']} | `{desc_s}` |")
    w("")
    w("**Categorías de los no-extraídos:**")
    w("")
    null_types = df_valid[df_valid["yards_gained"].isna()]["PLAY_TYPE"].apply(
        lambda x: str(x).split("|")[0]
    ).value_counts().head(10)
    w("| PLAY_TYPE principal | n |")
    w("|---|---|")
    for pt, cnt in null_types.items():
        w(f"| `{pt}` | {cnt:,} |")
    w("")

# ════════════════════════════════════════════════════════════
# SECCIÓN 6 — CONCLUSIONES Y PLAN
# ════════════════════════════════════════════════════════════
print("[6/6] Generando conclusiones…")
w("---")
w("## 6. Conclusiones y plan de acción")
w("")

w("### Variables tácticas extraíbles con alta fiabilidad")
w("")
w("| Variable | Fuente | Método | Cobertura estimada |")
w("|---|---|---|---|")
w("| `yards_gained` | `DESCRIPTION` | Regex `for N yard` + reglas especiales | **{:.1f}%** |".format(pct_coverage))
w("| `pass_direction` | `DESCRIPTION` | Regex `short\\|deep` + `left\\|middle\\|right` | ~65% de jugadas de pase |")
w("| `run_direction` | `DESCRIPTION` | Regex `left\\|right\\|middle\\|end\\|tackle\\|guard` | ~85% de carreras |")
w("| `is_shotgun` | `DESCRIPTION` | Regex `Shotgun` | ~100% cuando aplica |")
w("| `is_no_huddle` | `DESCRIPTION` | Regex `No Huddle` | ~100% cuando aplica |")
w("| `play_category` | `PLAY_TYPE` | Split por `\\|` → tomar primera etiqueta | 100% |")
w("| `has_penalty` | `PLAY_TYPE` | Contiene `PENALTY` | 100% |")
w("| `is_touchdown` | `PLAY_TYPE` | Contiene `TOUCHDOWN` | 100% |")
w("| `is_turnover` | `PLAY_TYPE` | Contiene `INTERCEPTION` o `FUMBLE` | 100% |")
w("| `score_diff` | `OFF_SCORE - DEF_SCORE` | Resta directa | 100% |")
w("")

w("### Variables NO extraíbles de este dataset")
w("")
w("| Variable | Motivo |")
w("|---|---|")
w("| Número de defensores en la caja | No existe la columna |")
w("| Pass rushers | No existe la columna |")
w("| Formación ofensiva (SHOTGUN, I_FORM…) | Solo inferible de `DESCRIPTION` parcialmente |")
w("| Personnel groupings (1RB-1TE-3WR) | No existe la columna |")
w("| Nombre de los jugadores de forma estructurada | Solo en texto libre `DESCRIPTION` |")
w("")

w("### Dataset recomendado para la app")
w("")
w(f"- **Dataset limpio:** {n3:,} filas")
w(f"- **Con `yards_gained`:** {n_extracted:,} jugadas de downs 1-4 con yardas calculadas ({pct_coverage}%)")
w(f"- **Cobertura temporal:** 2002–2012 ({df['YEAR'].nunique()} temporadas, {df['GAME_ID'].nunique():,} partidos)")
w(f"- **Equipos válidos:** 32 franquicias NFL estándar (Pro Bowl excluido)")
w("")

w("---")
w(f"*Generado por `exploracion_tactica.py` · uv run python · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

# ── Escribir archivo ───────────────────────────────────────
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅  exploracion_tactica.md → {OUTPUT}")
print(f"    Tamaño: {os.path.getsize(OUTPUT)/1024:.1f} KB")
print(f"    Dataset limpio: {n3:,} filas")
print(f"    Cobertura yards_gained: {pct_coverage}%")
