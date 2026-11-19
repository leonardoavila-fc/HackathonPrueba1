# Tesis del Coach — Prueba de Hipótesis Táctica NFL (2002-2012)
*Generado con `uv run python build_clean.py` · 2026-11-18 21:42*
*Fuente: `nfl_clean.parquet` · 411,134 jugadas limpias*

---
## 0. Auditoría de Sacks

*Verificación de que las jugadas con etiqueta `SACK` tienen yardas negativas y no nulos.*

| Métrica | Valor | % sobre sacks |
|---|---|---|
| Total jugadas con SACK | 12,098 | 100% |
| Yardas negativas (correcto) | 10,200 | 84.3% |
| Yardas = 0 | 1,876 | 15.5% |
| Yardas positivas (error) | 6 | 0.0% |
| Nulos (sin extracción) | 16 | 0.1% |
| Media de yards_gained en sacks | -5.6 yds | — |
| Mediana de yards_gained en sacks | -6.0 yds | — |

**Muestra de 5 sacks para verificar:**

| DESCRIPTION (primeros 100 chars) | yards_gained |
|---|---|
| `(5:50) D.Culpepper sacked at MIN 0 for -1 yards (K.Edwards). FUMBLES (K.Edwards) touched at MIN 0 RE` | **-1** |
| `(13:11) A.Smith sacked at SEA 41 for -4 yards. FUMBLES and recovers at SEA 41. A.Smith to SEA 41 for` | **0** |
| `(10:48) T.Green sacked at KC 14 for -3 yards (M.Patterson).` | **-3** |
| `(:55) C.Palmer sacked at NYG 12 for -8 yards (M.Kiwanuka).` | **-8** |
| `(4:36) (Shotgun) S.King sacked at ARZ 47 for -6 yards (P.Kerney).` | **-6** |

**16 sacks sin extracción (muestra):**

| DESCRIPTION |
|---|
| `TWO-POINT CONVERSION ATTEMPT. M.Hasselbeck is sacked. ATTEMPT FAILS.` |
| `TWO-POINT CONVERSION ATTEMPT. R.Gannon is sacked. ATTEMPT FAILS.` |
| `TWO-POINT CONVERSION ATTEMPT. E.Manning is sacked. ATTEMPT FAILS.` |

---
## Comparativa A — Zonas de Pase por Down

*Solo jugadas de pase (PASS_COMPLETE + PASS_INCOMPLETE + SACK) · downs 1-4*

**Hipótesis:** los pases cortos al centro (`short_middle`) tienen mayor tasa de 1er down en downs cortos (1-2), mientras que los pases profundos se usan más en 3er down largo.

### A.1 — 1er Down (n=39,048 jugadas de pase)

| Zona | n | % uso | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|
| **Short Right** | 13,130 | 33.6% | 5.75 yds | 5.0 yds | 23.5% 🔴 | 1.13% |
| **Short Left** | 11,044 | 28.3% | 6.23 yds | 5.0 yds | 26.2% 🔴 | 1.06% |
| **Short Middle** | 6,576 | 16.8% | 7.19 yds | 6.0 yds | 31.6% 🔴 | 1.22% |
| **Deep Left** | 3,020 | 7.7% | 11.51 yds | 0.0 yds | 39.2% 🔴 | 0.7% |
| **Deep Right** | 2,986 | 7.6% | 11.13 yds | 0.0 yds | 37.9% 🔴 | 0.74% |
| **Deep Middle** | 2,292 | 5.9% | 14.85 yds | 16.0 yds | 52.7% | 1.22% |

### A.2 — 2er Down (n=34,425 jugadas de pase)

| Zona | n | % uso | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|
| **Short Right** | 12,183 | 35.4% | 5.38 yds | 4.0 yds | 31.2% 🔴 | 1.01% |
| **Short Left** | 10,193 | 29.6% | 5.88 yds | 5.0 yds | 33.3% 🔴 | 1.25% |
| **Short Middle** | 6,468 | 18.8% | 6.74 yds | 6.0 yds | 37.3% 🔴 | 1.33% |
| **Deep Right** | 2,117 | 6.1% | 11.03 yds | 0.0 yds | 38.4% 🔴 | 0.71% |
| **Deep Left** | 2,077 | 6.0% | 10.8 yds | 0.0 yds | 38.0% 🔴 | 0.39% |
| **Deep Middle** | 1,387 | 4.0% | 12.79 yds | 0.0 yds | 48.6% | 0.58% |

### A.3 — 3er Down (n=29,530 jugadas de pase)

| Zona | n | % uso | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|
| **Short Right** | 9,454 | 32.0% | 5.62 yds | 4.0 yds | 39.3% 🔴 | 0.97% |
| **Short Left** | 8,154 | 27.6% | 5.75 yds | 4.0 yds | 39.8% 🔴 | 0.82% |
| **Short Middle** | 6,609 | 22.4% | 6.98 yds | 6.0 yds | 43.4% | 1.21% |
| **Deep Right** | 2,061 | 7.0% | 10.2 yds | 0.0 yds | 34.3% 🔴 | 0.58% |
| **Deep Left** | 1,891 | 6.4% | 10.24 yds | 0.0 yds | 35.4% 🔴 | 0.58% |
| **Deep Middle** | 1,361 | 4.6% | 12.2 yds | 0.0 yds | 45.6% | 1.25% |

### A.4 — 4er Down (n=1,640 jugadas de pase)

| Zona | n | % uso | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|
| **Short Right** | 498 | 30.4% | 5.04 yds | 2.0 yds | 47.0% | 1.61% |
| **Short Left** | 439 | 26.8% | 5.83 yds | 4.0 yds | 50.6% | 0.91% |
| **Short Middle** | 344 | 21.0% | 6.07 yds | 3.0 yds | 47.1% | 0.58% |
| **Deep Right** | 153 | 9.3% | 6.54 yds | 0.0 yds | 26.8% 🔴 | 0.65% |
| **Deep Left** | 132 | 8.0% | 9.04 yds | 0.0 yds | 33.3% 🔴 | 0.76% |
| **Deep Middle** | 74 | 4.5% | 13.51 yds | 16.5 yds | 50.0% | 0.0% |

### A.5 — Resumen Cross-Down: zonas cortas (% tasa de 1er Down)

| Zona | Down 1 | Down 2 | Down 3 | Down 4 |
|---|---|---|---|---|
| `Short Left` | 26.2% (n=11,044) | 33.3% (n=10,193) | 39.8% (n=8,154) | 50.6% (n=439) |
| `Short Middle` | 31.6% (n=6,576) | 37.3% (n=6,468) | 43.4% (n=6,609) | 47.1% (n=344) |
| `Short Right` | 23.5% (n=13,130) | 31.2% (n=12,183) | 39.3% (n=9,454) | 47.0% (n=498) |

---
## Comparativa B — Formación (Shotgun) vs Tendencia por Down

**Hipótesis:** en Shotgun, los equipos pasan más en 1er down (renunciando a la carrera) pero son más eficientes en 3er down largo. Sin Shotgun, la carrera domina en 1er down.

### B.1 — 1er Down (n=151,698)

| Formación | Tipo jugada | n | % del down | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|---|
| Shotgun ✓ | Pase | 17,200 | 11.3% | 7.04 yds | 5.0 yds | 28.1% | 0.0% |
| Shotgun ✓ | Carrera | 4,138 | 2.7% | 5.4 yds | 4.0 yds | 16.4% | 1.26% |
| Shotgun ✗ | Pase | 47,956 | 31.6% | 7.54 yds | 5.0 yds | 29.5% | 0.0% |
| Shotgun ✗ | Carrera | 71,615 | 47.2% | 4.29 yds | 3.0 yds | 12.3% | 1.05% |

### B.3 — 3er Down (n=75,947)

| Formación | Tipo jugada | n | % del down | Yds Media | Yds Mediana | Tasa 1er Down | Tasa Turnover |
|---|---|---|---|---|---|---|---|
| Shotgun ✓ | Pase | 29,716 | 39.1% | 7.12 yds | 4.0 yds | 39.1% | 0.0% |
| Shotgun ✓ | Carrera | 3,609 | 4.8% | 6.47 yds | 5.0 yds | 42.5% | 2.16% |
| Shotgun ✗ | Pase | 19,269 | 25.4% | 6.27 yds | 3.0 yds | 40.4% | 0.0% |
| Shotgun ✗ | Carrera | 12,787 | 16.8% | 4.03 yds | 2.0 yds | 52.8% | 1.46% |

### B.3 — Cruce Shotgun × Tipo en 3er Down (Tasa de 1er Down)

| | Pase | Carrera |
|---|---|---|
| **Shotgun ✓** | 39.1% (n=29,716) | 42.5% (n=3,609) |
| **Shotgun ✗** | 40.4% (n=19,269) | 52.8% (n=12,787) |

---
## Comparativa C — Ritmo (No Huddle) por Cuarto

**Hipótesis:** el No Huddle aumenta la eficiencia ofensiva (más yardas) pero también eleva la tasa de penalizaciones y turnovers por el mayor ritmo y complejidad de ejecución.

### C.1 — Cuarto 1 (n=88,664)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 1,685 (1.9%) | 86,979 | — |
| Yds Media | 5.29 | 5.6 | -0.31 yds |
| Yds Mediana | 3.0 | 3.0 | +0.0 yds |
| Tasa 1er Down | 30.1% | 28.4% | +1.7% 🟢 |
| Tasa Penalidad | 8.25% | 8.61% | -0.36% |
| Tasa Turnover | 2.67% | 2.95% | -0.28% |

### C.2 — Cuarto 2 (n=103,902)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 2,875 (2.8%) | 101,027 | — |
| Yds Media | 5.65 | 5.8 | -0.15 yds |
| Yds Mediana | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down | 32.9% | 29.7% | +3.2% 🟢 |
| Tasa Penalidad | 9.63% | 9.39% | +0.24% |
| Tasa Turnover | 2.99% | 3.27% | -0.28% |

### C.3 — Cuarto 3 (n=88,927)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 1,786 (2.0%) | 87,141 | — |
| Yds Media | 5.91 | 5.72 | +0.19 yds |
| Yds Mediana | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down | 31.4% | 28.6% | +2.8% 🟢 |
| Tasa Penalidad | 8.73% | 8.94% | -0.21% |
| Tasa Turnover | 3.3% | 3.23% | +0.07% |

### C.4 — Cuarto 4 (n=100,637)

| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |
|---|---|---|---|
| Jugadas | 4,164 (4.1%) | 96,473 | — |
| Yds Media | 6.3 | 5.54 | +0.76 yds 🟢 |
| Yds Mediana | 4.0 | 3.0 | +1.0 yds 🟢 |
| Tasa 1er Down | 36.2% | 28.7% | +7.5% 🟢 |
| Tasa Penalidad | 8.36% | 8.78% | -0.42% |
| Tasa Turnover | 4.73% | 3.69% | +1.04% 🔴 |

### C.5 — Resumen Cross-Cuarto: Yds Media No Huddle vs Normal

| Cuarto | No Huddle Yds | Normal Yds | Δ Yds | No Huddle Pen% | Normal Pen% |
|---|---|---|---|---|---|
| Q1 | 5.29 | 5.6 | -0.31 | 8.25% | 8.61% |
| Q2 | 5.65 | 5.8 | -0.15 | 9.63% | 9.39% |
| Q3 | 5.91 | 5.72 | +0.19 | 8.73% | 8.94% |
| Q4 | 6.3 | 5.54 | +0.76 | 8.36% | 8.78% |

---
## Conclusiones

### Comparativa A — Zonas de Pase
- **Mayor tasa de 1er Down:** `Deep Middle` (49.6%)
- **Mayor riesgo de turnover:** `Short Middle` (1.2%)

### Comparativa B — Formación
- En **1er down**, Shotgun ✓ usa el pase significativamente más que Shotgun ✗ que prefiere la carrera.
- En **3er down**, la mayor tasa de conversión la registra Shotgun ✓ + Pase.

### Comparativa C — Ritmo
- No Huddle genera **5.89 yds/jugada** vs 5.67 en ritmo normal (delta: +0.22 yds).
- Tasa de penalidad No Huddle: **8.76%** vs 8.94% normal.
- La hipótesis **SE CONFIRMA**: No Huddle es más eficiente en yardas.

---
*Generado por `build_clean.py` · uv run python · dataset: 411,134 jugadas limpias · 2026-11-18 21:42*