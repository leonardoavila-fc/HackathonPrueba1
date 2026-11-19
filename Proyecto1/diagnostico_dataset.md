# Diagnóstico del Dataset — `nflplays.csv`
*Generado con `uv run python diagnostico.py` el 2026-11-18 21:16*
*Archivo: `/home/alberto/HackathonPrueba1/data/nflplays.csv` · Separador: TAB (TSV)*

---
## 1. Dimensiones y Calidad

### 1.1 Dimensiones

| Métrica | Valor |
|---|---|
| Filas totales | **471,583** |
| Columnas totales | **20** |
| Celdas totales | 9,431,660 |
| Filas duplicadas | **0** (0.0%) |
| Completitud global | **99.35%** |

### 1.2 Columnas — dtype y nulos

| # | Columna | dtype | Nulos | % Nulos |
|---|---|---|---|---|
| 1 | `PLAY_ID` | `int64` | 0 | 0.0% |
| 2 | `GAME_ID` | `str` | 0 | 0.0% |
| 3 | `QTR` | `int64` | 0 | 0.0% |
| 4 | `MIN` | `int64` | 0 | 0.0% |
| 5 | `SEC` | `int64` | 0 | 0.0% |
| 6 | `OFF` | `str` | 551 | 0.12% |
| 7 | `DEF` | `str` | 0 | 0.0% |
| 8 | `DOWN` | `int64` | 0 | 0.0% |
| 9 | `YARDS_TO_FIRST` | `int64` | 0 | 0.0% |
| 10 | `YARDS_TO_GOAL` | `int64` | 0 | 0.0% |
| 11 | `DESCRIPTION` | `str` | 0 | 0.0% |
| 12 | `OFF_SCORE` | `int64` | 0 | 0.0% |
| 13 | `DEF_SCORE` | `int64` | 0 | 0.0% |
| 14 | `SEASON` | `int64` | 0 | 0.0% |
| 15 | `YEAR` | `int64` | 0 | 0.0% |
| 16 | `MONTH` | `int64` | 0 | 0.0% |
| 17 | `DAY` | `int64` | 0 | 0.0% |
| 18 | `HOME_TEAM` | `str` | 0 | 0.0% |
| 19 | `AWAY_TEAM` | `str` | 0 | 0.0% |
| 20 | `PLAY_TYPE` | `str` | 60,291 | 12.78% 🟡 |

### 1.3 Columnas con valores nulos (solo las que tienen > 0)

| Columna | Nulos | % |
|---|---|---|
| `PLAY_TYPE` | 60,291 | 🟡 12.78% |
| `OFF` | 551 | 🟢 0.12% |

---
## 2. Prueba de Granularidad — ¿Qué representa cada fila?

### 2.1 Columnas identificadoras candidatas

| Columna | Valores únicos | Cobertura (% filas) | Prom. filas/ID | Máx. filas/ID | Interpretación |
|---|---|---|---|---|---|
| `PLAY_ID` | 471,583 | 100.0% | 1.0 | 1 | 🔑 ID único por fila (clave primaria) |
| `GAME_ID` | 2,905 | 0.62% | 162.33 | 217 | 📊 Muchas filas por ID (frames o tracking) |

### 2.2 Cálculo de granularidad por combinación de IDs

| Combinación | Combinaciones únicas | Prom. filas/combo | ¿Es clave? |
|---|---|---|---|
| `PLAY_ID + GAME_ID` | 471,583 | 1.0 | ✅ Sí |

### 2.3 Columnas espaciales / temporales detectadas

**Columnas espaciales** (coordenadas, velocidad, aceleración): *Ninguna detectada*

**Columnas temporales** (frames, reloj, tiempo): `MIN`, `SEC`

---
## 3. Clasificación del Esquema NFL

### Tipo detectado: **Play-by-Play**

#### Puntuación por categoría

| Categoría | Señales encontradas | Columnas de evidencia |
|---|---|---|
| ⭐ Play-by-Play | **7** | `PLAY_ID`, `QTR`, `OFF`, `DEF`, `DOWN`, `YARDS_TO_FIRST`… |
|  Player Tracking (Next Gen Stats) | **0** | — |
|  Player/Game Summary | **0** | — |

### Descripción del tipo detectado

> Registra el resultado de cada **jugada individual**: down, yardas, formación, tipo de jugada, marcador. Una fila = una jugada.

### Justificación con evidencia del dataset

**Evidencia estructural:**

- El dataset tiene **471,583 filas** — volumen consistente con un registro jugada por jugada a lo largo de múltiples temporadas (típicamente ~40,000–50,000 jugadas/temporada NFL).
- `GAME_ID` tiene **2,905 valores únicos** con un promedio de **162.33** filas por partido — coherente con ~130–160 jugadas/partido NFL.
- `PLAY_ID` tiene **471,583 valores únicos** — equivale al total de filas (clave primaria).
- Columnas `DOWN`, `YARDS_TO_FIRST`, `YARDS_TO_GOAL`, `OFF`, `DEF` son el vocabulario exacto del sistema de registro play-by-play de la NFL.
- `PLAY_TYPE` codifica el tipo de acción (`RUN`, `PASS_COMPLETE`, `KICKOFF`, etc.) — estructura característica de logs de eventos.
- `DESCRIPTION` contiene texto narrativo libre (play-by-play tal como lo transmite la NFL).
- **Ausencia** de columnas `x`, `y`, `speed`, `accel`, `frame_id` descarta Player Tracking.
- **Ausencia** de columnas `total_yards`, `avg_per_game`, `career_stats` descarta Summary.

---
## 4. Estadísticas Descriptivas

> *Calculadas sobre una muestra aleatoria de 100,000 filas (semilla=42). El dataset completo tiene 471,583 filas.*

### 4.1 Variables numéricas

| Columna | n | Media | Mediana | Desv. Std | Mín | P25 | P75 | Máx |
|---|---|---|---|---|---|---|---|---|
| `PLAY_ID` | 100,000 | 235981.3053 | 235905.5 | 136163.1837 | 7.0 | 118301.75 | 354200.0 | 471584.0 |
| `QTR` | 100,000 | 2.5473 | 3.0 | 1.1286 | 1.0 | 2.0 | 4.0 | 5.0 |
| `MIN` | 100,000 | 28.2002 | 30.0 | 17.5803 | -15.0 | 13.0 | 43.0 | 60.0 |
| `SEC` | 100,000 | 28.3221 | 28.0 | 17.9645 | 0.0 | 13.0 | 44.0 | 59.0 |
| `DOWN` | 100,000 | 1.8311 | 2.0 | 1.1213 | 0.0 | 1.0 | 3.0 | 4.0 |
| `YARDS_TO_FIRST` | 100,000 | 7.7878 | 10.0 | 4.6053 | 0.0 | 4.0 | 10.0 | 70.0 |
| `YARDS_TO_GOAL` | 100,000 | 49.1058 | 52.0 | 25.6311 | 0.0 | 28.0 | 70.0 | 100.0 |
| `OFF_SCORE` | 100,000 | 9.0405 | 7.0 | 9.3773 | 0.0 | 0.0 | 14.0 | 62.0 |
| `DEF_SCORE` | 100,000 | 9.6822 | 7.0 | 9.8244 | 0.0 | 0.0 | 16.0 | 62.0 |
| `SEASON` | 100,000 | 1824.1677 | 2006.0 | 576.7469 | -7.0 | 2003.0 | 2009.0 | 2011.0 |
| `YEAR` | 100,000 | 2007.0986 | 2007.0 | 3.1694 | 2002.0 | 2004.0 | 2010.0 | 2012.0 |
| `MONTH` | 100,000 | 10.0013 | 11.0 | 2.5784 | 1.0 | 9.0 | 12.0 | 12.0 |
| `DAY` | 100,000 | 15.9658 | 16.0 | 8.6487 | 1.0 | 9.0 | 23.0 | 31.0 |

### 4.2 Variables categóricas — Top 5 valores

#### `OFF` — 32 valores únicos

| Valor | Frecuencia | % |
|---|---|---|
| `NE` | 3,455 | 3.5%  |
| `PIT` | 3,325 | 3.3%  |
| `PHI` | 3,313 | 3.3%  |
| `GB` | 3,312 | 3.3%  |
| `NYG` | 3,274 | 3.3%  |

#### `DEF` — 33 valores únicos

| Valor | Frecuencia | % |
|---|---|---|
| `PHI` | 3,313 | 3.3%  |
| `SEA` | 3,307 | 3.3%  |
| `NYG` | 3,285 | 3.3%  |
| `SF` | 3,220 | 3.2%  |
| `MIN` | 3,208 | 3.2%  |

#### `HOME_TEAM` — 33 valores únicos

| Valor | Frecuencia | % |
|---|---|---|
| `NE` | 3,516 | 3.5%  |
| `PHI` | 3,401 | 3.4%  |
| `PIT` | 3,349 | 3.3%  |
| `GB` | 3,332 | 3.3%  |
| `SEA` | 3,259 | 3.3%  |

#### `AWAY_TEAM` — 33 valores únicos

| Valor | Frecuencia | % |
|---|---|---|
| `NYG` | 3,371 | 3.4%  |
| `BAL` | 3,336 | 3.3%  |
| `NYJ` | 3,272 | 3.3%  |
| `SEA` | 3,269 | 3.3%  |
| `PHI` | 3,225 | 3.2%  |

---
*Diagnóstico generado por `diagnostico.py` usando `uv run python` · pandas + numpy · 2026-11-18 21:16*