# Perfil del Dataset — `nflplays.csv`
*Generado automáticamente el 2026-11-16 23:21 · primeras 5,000 filas analizadas*

## Métricas generales

| Métrica | Valor |
|---|---|
| Filas analizadas | 5,000 |
| Columnas totales | 20 |
| Completitud global | **99.8%** |
| Columnas categóricas | 6 |
| Columnas numéricas | 13 |
| Columnas texto libre | 1 |
| Columnas fecha/hora | 0 |
| Columnas booleanas/binarias | 3 |

## Columnas con mayor porcentaje de nulos

| Columna | % Nulos |
|---|---|
| `PLAY_TYPE` | 🟢 4.1% |
| `OFF` | 🟢 0.1% |
| `PLAY_ID` | 🟢 0.0% |
| `GAME_ID` | 🟢 0.0% |
| `QTR` | 🟢 0.0% |

## Inventario completo de columnas

| # | Columna | Tipo semántico | % Nulos | Únicos | Muestra de valores |
|---|---|---|---|---|---|
| 1 | `PLAY_ID` | numérico continuo | 0.0% | 5,000 | `1`, `2`, `3`, `4`, `5` (min=1.0, max=5000.0, avg=2500.5) |
| 2 | `GAME_ID` | categoría | 0.0% | 31 | `20020905_SF@NYG`, `20020908_KC@CLE`, `20020908_ARI@WAS`, `20020908_PHI@TEN`, `20020908_DET@MIA` |
| 3 | `QTR` | numérico discreto | 0.0% | 5 | `1`, `2`, `3`, `4`, `5` (min=1.0, max=5.0, avg=2.54) |
| 4 | `MIN` | numérico discreto | 0.0% | 74 | `0`, `60`, `59`, `58`, `57` (min=-13.0, max=60.0, avg=28.26) |
| 5 | `SEC` | numérico discreto | 0.0% | 60 | `0`, `25`, `20`, `9`, `38` (min=0.0, max=59.0, avg=27.81) |
| 6 | `OFF` | categoría | 0.1% | 32 | `SF`, `NYG`, `CLE`, `KC`, `ARI` |
| 7 | `DEF` | categoría | 0.0% | 32 | `NYG`, `SF`, `KC`, `CLE`, `WAS` |
| 8 | `DOWN` | numérico discreto | 0.0% | 5 | `0`, `1`, `2`, `3`, `4` (min=0.0, max=4.0, avg=1.82) |
| 9 | `YARDS_TO_FIRST` | numérico discreto | 0.0% | 33 | `0`, `10`, `6`, `11`, `7` (min=0.0, max=34.0, avg=7.7) |
| 10 | `YARDS_TO_GOAL` | numérico discreto | 0.0% | 100 | `0`, `80`, `76`, `81`, `23` (min=0.0, max=99.0, avg=48.76) |
| 11 | `DESCRIPTION` | texto libre | 0.0% | 4,873 | `J.Cortez kicks 75 yards from SF 30 to NYG -5. R.Dixon  Touch`, `(15:00) T.Barber left end to NYG 24 for 4 yards (C.Okeafor  `, `(14:25) K.Collins pass incomplete to J.Shockey (D.Smith).` |
| 12 | `OFF_SCORE` | numérico discreto | 0.0% | 33 | `0`, `3`, `6`, `10`, `13` (min=0.0, max=55.0, avg=10.82) |
| 13 | `DEF_SCORE` | numérico discreto | 0.0% | 33 | `0`, `3`, `6`, `10`, `13` (min=0.0, max=55.0, avg=11.8) |
| 14 | `SEASON` | binario numérico | 0.0% | 1 | — (min=2002.0, max=2002.0, avg=2002.0) |
| 15 | `YEAR` | binario numérico | 0.0% | 1 | — (min=2002.0, max=2002.0, avg=2002.0) |
| 16 | `MONTH` | binario numérico | 0.0% | 1 | — (min=9.0, max=9.0, avg=9.0) |
| 17 | `DAY` | numérico discreto | 0.0% | 6 | `5`, `8`, `9`, `15`, `22` (min=5.0, max=23.0, avg=14.41) |
| 18 | `HOME_TEAM` | categoría | 0.0% | 23 | `NYG`, `CLE`, `WAS`, `TEN`, `MIA` |
| 19 | `AWAY_TEAM` | categoría | 0.0% | 23 | `SF`, `KC`, `ARI`, `PHI`, `DET` |
| 20 | `PLAY_TYPE` | categoría | 4.1% | 98 | `KICKOFF`, `RUN|RUN_LEFT`, `PASS_INCOMPLETE`, `PENALTY|NO_PLAY`, `INTERCEPTION` |

## Detalle de columnas categóricas

**`GAME_ID`** — 31 valores únicos
> `20020905_SF@NYG`, `20020908_KC@CLE`, `20020908_ARI@WAS`, `20020908_PHI@TEN`, `20020908_DET@MIA`, `20020908_IND@JAC`, `20020908_ATL@GB`, `20020908_SD@CIN`, `20020908_BAL@CAR`, `20020908_NYJ@BUF`, `20020908_MIN@CHI`, `20020908_NO@TB`, `20020908_SEA@OAK`, `20020908_STL@DEN`, `20020908_DAL@HOU`, `20020909_PIT@NE`, `20020915_MIA@IND`, `20020922_IND@HOU`, `20020922_CLE@TEN`, `20020922_DAL@PHI`…

**`OFF`** — 32 valores únicos
> `SF`, `NYG`, `CLE`, `KC`, `ARI`, `WAS`, `TEN`, `PHI`, `DET`, `MIA`, `IND`, `JAC`, `GB`, `ATL`, `CIN`, `SD`, `BAL`, `CAR`, `NYJ`, `BUF`…

**`DEF`** — 32 valores únicos
> `NYG`, `SF`, `KC`, `CLE`, `WAS`, `ARI`, `PHI`, `TEN`, `MIA`, `DET`, `JAC`, `IND`, `ATL`, `GB`, `SD`, `CIN`, `CAR`, `BAL`, `BUF`, `NYJ`…

**`HOME_TEAM`** — 23 valores únicos
> `NYG`, `CLE`, `WAS`, `TEN`, `MIA`, `JAC`, `GB`, `CIN`, `CAR`, `BUF`, `CHI`, `TB`, `OAK`, `DEN`, `HOU`, `NE`, `IND`, `PHI`, `MIN`, `ARI`…

**`AWAY_TEAM`** — 23 valores únicos
> `SF`, `KC`, `ARI`, `PHI`, `DET`, `IND`, `ATL`, `SD`, `BAL`, `NYJ`, `MIN`, `NO`, `SEA`, `STL`, `DAL`, `PIT`, `MIA`, `CLE`, `CAR`, `BUF`…

**`PLAY_TYPE`** — 98 valores únicos
> `KICKOFF`, `RUN|RUN_LEFT`, `PASS_INCOMPLETE`, `PENALTY|NO_PLAY`, `INTERCEPTION`, `RUN|RUN_RIGHT|PASS_COMPLETE`, `PASS_COMPLETE`, `FIELD_GOAL_BLOCKED`, `PASS_INCOMPLETE|PENALTY|NO_PLAY`, `PASS_COMPLETE|PENALTY|NO_PLAY`, `RUN|RUN_RIGHT`, `FUMBLE|PENALTY|NO_PLAY`, `FIELD_GOAL_GOOD`, `RUN|RUN_MIDDLE|PASS_COMPLETE`, `RUN|RUN_MIDDLE`, `PASS_COMPLETE|PENALTY`, `RUN|RUN_RIGHT|PENALTY|NO_PLAY`, `RUN|RUN_LEFT|PASS_COMPLETE|PENALTY|NO_PLAY`, `PUNT|PENALTY`, `PUNT`…

---

## 1. Diagnóstico — ¿De qué industria o tema es este dataset?

### Industria inferida: **DEPORTES**

**Confianza:** Alta ✅ (5 señales encontradas en los nombres de columnas)

**Justificación basada en las columnas:**

Las columnas contienen términos como: `down`, `yards`, `score`, `play`, `goal`, lo que apunta inequívocamente a registros de deportes/fútbol americano.

**Hipótesis sobre el origen:**

- **Identificadores detectados:** `PLAY_ID`, `GAME_ID`, `PLAY_TYPE`
- **Columnas temporales:** ninguna
- **Columnas de equipos/actores:** `HOME_TEAM`, `AWAY_TEAM`

> Este dataset registra **eventos individuales** (una fila = una jugada/acción), no agregados. Es un log transaccional de alto granulado.

---

## 2. Diccionario de Datos

Interpretación de cada columna según su nombre, tipo y valores observados.

| Columna | Tipo | Interpretación probable |
|---|---|---|
| `PLAY_ID` | numérico continuo | Identificador único de la jugada (secuencial dentro del archivo) |
| `GAME_ID` | categoría | Identificador único del partido (formato YYYYMMDD_AWAY@HOME) |
| `QTR` | numérico discreto | Cuarto del partido (1 a 4, 5 = tiempo extra) |
| `MIN` | numérico discreto | Minutos restantes en el cuarto (0–60) |
| `SEC` | numérico discreto | Segundos del reloj al momento de la jugada (0–59) |
| `OFF` | categoría | Equipo ofensivo con posesión del balón (siglas NFL, ej. SF, NYG) |
| `DEF` | categoría | Equipo defensivo (sin posesión) en la jugada (siglas NFL) |
| `DOWN` | numérico discreto | Número de down (intento): 1, 2, 3 o 4 — 0 indica jugada especial |
| `YARDS_TO_FIRST` | numérico discreto | Yardas necesarias para obtener un nuevo 1er down |
| `YARDS_TO_GOAL` | numérico discreto | Yardas restantes para llegar a la end zone (0–99) |
| `DESCRIPTION` | texto libre | Descripción textual completa de la jugada (play-by-play narrativo) |
| `OFF_SCORE` | numérico discreto | Puntaje acumulado del equipo ofensivo al momento de la jugada |
| `DEF_SCORE` | numérico discreto | Puntaje acumulado del equipo defensivo al momento de la jugada |
| `SEASON` | binario numérico | Temporada NFL a la que pertenece el partido (año) |
| `YEAR` | binario numérico | Año del partido |
| `MONTH` | binario numérico | Mes del partido (9=septiembre, inicio de temporada regular) |
| `DAY` | numérico discreto | Día del mes del partido |
| `HOME_TEAM` | categoría | Equipo local (anfitrión) del partido |
| `AWAY_TEAM` | categoría | Equipo visitante del partido |
| `PLAY_TYPE` | categoría | Tipo de jugada codificado (ej. RUN|RUN_LEFT, PASS_COMPLETE, KICKOFF, PUNT) — puede ser compuesto con '|' |

---

## 3. Visión de Valor — Roles y Preguntas de Alto Impacto

Tres perfiles profesionales que encontrarían valor en este dataset, con la pregunta más relevante que cada uno intentaría responder.

### 🎯 Analista Cuantitativo de Apuestas Deportivas (Sports Quant)

**Perfil:** Construye modelos probabilísticos para detectar cuotas mal calibradas en mercados de apuestas en vivo.

**Pregunta de alto valor:**
> ¿En qué combinación exacta de **cuarto, estado del marcador y formación ofensiva** el rendimiento real del equipo diverge más del rendimiento que el mercado de apuestas asume — generando una ventana de value bet repetible?

**Variables clave:** `quarter`, `score`, `offenseFormation`, `PlayResult`, `PassResult`, `down`, `yardsToGo`

**Método sugerido:** Modelo de regresión logística o árbol de decisión para predecir probabilidad de anotación en las próximas N jugadas según contexto táctico.

### 📊 Coordinador Ofensivo / Analista de Rendimiento NFL

**Perfil:** Optimiza el play-calling basándose en patrones históricos de eficiencia para maximizar yardas y conversiones.

**Pregunta de alto valor:**
> ¿Qué combinación de **formación ofensiva + paquete de personal + down & distance** maximiza la tasa de conversión en 3er down contra distintos paquetes defensivos?

**Variables clave:** `offenseFormation`, `personnel.offense`, `personnel.defense`, `down`, `yardsToGo`, `defendersInTheBox`, `PlayResult`

**Método sugerido:** Análisis de frecuencia cruzada (crosstab) y matriz de eficiencia por situación de juego.

### 🤖 Ingeniero de Machine Learning / NLP

**Perfil:** Entrena modelos predictivos sobre eventos deportivos y extrae entidades de texto no estructurado.

**Pregunta de alto valor:**
> ¿Es posible entrenar un modelo que, dado el estado del juego en tiempo real (quarter, clock, score, down, formation), prediga el **tipo de jugada siguiente** (pase corto, pase largo, carrera, jugada especial) con precisión superior al 65%?

**Variables clave:** Todas las columnas de contexto + `PlayResult`, `PassResult`, `offenseFormation`, `playDescription` (NLP)

**Método sugerido:** Clasificador multiclase (Random Forest / XGBoost) con features de lag (últimas N jugadas) y one-hot encoding de variables categóricas.

---

## 4. Calidad del Dataset — Semáforo

| Dimensión | Estado | Detalle |
|---|---|---|
| Completitud | 🟢 99.8% | Porcentaje de celdas con datos |
| Columnas 100% completas | 🟢 18/20 | Sin ningún valor faltante |
| IDs / Alta cardinalidad | 🟡 1 cols | Columnas casi únicas por fila (posibles IDs) |
| Variables binarias | 🟢 3 | Indicadores de eventos discretos |

---
*Perfil generado por `descubrimiento.py` · Dataset: `nflplays.csv` · Filas analizadas: 5,000*