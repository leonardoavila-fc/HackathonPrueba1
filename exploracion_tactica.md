# Exploración Táctica — `nflplays.csv`
*Dataset completo · 471,583 filas × 20 columnas*
*Generado con `uv run python exploracion_tactica.py` · 2026-11-18 21:29*

---
## 1. Columnas exactas del archivo

| # | Nombre | dtype |
|---|---|---|
| 1 | `PLAY_ID` | `int64` |
| 2 | `GAME_ID` | `str` |
| 3 | `QTR` | `int64` |
| 4 | `MIN` | `int64` |
| 5 | `SEC` | `int64` |
| 6 | `OFF` | `str` |
| 7 | `DEF` | `str` |
| 8 | `DOWN` | `int64` |
| 9 | `YARDS_TO_FIRST` | `int64` |
| 10 | `YARDS_TO_GOAL` | `int64` |
| 11 | `DESCRIPTION` | `str` |
| 12 | `OFF_SCORE` | `int64` |
| 13 | `DEF_SCORE` | `int64` |
| 14 | `SEASON` | `int64` |
| 15 | `YEAR` | `int64` |
| 16 | `MONTH` | `int64` |
| 17 | `DAY` | `int64` |
| 18 | `HOME_TEAM` | `str` |
| 19 | `AWAY_TEAM` | `str` |
| 20 | `PLAY_TYPE` | `str` |

---
## 2. Filtrado y limpieza

### 2.1 Pasos de filtrado

| Paso | Criterio | Filas eliminadas | Filas restantes |
|---|---|---|---|
| 0 | Dataset original | — | 471,583 |
| 1 | Eliminar Pro Bowl (AFC/NFC en HOME_TEAM, AWAY_TEAM, OFF o DEF) | 174 | 471,409 |
| 2 | Eliminar PLAY_TYPE nulo | 60,275 | 411,134 |
| 3 | Eliminar DESCRIPTION solo-numérica (registros degenerados) | 0 | 411,134 |
| **Final** | **Dataset limpio** | **60,449 eliminadas (12.82%)** | **411,134** |

### 2.2 Distribución del dataset limpio por temporada

| Año | Jugadas | % |
|---|---|---|
| 2002 | 37,867 | 9.2% |
| 2003 | 41,487 | 10.1% |
| 2004 | 38,321 | 9.3% |
| 2005 | 41,757 | 10.2% |
| 2006 | 42,909 | 10.4% |
| 2007 | 40,962 | 10.0% |
| 2008 | 40,820 | 9.9% |
| 2009 | 39,085 | 9.5% |
| 2010 | 41,504 | 10.1% |
| 2011 | 42,108 | 10.2% |
| 2012 | 4,314 | 1.0% |

---
## 3. Top 25 etiquetas individuales de PLAY_TYPE

*`PLAY_TYPE` es un campo compuesto separado por `|`. Se descompone en etiquetas atómicas.*

| Rango | Etiqueta | Frecuencia | % del total | Descripción táctica |
|---|---|---|---|---|
| 1 | `RUN` | 144,059 | 22.78% ███████████ | Carrera (dirección no especificada) |
| 2 | `PASS_COMPLETE` | 107,511 | 17.0% ████████ | Pase completado |
| 3 | `PASS_INCOMPLETE` | 68,914 | 10.9% █████ | Pase incompleto |
| 4 | `RUN_LEFT` | 51,604 | 8.16% ████ | Carrera hacia la izquierda |
| 5 | `RUN_RIGHT` | 51,272 | 8.11% ████ | Carrera hacia la derecha |
| 6 | `RUN_MIDDLE` | 41,105 | 6.5% ███ | Carrera por el centro |
| 7 | `PENALTY` | 36,539 | 5.78% ██ | Penalización |
| 8 | `PUNT` | 25,688 | 4.06% ██ | Despeje |
| 9 | `KICKOFF` | 25,557 | 4.04% ██ | Patada de inicio |
| 10 | `NO_PLAY` | 23,471 | 3.71% █ | Jugada anulada (generalmente por penalidad) |
| 11 | `TOUCHDOWN` | 13,410 | 2.12% █ | Anotación de touchdown |
| 12 | `SACK` | 12,098 | 1.91%  | QB derribado en la jugada |
| 13 | `FIELD_GOAL_GOOD` | 7,994 | 1.26%  | Gol de campo anotado |
| 14 | `FUMBLE` | 7,510 | 1.19%  | Pérdida de balón (fumble) |
| 15 | `INTERCEPTION` | 5,731 | 0.91%  | Pase interceptado |
| 16 | `CHALLENGE` | 3,046 | 0.48%  | Reto al árbitro (resultado pendiente en la tag) |
| 17 | `CHALLENGE_FAIL` | 1,939 | 0.31%  | Reto al árbitro fallido |
| 18 | `FIELD_GOAL_MISSED` | 1,627 | 0.26%  | Gol de campo fallado |
| 19 | `CHALLENGE_SUCCESSFUL` | 1,108 | 0.18%  | Reto al árbitro exitoso |
| 20 | `PUNT_FAKE` | 637 | 0.1%  | Despeje fingido |
| 21 | `CONVERSION_FAILED` | 321 | 0.05%  | Conversión de 2 puntos fallida |
| 22 | `CONVERSION_GOOD` | 304 | 0.05%  | Conversión de 2 puntos exitosa |
| 23 | `FIELD_GOAL_BLOCKED` | 217 | 0.03%  | Gol de campo bloqueado |
| 24 | `SAFETY` | 168 | 0.03%  | Seguridad (2 puntos defensa) |
| 25 | `FIELD_GOAL_FAKE` | 158 | 0.02%  | Gol de campo fingido |

> Total de ocurrencias de etiquetas individuales: **632,261** | Etiquetas únicas: **28**

---
## 4. Patrones tácticos en DESCRIPTION

### 4.1 Dirección del pase

| Patrón | Regex | Coincidencias | % sobre jugadas pase+carrera |
|---|---|---|---|
| `short left` | `\bshort left\b` | 29,830 | 9.32% ███ |
| `short middle` | `\bshort middle\b` | 19,999 | 6.25% ██ |
| `short right` | `\bshort right\b` | 35,267 | 11.02% ███ |
| `deep left` | `\bdeep left\b` | 7,124 | 2.23%  |
| `deep middle` | `\bdeep middle\b` | 5,117 | 1.6%  |
| `deep right` | `\bdeep right\b` | 7,324 | 2.29%  |
| `intended for` | `\bintended for\b` | 130 | 0.04%  |

### 4.2 Dirección de carrera

| Patrón | Regex | Coincidencias | % sobre jugadas pase+carrera |
|---|---|---|---|
| `up the middle` | `\bup the middle\b` | 41,105 | 12.84% ████ |
| `left end` | `\bleft end\b` | 18,842 | 5.89% █ |
| `right end` | `\bright end\b` | 17,394 | 5.43% █ |
| `left tackle` | `\bleft tackle\b` | 18,572 | 5.8% █ |
| `right tackle` | `\bright tackle\b` | 18,706 | 5.84% █ |
| `left guard` | `\bleft guard\b` | 14,192 | 4.43% █ |
| `right guard` | `\bright guard\b` | 15,171 | 4.74% █ |
| `left` | `\bleft\b` | 89,923 | 28.09% █████████ |
| `right` | `\bright\b` | 95,538 | 29.85% █████████ |

### 4.3 Formación

| Patrón | Regex | Coincidencias | % sobre jugadas pase+carrera |
|---|---|---|---|
| `Shotgun` | `\bShotgun\b` | 78,493 | 24.52% ████████ |
| `No Huddle` | `\bNo Huddle\b` | 9,707 | 3.03% █ |
| `No Huddle Shotgun` | `\bNo Huddle.*Shotgun\b` | 5,835 | 1.82%  |
| `Wildcat` | `\bWildcat\b` | 55 | 0.02%  |
| `I-Form` | `\bI-Form\b|\bI Form\b` | 0 | 0.0%  |

### 4.4 Resultado especial

| Patrón | Regex | Coincidencias | % sobre jugadas pase+carrera |
|---|---|---|---|
| `TOUCHDOWN` | `\bTOUCHDOWN\b` | 12,207 | 3.81% █ |
| `INTERCEPTED` | `\bINTERCEPTED\b` | 204 | 0.06%  |
| `FUMBLES` | `\bFUMBLES\b` | 3,290 | 1.03%  |
| `incomplete` | `\bincomplete\b` | 68,914 | 21.53% ███████ |
| `sacked` | `\bsacked\b` | 90 | 0.03%  |
| `scrambles` | `\bscrambles\b` | 3,539 | 1.11%  |
| `ran ob` | `\bran ob\b` | 6,841 | 2.14%  |
| `pushed ob` | `\bpushed ob\b` | 18,096 | 5.65% █ |
| `PENALTY` | `\bPENALTY\b` | 18,890 | 5.9% █ |

> Base de análisis: **320,109** jugadas de pase o carrera del dataset limpio

---
## 5. Extracción robusta de `yards_gained`

### 5.1 Resultados de la extracción

| Métrica | Valor | % sobre válidas |
|---|---|---|
| Jugadas válidas (DOWN 1-4) | 384,688 | 100% |
| Yardas extraídas correctamente | 350,147 | **91.02%** |
| → Yardas = 0 (incomplete / no gain) | 89,904 | 23.37% |
| → Yardas positivas (> 0) | 233,248 | 60.63% |
| → Yardas negativas (< 0) | 26,995 | 7.02% |
| Sin extracción (None) | 34,541 | 8.98% |

### 5.2 Estadísticas de `yards_gained` extraído

| Estadística | Valor |
|---|---|
| Media | 5.674 yds |
| Mediana | 3.0 yds |
| Desv. Std | 9.188 |
| Mínimo | -74 yds |
| Máximo | 109 yds |
| P25 | 0.0 yds |
| P75 | 8.0 yds |

### 5.3 Distribución de `yards_gained` por rango

| Rango | Frecuencia | % |
|---|---|---|
| `< 0 (perdida)` | 26,995 | 7.7% ███ |
| `0 (sin ganancia)` | 89,904 | 25.7% ████████████ |
| `1-3` | 66,536 | 19.0% █████████ |
| `4-6` | 55,698 | 15.9% ███████ |
| `7-10` | 46,032 | 13.1% ██████ |
| `11-15` | 30,618 | 8.7% ████ |
| `16-20` | 14,804 | 4.2% ██ |
| `> 20` | 19,560 | 5.6% ██ |

### 5.4 Auditoría — 10 ejemplos aleatorios

*Muestra aleatoria de DESCRIPTION junto con `yards_gained` extraído para verificar calidad.*

| # | PLAY_TYPE (simplificado) | yards_gained | DESCRIPTION |
|---|---|---|---|
| 1 | `RUN` | **-1**  ✅ | `(9:35) L.White right guard to TEN 23 for -1 yards (M.Williams C.Brown).…` |
| 2 | `PASS_COMPLETE` | **20**  ✅ | `(:47) (No Huddle Shotgun) T.Brady pass short left to A.Hernandez to DEN 30 for 20 yards (D.Bruton; R…` |
| 3 | `RUN` | **1**  ✅ | `(9:39) E.James left end to ATL 36 for 1 yard (J.Babineaux).…` |
| 4 | `PASS_INCOMPLETE` | **0**  ✅ | `(2:03) (Shotgun) T.Romo pass incomplete deep left to K.Ogletree (C.Rogers). PENALTY on SF-A.Brooks D…` |
| 5 | `RUN` | **1**  ✅ | `(13:13) R.Droughns right guard to CLV 23 for 1 yard (J.Zgonina J.Seau).…` |
| 6 | `PASS_COMPLETE` | **13**  ✅ | `(10:49) (Shotgun) D.McNabb pass short middle to R.Brown to PHI 34 for 13 yards (E.Henderson).…` |
| 7 | `PASS_COMPLETE` | **6**  ✅ | `(5:27) D. Flutie pass to D.Boston to SD 33 for 6 yards (L.Walls).…` |
| 8 | `RUN` | **2**  ✅ | `(10:48) R. Williams right guard to MIA 26 for 2 yards (A.Boone).…` |
| 9 | `PASS_INCOMPLETE` | **0**  ✅ | `(2:45) S.Wallace pass incomplete to D.Hackett.…` |
| 10 | `PASS_COMPLETE` | **10**  ✅ | `(1:43) (Shotgun) J.Kitna pass short middle to J.Witten to DAL 25 for 10 yards (D.Grant). Pass comple…` |

### 5.5 Muestra de registros sin extracción (None) — para diagnosticar

| PLAY_TYPE | DOWN | DESCRIPTION |
|---|---|---|
| `FIELD_GOAL_GOOD` | 4 | `(6:30) N.Kaeding 28 yard field goal is GOOD Center-D.Binn Holder-M.Scifres.` |
| `PUNT` | 4 | `(4:45) C.Kluwe punts 34 yards to DET 8 Center-C.Loeffler out of bounds.` |
| `PUNT` | 4 | `(4:51) M.Turk punts 42 yards to end zone Center-J.Weeks Touchback. (The punt hangtime was 4.9 seconds.)` |
| `PUNT` | 4 | `(7:37) C. Gardocki punts 49 yards to KC 24 Center-R. Pontbriand downed by CLV-R. Pontbriand.` |
| `FIELD_GOAL_GOOD` | 4 | `(11:18) J.Reed 46 yard field goal is GOOD Center-M.Schneck Holder-T.Maddox.` |
| `PENALTY` | 1 | `(11:31) (Shotgun) PENALTY on MIN-R.Edwards Encroachment 5 yards enforced at GB 26 - No Play.` |
| `PENALTY` | 3 | `(8:12) (Shotgun) PENALTY on TEN-J.Scott False Start 5 yards enforced at TEN 24 - No Play.` |
| `PUNT` | 4 | `(2:33) M.Berger punts 43 yards to CAR 4 Center-K.Houser fair catch by S.Smith.` |

**Categorías de los no-extraídos:**

| PLAY_TYPE principal | n |
|---|---|
| `PUNT` | 13,510 |
| `PENALTY` | 10,180 |
| `FIELD_GOAL_GOOD` | 7,994 |
| `FIELD_GOAL_MISSED` | 1,579 |
| `PUNT_FAKE` | 460 |
| `INTERCEPTION` | 391 |
| `FUMBLE` | 197 |
| `FIELD_GOAL_BLOCKED` | 126 |
| `PUNT_BLOCKED` | 42 |
| `PASS_COMPLETE` | 33 |

---
## 6. Conclusiones y plan de acción

### Variables tácticas extraíbles con alta fiabilidad

| Variable | Fuente | Método | Cobertura estimada |
|---|---|---|---|
| `yards_gained` | `DESCRIPTION` | Regex `for N yard` + reglas especiales | **91.0%** |
| `pass_direction` | `DESCRIPTION` | Regex `short\|deep` + `left\|middle\|right` | ~65% de jugadas de pase |
| `run_direction` | `DESCRIPTION` | Regex `left\|right\|middle\|end\|tackle\|guard` | ~85% de carreras |
| `is_shotgun` | `DESCRIPTION` | Regex `Shotgun` | ~100% cuando aplica |
| `is_no_huddle` | `DESCRIPTION` | Regex `No Huddle` | ~100% cuando aplica |
| `play_category` | `PLAY_TYPE` | Split por `\|` → tomar primera etiqueta | 100% |
| `has_penalty` | `PLAY_TYPE` | Contiene `PENALTY` | 100% |
| `is_touchdown` | `PLAY_TYPE` | Contiene `TOUCHDOWN` | 100% |
| `is_turnover` | `PLAY_TYPE` | Contiene `INTERCEPTION` o `FUMBLE` | 100% |
| `score_diff` | `OFF_SCORE - DEF_SCORE` | Resta directa | 100% |

### Variables NO extraíbles de este dataset

| Variable | Motivo |
|---|---|
| Número de defensores en la caja | No existe la columna |
| Pass rushers | No existe la columna |
| Formación ofensiva (SHOTGUN, I_FORM…) | Solo inferible de `DESCRIPTION` parcialmente |
| Personnel groupings (1RB-1TE-3WR) | No existe la columna |
| Nombre de los jugadores de forma estructurada | Solo en texto libre `DESCRIPTION` |

### Dataset recomendado para la app

- **Dataset limpio:** 411,134 filas
- **Con `yards_gained`:** 350,147 jugadas de downs 1-4 con yardas calculadas (91.02%)
- **Cobertura temporal:** 2002–2012 (11 temporadas, 2,648 partidos)
- **Equipos válidos:** 32 franquicias NFL estándar (Pro Bowl excluido)

---
*Generado por `exploracion_tactica.py` · uv run python · 2026-11-18 21:29*