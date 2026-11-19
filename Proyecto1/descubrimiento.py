"""
descubrimiento.py — Radiografía automática de un dataset desconocido
Uso: python3 descubrimiento.py
Genera: Perfil_del_Dataset.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# ── Configuración ──────────────────────────────────────────────────────────
FILE   = os.path.join(os.path.dirname(__file__), 'data', 'nflplays.csv')
NROWS  = 5000
OUTPUT = os.path.join(os.path.dirname(__file__), 'Perfil_del_Dataset.md')
MAX_UNIQUE_CATEGORICAL = 100  # columnas con ≤ este número de únicos → categoría
MIN_UNIQUE_TEXT        = 100  # columnas texto con > este número     → texto libre

# ── Carga segura ───────────────────────────────────────────────────────────
print(f"Leyendo {FILE} (máx {NROWS} filas)…")

# Detectar separador automáticamente
with open(FILE, 'r', encoding='utf-8', errors='replace') as f:
    first_line = f.readline()
sep = '\t' if first_line.count('\t') > first_line.count(',') else ','

df = pd.read_csv(FILE, sep=sep, nrows=NROWS, low_memory=False)
print(f"  Separador detectado: {'TAB (TSV)' if sep == chr(9) else 'COMA (CSV)'}")
print(f"  → {df.shape[0]} filas × {df.shape[1]} columnas cargadas\n")

total_rows = df.shape[0]
results = []

for col in df.columns:
    series   = df[col]
    dtype    = series.dtype
    n_null   = series.isna().sum()
    pct_null = round(n_null / total_rows * 100, 1)
    n_unique = series.nunique()

    # ── Inferir tipo semántico ─────────────────────────────────────────────
    # Intentar parsear como fecha
    is_date = False
    if dtype == object:
        sample_vals = series.dropna().head(20).astype(str)
        date_hits = 0
        for v in sample_vals:
            try:
                pd.to_datetime(v, infer_datetime_format=True)
                date_hits += 1
            except:
                pass
        if date_hits >= len(sample_vals) * 0.7:
            is_date = True

    if is_date:
        sem_type = "fecha/hora"
    elif pd.api.types.is_bool_dtype(dtype):
        sem_type = "booleano"
    elif pd.api.types.is_numeric_dtype(dtype):
        if n_unique <= 2:
            sem_type = "binario numérico"
        elif n_unique <= MAX_UNIQUE_CATEGORICAL:
            sem_type = "numérico discreto"
        else:
            sem_type = "numérico continuo"
    elif dtype == object or str(dtype) in ('string', 'object', 'str'):
        if n_unique <= MAX_UNIQUE_CATEGORICAL:
            sem_type = "categoría"
        else:
            sem_type = "texto libre"
    else:
        # Fallback para cualquier tipo de texto
        if series.dtype.kind in ('O', 'U', 'S') or 'str' in str(dtype).lower():
            sem_type = "categoría" if n_unique <= MAX_UNIQUE_CATEGORICAL else "texto libre"
        else:
            sem_type = str(dtype)

    # ── Muestra de valores únicos ──────────────────────────────────────────
    sample_uniques = []
    if sem_type in ("categoría",):
        vals = series.dropna().unique()
        sample_uniques = [str(v) for v in vals[:5]]
    elif sem_type == "texto libre":
        vals = series.dropna().unique()
        sample_uniques = [str(v)[:60] for v in vals[:3]]
    elif sem_type in ("numérico continuo", "numérico discreto"):
        sample_uniques = [str(round(v, 3)) for v in series.dropna().unique()[:5]]
    elif sem_type == "fecha/hora":
        sample_uniques = list(series.dropna().astype(str).unique()[:5])

    # ── Estadísticas básicas ───────────────────────────────────────────────
    stats = {}
    if pd.api.types.is_numeric_dtype(dtype):
        clean = series.dropna()
        if len(clean) > 0:
            stats = {
                'min': round(float(clean.min()), 2),
                'max': round(float(clean.max()), 2),
                'mean': round(float(clean.mean()), 2),
            }

    results.append({
        'columna':       col,
        'dtype_pandas':  str(dtype),
        'tipo_semantico':sem_type,
        'n_nulos':       n_null,
        'pct_nulos':     pct_null,
        'n_unicos':      n_unique,
        'muestra':       sample_uniques,
        'stats':         stats,
    })

# ── Imprimir resumen en consola ────────────────────────────────────────────
print(f"{'Columna':<35} {'Tipo':<22} {'Nulos%':>7}  {'Únicos':>7}  Muestra")
print("─" * 110)
for r in results:
    muestra_str = ', '.join(r['muestra'])[:55] if r['muestra'] else ''
    print(f"{r['columna']:<35} {r['tipo_semantico']:<22} {r['pct_nulos']:>6}%  {r['n_unicos']:>7}  {muestra_str}")

# ── Métricas globales ──────────────────────────────────────────────────────
n_cols        = len(results)
n_categoricas = sum(1 for r in results if r['tipo_semantico'] == 'categoría')
n_numericas   = sum(1 for r in results if 'numérico' in r['tipo_semantico'])
n_texto       = sum(1 for r in results if r['tipo_semantico'] == 'texto libre')
n_fecha       = sum(1 for r in results if r['tipo_semantico'] == 'fecha/hora')
n_bool        = sum(1 for r in results if 'bool' in r['tipo_semantico'] or 'binario' in r['tipo_semantico'])
pct_completo  = round((1 - df.isna().sum().sum() / (total_rows * n_cols)) * 100, 1)

cols_mas_nulos = sorted(results, key=lambda x: x['pct_nulos'], reverse=True)[:5]
categoricas    = [r for r in results if r['tipo_semantico'] == 'categoría']

print(f"\n✓ Perfilado completo. Generando Perfil_del_Dataset.md…")

# ══════════════════════════════════════════════════════════════════════════
# GENERAR MARKDOWN
# ══════════════════════════════════════════════════════════════════════════
lines = []
w = lines.append

w(f"# Perfil del Dataset — `nflplays.csv`")
w(f"*Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M')} · primeras {total_rows:,} filas analizadas*")
w("")

# ── Métricas de cabecera ───────────────────────────────────────────────────
w("## Métricas generales")
w("")
w(f"| Métrica | Valor |")
w(f"|---|---|")
w(f"| Filas analizadas | {total_rows:,} |")
w(f"| Columnas totales | {n_cols} |")
w(f"| Completitud global | **{pct_completo}%** |")
w(f"| Columnas categóricas | {n_categoricas} |")
w(f"| Columnas numéricas | {n_numericas} |")
w(f"| Columnas texto libre | {n_texto} |")
w(f"| Columnas fecha/hora | {n_fecha} |")
w(f"| Columnas booleanas/binarias | {n_bool} |")
w("")

# ── Columnas con más nulos ─────────────────────────────────────────────────
w("## Columnas con mayor porcentaje de nulos")
w("")
w("| Columna | % Nulos |")
w("|---|---|")
for r in cols_mas_nulos:
    barra = '🔴' if r['pct_nulos'] > 50 else '🟡' if r['pct_nulos'] > 20 else '🟢'
    w(f"| `{r['columna']}` | {barra} {r['pct_nulos']}% |")
w("")

# ── Inventario completo ────────────────────────────────────────────────────
w("## Inventario completo de columnas")
w("")
w("| # | Columna | Tipo semántico | % Nulos | Únicos | Muestra de valores |")
w("|---|---|---|---|---|---|")
for i, r in enumerate(results, 1):
    muestra = ', '.join([f'`{v}`' for v in r['muestra']]) if r['muestra'] else '—'
    stats_str = ''
    if r['stats']:
        stats_str = f" (min={r['stats']['min']}, max={r['stats']['max']}, avg={r['stats']['mean']})"
    w(f"| {i} | `{r['columna']}` | {r['tipo_semantico']} | {r['pct_nulos']}% | {r['n_unicos']:,} | {muestra}{stats_str} |")
w("")

# ── Categorías expandidas ──────────────────────────────────────────────────
if categoricas:
    w("## Detalle de columnas categóricas")
    w("")
    for r in categoricas:
        all_vals = df[r['columna']].dropna().unique()
        vals_str = ', '.join([f'`{v}`' for v in all_vals[:20]])
        w(f"**`{r['columna']}`** — {r['n_unicos']} valores únicos")
        w(f"> {vals_str}{'…' if r['n_unicos'] > 20 else ''}")
        w("")

# ══════════════════════════════════════════════════════════════════════════
# DIAGNÓSTICO — inferencia automática de dominio
# ══════════════════════════════════════════════════════════════════════════
w("---")
w("")
w("## 1. Diagnóstico — ¿De qué industria o tema es este dataset?")
w("")

# Heurística de dominio: buscar palabras clave en nombres de columnas
col_names_lower = ' '.join(df.columns.str.lower())
keywords = {
    'deportes/fútbol americano': ['quarter','down','yards','pass','rush','touchdown','penalty','formation','offense','defense','kick','punt','score','play','field','goal'],
    'finanzas/transacciones':    ['amount','price','balance','transaction','account','revenue','cost','profit','currency','payment'],
    'salud/médico':              ['patient','diagnosis','age','weight','bmi','blood','hospital','treatment','medication'],
    'e-commerce/retail':         ['product','category','order','customer','purchase','price','quantity','discount','shipping'],
    'rh/recursos humanos':       ['employee','salary','department','hire','position','performance'],
    'logística/transporte':      ['shipment','route','distance','warehouse','delivery','carrier','freight'],
}
scores = {}
for domain, kws in keywords.items():
    scores[domain] = sum(1 for kw in kws if kw in col_names_lower)

top_domain = max(scores, key=scores.get)
top_score  = scores[top_domain]

w(f"### Industria inferida: **{top_domain.split('/')[0].upper()}**")
w("")
w(f"**Confianza:** {'Alta ✅' if top_score >= 5 else 'Media ⚠️' if top_score >= 2 else 'Baja ❓'} ({top_score} señales encontradas en los nombres de columnas)")
w("")
w("**Justificación basada en las columnas:**")
w("")

# Señales específicas encontradas
found_kws = [kw for kw in keywords[top_domain] if kw in col_names_lower]
w(f"Las columnas contienen términos como: {', '.join([f'`{k}`' for k in found_kws])}, "
  f"lo que apunta inequívocamente a registros de {top_domain}.")
w("")
w("**Hipótesis sobre el origen:**")
w("")

# Columna de ID tipo game/play
id_cols = [c for c in df.columns if any(x in c.lower() for x in ['id','game','play','match'])]
time_cols = [c for c in df.columns if any(x in c.lower() for x in ['time','clock','quarter','date','period'])]
team_cols = [c for c in df.columns if any(x in c.lower() for x in ['team','side','home','visitor','possession'])]

w(f"- **Identificadores detectados:** {', '.join([f'`{c}`' for c in id_cols[:5]]) or 'ninguno obvio'}")
w(f"- **Columnas temporales:** {', '.join([f'`{c}`' for c in time_cols[:5]]) or 'ninguna'}")
w(f"- **Columnas de equipos/actores:** {', '.join([f'`{c}`' for c in team_cols[:5]]) or 'ninguna'}")
w("")
w("> Este dataset registra **eventos individuales** (una fila = una jugada/acción), "
  "no agregados. Es un log transaccional de alto granulado.")
w("")

# ══════════════════════════════════════════════════════════════════════════
# DICCIONARIO DE DATOS
# ══════════════════════════════════════════════════════════════════════════
w("---")
w("")
w("## 2. Diccionario de Datos")
w("")
w("Interpretación de cada columna según su nombre, tipo y valores observados.")
w("")
w("| Columna | Tipo | Interpretación probable |")
w("|---|---|---|")

# Diccionario heurístico por palabras clave
def infer_meaning(col, r):
    c = col.lower()
    t = r['tipo_semantico']
    s = r['muestra']

    if 'play_id'    in c: return "Identificador único de la jugada (secuencial dentro del archivo)"
    if 'gameid'    in c or 'game_id' in c: return "Identificador único del partido (formato YYYYMMDD_AWAY@HOME)"
    if 'playid'    in c: return "Identificador único de la jugada dentro del partido"
    if 'quarter'   in c or c == 'qtr': return "Cuarto del partido (1 a 4, 5 = tiempo extra)"
    if c == 'min':  return "Minutos restantes en el cuarto (0–60)"
    if c == 'sec':  return "Segundos del reloj al momento de la jugada (0–59)"
    if c == 'off':  return "Equipo ofensivo con posesión del balón (siglas NFL, ej. SF, NYG)"
    if c == 'def':  return "Equipo defensivo (sin posesión) en la jugada (siglas NFL)"
    if 'gameclock' in c or 'clock' in c: return "Tiempo restante en el cuarto (MM:SS)"
    if 'down'      in c and t != 'texto libre': return "Número de down (intento): 1, 2, 3 o 4 — 0 indica jugada especial"
    if 'yards_to_first' in c or 'yardstogo' in c: return "Yardas necesarias para obtener un nuevo 1er down"
    if 'yards_to_goal'  in c or 'yardline'  in c: return "Yardas restantes para llegar a la end zone (0–99)"
    if 'off_score' in c: return "Puntaje acumulado del equipo ofensivo al momento de la jugada"
    if 'def_score' in c: return "Puntaje acumulado del equipo defensivo al momento de la jugada"
    if 'season'    in c: return "Temporada NFL a la que pertenece el partido (año)"
    if c == 'year': return "Año del partido"
    if c == 'month':return "Mes del partido (9=septiembre, inicio de temporada regular)"
    if c == 'day':  return "Día del mes del partido"
    if 'home_team' in c or ('home' in c and 'team' in c): return "Equipo local (anfitrión) del partido"
    if 'away_team' in c or ('away' in c and 'team' in c): return "Equipo visitante del partido"
    if 'play_type' in c: return "Tipo de jugada codificado (ej. RUN|RUN_LEFT, PASS_COMPLETE, KICKOFF, PUNT) — puede ser compuesto con '|'"
    if 'possession' in c: return "Equipo con posesión del balón (siglas NFL)"
    if 'formation' in c: return "Formación táctica del equipo ofensivo"
    if 'personnel' in c and 'off' in c: return "Paquete de jugadores ofensivos en el campo (ej. 1 RB, 1 TE, 3 WR)"
    if 'personnel' in c and 'def' in c: return "Paquete de jugadores defensivos en el campo (ej. 4 DL, 2 LB, 5 DB)"
    if 'defenders' in c: return "Número de defensores dentro de la línea de scrimmage"
    if 'passrush'  in c or 'rusher' in c: return "Número de jugadores enviados a presionar al QB"
    if 'homescore' in c and 'before' in c: return "Puntaje del equipo local antes de la jugada"
    if 'homescore' in c and 'after'  in c: return "Puntaje del equipo local después de la jugada"
    if 'visitorscore' in c and 'before' in c: return "Puntaje del equipo visitante antes de la jugada"
    if 'visitorscore' in c and 'after'  in c: return "Puntaje del equipo visitante después de la jugada"
    if 'ispenalty'  in c: return "Indica si hubo penalización en la jugada (TRUE/FALSE)"
    if 'isstplay'   in c: return "Indica si es una jugada de equipos especiales (TRUE/FALSE)"
    if 'specialteams' in c: return "Tipo de jugada especial (Kickoff, Punt, Field Goal, Extra Point)"
    if 'kickreturn' in c: return "Yardas ganadas en retorno de patada"
    if 'passlength' in c: return "Distancia del pase en yardas (aéreo)"
    if 'passresult' in c: return "Resultado del pase: C=Completo, I=Incompleto, S=Sack, R=Scramble, IN=Interceptado"
    if 'yardsaftercatch' in c: return "Yardas ganadas por el receptor después de atrapar el balón (YAC)"
    if 'playresult' in c: return "Yardas totales ganadas o perdidas en la jugada"
    if 'playdescription' in c or 'description' in c: return "Descripción textual completa de la jugada (play-by-play narrativo)"
    if 'side' in c: return "Lado del campo donde está el balón (siglas del equipo dueño del lado)"

    # Fallback por tipo
    if t == 'categoría':     return f"Variable categórica — valores: {', '.join(s[:3])}"
    if t == 'numérico continuo': return f"Métrica numérica (rango {r['stats'].get('min','?')}–{r['stats'].get('max','?')})"
    if t == 'booleano' or 'binario' in t: return "Indicador binario (sí/no)"
    if t == 'texto libre':   return "Campo descriptivo de texto libre"
    return "Por determinar"

for r in results:
    meaning = infer_meaning(r['columna'], r)
    w(f"| `{r['columna']}` | {r['tipo_semantico']} | {meaning} |")
w("")

# ══════════════════════════════════════════════════════════════════════════
# VISIÓN DE VALOR
# ══════════════════════════════════════════════════════════════════════════
w("---")
w("")
w("## 3. Visión de Valor — Roles y Preguntas de Alto Impacto")
w("")
w("Tres perfiles profesionales que encontrarían valor en este dataset, con la pregunta más relevante que cada uno intentaría responder.")
w("")

roles = [
    {
        "emoji": "🎯",
        "rol": "Analista Cuantitativo de Apuestas Deportivas (Sports Quant)",
        "descripcion": "Construye modelos probabilísticos para detectar cuotas mal calibradas en mercados de apuestas en vivo.",
        "pregunta": "¿En qué combinación exacta de **cuarto, estado del marcador y formación ofensiva** el rendimiento real del equipo diverge más del rendimiento que el mercado de apuestas asume — generando una ventana de value bet repetible?",
        "variables": "`quarter`, `score`, `offenseFormation`, `PlayResult`, `PassResult`, `down`, `yardsToGo`",
        "metodo": "Modelo de regresión logística o árbol de decisión para predecir probabilidad de anotación en las próximas N jugadas según contexto táctico.",
    },
    {
        "emoji": "📊",
        "rol": "Coordinador Ofensivo / Analista de Rendimiento NFL",
        "descripcion": "Optimiza el play-calling basándose en patrones históricos de eficiencia para maximizar yardas y conversiones.",
        "pregunta": "¿Qué combinación de **formación ofensiva + paquete de personal + down & distance** maximiza la tasa de conversión en 3er down contra distintos paquetes defensivos?",
        "variables": "`offenseFormation`, `personnel.offense`, `personnel.defense`, `down`, `yardsToGo`, `defendersInTheBox`, `PlayResult`",
        "metodo": "Análisis de frecuencia cruzada (crosstab) y matriz de eficiencia por situación de juego.",
    },
    {
        "emoji": "🤖",
        "rol": "Ingeniero de Machine Learning / NLP",
        "descripcion": "Entrena modelos predictivos sobre eventos deportivos y extrae entidades de texto no estructurado.",
        "pregunta": "¿Es posible entrenar un modelo que, dado el estado del juego en tiempo real (quarter, clock, score, down, formation), prediga el **tipo de jugada siguiente** (pase corto, pase largo, carrera, jugada especial) con precisión superior al 65%?",
        "variables": "Todas las columnas de contexto + `PlayResult`, `PassResult`, `offenseFormation`, `playDescription` (NLP)",
        "metodo": "Clasificador multiclase (Random Forest / XGBoost) con features de lag (últimas N jugadas) y one-hot encoding de variables categóricas.",
    },
]

for role in roles:
    w(f"### {role['emoji']} {role['rol']}")
    w("")
    w(f"**Perfil:** {role['descripcion']}")
    w("")
    w(f"**Pregunta de alto valor:**")
    w(f"> {role['pregunta']}")
    w("")
    w(f"**Variables clave:** {role['variables']}")
    w("")
    w(f"**Método sugerido:** {role['metodo']}")
    w("")

# ── Calidad del dataset ────────────────────────────────────────────────────
w("---")
w("")
w("## 4. Calidad del Dataset — Semáforo")
w("")
w("| Dimensión | Estado | Detalle |")
w("|---|---|---|")

completitud_color = '🟢' if pct_completo >= 80 else '🟡' if pct_completo >= 60 else '🔴'
w(f"| Completitud | {completitud_color} {pct_completo}% | Porcentaje de celdas con datos |")

cols_sin_nulos = sum(1 for r in results if r['pct_nulos'] == 0)
w(f"| Columnas 100% completas | {'🟢' if cols_sin_nulos > n_cols*0.5 else '🟡'} {cols_sin_nulos}/{n_cols} | Sin ningún valor faltante |")

cols_alta_cardinalidad = sum(1 for r in results if r['n_unicos'] > total_rows * 0.9 and 'texto' not in r['tipo_semantico'])
w(f"| IDs / Alta cardinalidad | {'🟡' if cols_alta_cardinalidad > 0 else '🟢'} {cols_alta_cardinalidad} cols | Columnas casi únicas por fila (posibles IDs) |")

bool_cols = sum(1 for r in results if 'bool' in r['tipo_semantico'] or 'binario' in r['tipo_semantico'])
w(f"| Variables binarias | 🟢 {bool_cols} | Indicadores de eventos discretos |")

w("")
w("---")
w(f"*Perfil generado por `descubrimiento.py` · Dataset: `nflplays.csv` · Filas analizadas: {total_rows:,}*")

# ── Escribir archivo ───────────────────────────────────────────────────────
with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f"\n✅ Perfil_del_Dataset.md generado en:\n   {OUTPUT}")
