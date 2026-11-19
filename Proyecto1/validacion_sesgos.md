# Validación de Sesgos — `nfl_clean.parquet`
*Generado con `uv run python validacion_sesgos.py` · 2026-11-18 21:52*

---
## Control 1 — Distancia en 3er Down

*Tasa de conversión de 1er down y `yards_gained` medio, cruzando*
*`is_shotgun × play_category` segmentado por rango de `YARDS_TO_FIRST`.*

**Hipótesis a verificar:** la ventaja de Shotgun+Pase en 3er down es real en distancias
largas (7+ yds) pero desaparece o se invierte en distancias cortas (1-2 yds)?

### C1 — 3er Down · 1-2 yds (corto) (n=13,760)

| Formación | Tipo | n | % del segmento | Yds Media | Yds Mediana | Conv 1er Down % |
|---|---|---|---|---|---|---|
| Shotgun ✓ | Carrera | 567 | 4.1% | 4.17 yds | 3.0 yds | 68.8% 🟢 |
| Shotgun ✗ | Carrera | 7,570 | 55.0% | 3.26 yds | 2.0 yds | 68.0% 🟢 |
| Shotgun ✓ | Pase | 1,759 | 12.8% | 5.94 yds | 3.0 yds | 56.7% 🟢 |
| Shotgun ✗ | Pase | 3,324 | 24.2% | 6.06 yds | 2.0 yds | 55.2% 🟢 |

### C1 — 3er Down · 3-6 yds (medio) (n=23,495)

| Formación | Tipo | n | % del segmento | Yds Media | Yds Mediana | Conv 1er Down % |
|---|---|---|---|---|---|---|
| Shotgun ✓ | Carrera | 1,189 | 5.1% | 5.98 yds | 4.0 yds | 54.8% 🟢 |
| Shotgun ✓ | Pase | 9,865 | 42.0% | 6.53 yds | 4.0 yds | 49.8% |
| Shotgun ✗ | Pase | 7,552 | 32.1% | 5.73 yds | 3.0 yds | 46.5% |
| Shotgun ✗ | Carrera | 2,627 | 11.2% | 4.63 yds | 3.0 yds | 44.2% |

### C1 — 3er Down · 7+ yds (largo) (n=35,316)

| Formación | Tipo | n | % del segmento | Yds Media | Yds Mediana | Conv 1er Down % |
|---|---|---|---|---|---|---|
| Shotgun ✓ | Pase | 18,091 | 51.2% | 7.56 yds | 5.0 yds | 31.5% 🔴 |
| Shotgun ✗ | Pase | 8,386 | 23.7% | 6.83 yds | 3.0 yds | 29.1% 🔴 |
| Shotgun ✓ | Carrera | 1,853 | 5.2% | 7.49 yds | 7.0 yds | 26.5% 🔴 |
| Shotgun ✗ | Carrera | 2,589 | 7.3% | 5.68 yds | 4.0 yds | 17.1% 🔴 |

### C1.4 — Tabla resumen: Conv% por rango de distancia

| Formación + Tipo | 1-2 yds (corto) | 3-6 yds (medio) | 7+ yds (largo) |
|---|---|---|---|
| **Shotgun ✓ Pase** | 56.7% (n=1,759) | 49.8% (n=9,865) | 31.5% (n=18,091) |
| **Shotgun ✗ Pase** | 55.2% (n=3,324) | 46.5% (n=7,552) | 29.1% (n=8,386) |
| **Shotgun ✓ Carrera** | 68.8% (n=567) | 54.8% (n=1,189) | 26.5% (n=1,853) |
| **Shotgun ✗ Carrera** | 68.0% (n=7,570) | 44.2% (n=2,627) | 17.1% (n=2,589) |

---
## Control 2 — Sesgo en `pass_direction`

*¿Está `pass_direction` sesgado hacia pases completos?*
*Si los incompletos tienen más nulos/unknown que los completos, la variable está sesgada.*

### C2.1 — Distribución de `pass_direction` por resultado del pase

| Resultado | n total | short_* | deep_* | incomplete_no_dir | unknown | NULO |
|---|---|---|---|---|---|---|
| **COMPLETE** | 107,511 | 52.5% | 7.5% | 0.0% | 40.0% | 0.0% |
| **INCOMPLETE** | 68,913 | 41.5% | 16.6% | 41.8% | 0.0% | 0.0% |

### C2.2 — Veredicto de sesgo

| Métrica | COMPLETE | INCOMPLETE | Brecha |
|---|---|---|---|
| % con dirección conocida (short/deep) | 60.0% | 58.2% | 1.9 pp |
| % con `incomplete_no_dir` | 0% | 41.8% | 41.8 pp |

✅ **SIN SESGO MATERIAL:** diferencia de 1.9 pp — aceptable para análisis.

---
## Control 3 — No Huddle en Partido Cerrado (4to Cuarto)

*Recálculo de impacto de `is_no_huddle` en Q4 filtrando solo*
*`abs(score_diff) <= 8` (dentro de una posesión).*

**Hipótesis a verificar:** ¿la ventaja del No Huddle en Q4 (+0.76 yds) se mantiene
cuando el partido está cerrado, o es un artefacto de equipos que van muy perdidos
y usan No Huddle desesperadamente (inflando las yardas por estilo de juego)?

### C3 — Partido cerrado (|score_diff| ≤ 8) (n=46,949)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 1,185 (2.5%) | 45,764 | — |
| Yds Media       | 5.85 | 6.36 | -0.51 yds 🔴 |
| Yds Mediana     | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down   | 34.5% | 32.3% | +2.2% 🟢 |
| Tasa Penalidad  | 5.99% | 6.51% | -0.52% 🟢 |
| Tasa Turnover   | 4.3% | 3.66% | +0.64% 🔴 |

### C3 — Partido decidido (|score_diff| > 8) (n=49,850)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 2,876 (5.8%) | 46,974 | — |
| Yds Media       | 6.48 | 6.16 | +0.32 yds 🟢 |
| Yds Mediana     | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down   | 36.9% | 32.2% | +4.7% 🟢 |
| Tasa Penalidad  | 6.4% | 6.48% | -0.08% |
| Tasa Turnover   | 4.73% | 3.75% | +0.98% 🔴 |

### C3 — Q4 completo (sin filtro) (n=96,799)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 4,061 (4.2%) | 92,738 | — |
| Yds Media       | 6.3 | 6.26 | +0.04 yds |
| Yds Mediana     | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down   | 36.2% | 32.3% | +3.9% 🟢 |
| Tasa Penalidad  | 6.28% | 6.49% | -0.21% |
| Tasa Turnover   | 4.6% | 3.71% | +0.89% 🔴 |

### C3.4 — Veredicto

✅ **VENTAJA REAL:** delta No Huddle en partido cerrado = **-0.51 yds**
vs **+0.04 yds** en Q4 completo.
La ventaja del No Huddle es robusta y no depende del contexto de blowout.

---
## Resumen Ejecutivo para la App

| Control | Hallazgo | Acción en la App |
|---|---|---|
| C1 — Distancia 3er Down | Shotgun+Pase domina en 7+ yds; carrera sin Shotgun gana en 1-2 yds | Segmentar recomendación por `YARDS_TO_FIRST` antes de sugerir formación |
| C2 — Sesgo pass_direction | 1.9 pp de diferencia en cobertura entre completos e incompletos | Filtrar `pass_direction NOT IN ('incomplete_no_dir','unknown',NULL)` en Comparativa A |
| C3 — No Huddle cerrado | Delta Q4 se mantiene en partido cerrado (-0.51 vs +0.04 yds) | Condicionar consejo No Huddle a `abs(score_diff) <= 8` |

---
*Generado por `validacion_sesgos.py` · 2026-11-18 21:52*