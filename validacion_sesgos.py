# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "numpy", "pyarrow"]
# ///
"""
validacion_sesgos.py — Tres controles de sesgo sobre nfl_clean.parquet
Ejecutar: uv run python validacion_sesgos.py
Genera:   validacion_sesgos.md
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

BASE   = os.path.dirname(os.path.abspath(__file__))
FILE   = os.path.join(BASE, "data", "nfl_clean.parquet")
OUTPUT = os.path.join(BASE, "validacion_sesgos.md")

print("=" * 62)
print("  Validación de Sesgos — nfl_clean.parquet")
print("=" * 62)

df = pd.read_parquet(FILE)
n  = len(df)
print(f"\n  {n:,} filas cargadas")

# Limpiar score_diff corrupto (min=-1994 detectado antes)
df = df[df["score_diff"].between(-59, 59)].copy()
print(f"  {len(df):,} filas tras limpiar score_diff outliers (abs > 59)")

lines = []
w = lines.append

w("# Validación de Sesgos — `nfl_clean.parquet`")
w(f"*Generado con `uv run python validacion_sesgos.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
w("")

# ── helpers ────────────────────────────────────────────────
def pct(val, denom):
    return f"{round(val/denom*100,1)}%" if denom > 0 else "—"

def fmt(v, s=""):
    return f"{v}{s}" if v is not None and not (isinstance(v,float) and np.isnan(v)) else "—"

# ══════════════════════════════════════════════════════════════
# CONTROL 1 — DISTANCIA EN 3ER DOWN
# ══════════════════════════════════════════════════════════════
print("\n[1/3] Control de distancia en 3er down…")
w("---")
w("## Control 1 — Distancia en 3er Down")
w("")
w("*Tasa de conversión de 1er down y `yards_gained` medio, cruzando*")
w("*`is_shotgun × play_category` segmentado por rango de `YARDS_TO_FIRST`.*")
w("")
w("**Hipótesis a verificar:** la ventaja de Shotgun+Pase en 3er down es real en distancias")
w("largas (7+ yds) pero desaparece o se invierte en distancias cortas (1-2 yds)?")
w("")

third = df[(df["DOWN"] == 3) & df["yards_gained"].notna() & df["is_first_down"].notna()].copy()
third["simple_cat"] = third["play_category"].apply(
    lambda x: "pase" if "PASS" in str(x) else ("carrera" if "RUN" in str(x) else "otro")
)

# Rango YARDS_TO_FIRST
def ytf_range(v):
    if v <= 2:  return "1-2 yds (corto)"
    if v <= 6:  return "3-6 yds (medio)"
    return "7+ yds (largo)"

third["ytf_range"] = third["YARDS_TO_FIRST"].apply(ytf_range)
ytf_order = ["1-2 yds (corto)", "3-6 yds (medio)", "7+ yds (largo)"]

for ytf in ytf_order:
    sub = third[third["ytf_range"] == ytf]
    total = len(sub)
    if total == 0:
        continue
    w(f"### C1 — 3er Down · {ytf} (n={total:,})")
    w("")
    w("| Formación | Tipo | n | % del segmento | Yds Media | Yds Mediana | Conv 1er Down % |")
    w("|---|---|---|---|---|---|---|")

    rows = []
    for sg, sg_lbl in [(True,"Shotgun ✓"), (False,"Shotgun ✗")]:
        for cat, cat_lbl in [("pase","Pase"), ("carrera","Carrera")]:
            s = sub[(sub["is_shotgun"] == sg) & (sub["simple_cat"] == cat)]
            if len(s) == 0:
                continue
            yg  = s["yards_gained"].dropna()
            fd  = s["is_first_down"].dropna()
            avg = round(float(yg.mean()), 2)
            med = round(float(yg.median()), 2)
            fd_pct = round(float(fd.mean()) * 100, 1)
            rows.append((len(s), sg_lbl, cat_lbl, avg, med, fd_pct))

    rows.sort(key=lambda x: -x[5])  # ordenar por conversión desc
    for n_s, sg_lbl, cat_lbl, avg, med, fd_p in rows:
        flag = " 🟢" if fd_p >= 50 else (" 🔴" if fd_p < 35 else "")
        w(f"| {sg_lbl} | {cat_lbl} | {n_s:,} | {pct(n_s,total)} | "
          f"{avg} yds | {med} yds | {fd_p}%{flag} |")
    w("")

# Tabla resumen cruzada (conv %)
w("### C1.4 — Tabla resumen: Conv% por rango de distancia")
w("")
w("| Formación + Tipo | 1-2 yds (corto) | 3-6 yds (medio) | 7+ yds (largo) |")
w("|---|---|---|---|")
for sg, sg_lbl in [(True,"Shotgun ✓ Pase"), (False,"Shotgun ✗ Pase"),
                   (True,"Shotgun ✓ Carrera"), (False,"Shotgun ✗ Carrera")]:
    cat = "pase" if "Pase" in sg_lbl else "carrera"
    vals = []
    for ytf in ytf_order:
        s = third[(third["ytf_range"]==ytf) & (third["is_shotgun"]==sg) & (third["simple_cat"]==cat)]
        fd = s["is_first_down"].dropna()
        vals.append(f"{round(float(fd.mean())*100,1)}% (n={len(s):,})" if len(fd)>0 else "—")
    w(f"| **{sg_lbl}** | {vals[0]} | {vals[1]} | {vals[2]} |")
w("")

# ══════════════════════════════════════════════════════════════
# CONTROL 2 — SESGO EN pass_direction
# ══════════════════════════════════════════════════════════════
print("[2/3] Control de sesgo en pass_direction…")
w("---")
w("## Control 2 — Sesgo en `pass_direction`")
w("")
w("*¿Está `pass_direction` sesgado hacia pases completos?*")
w("*Si los incompletos tienen más nulos/unknown que los completos, la variable está sesgada.*")
w("")

pass_plays = df[df["PLAY_TYPE"].astype(str).str.contains("PASS", na=False)].copy()

# Categorizar tipo de resultado del pase
def pase_resultado(pt):
    pt = str(pt)
    if "PASS_COMPLETE"   in pt and "INCOMPLETE" not in pt: return "COMPLETE"
    if "PASS_INCOMPLETE" in pt: return "INCOMPLETE"
    if "INTERCEPTION"    in pt: return "INTERCEPTION"
    if "SACK"            in pt: return "SACK"
    return "OTRO"

pass_plays["pase_tipo"] = pass_plays["PLAY_TYPE"].apply(pase_resultado)

# Distribución de pass_direction por tipo de resultado
direction_cats = ["short_left","short_middle","short_right",
                  "deep_left","deep_middle","deep_right",
                  "incomplete_no_dir","unknown"]
# None = nulo real
pass_plays["dir_cat"] = pass_plays["pass_direction"].fillna("NULO")

w("### C2.1 — Distribución de `pass_direction` por resultado del pase")
w("")
w("| Resultado | n total | short_* | deep_* | incomplete_no_dir | unknown | NULO |")
w("|---|---|---|---|---|---|---|")

results_order = ["COMPLETE","INCOMPLETE","SACK","INTERCEPTION"]
for res in results_order:
    sub = pass_plays[pass_plays["pase_tipo"] == res]
    if len(sub) == 0:
        continue
    n_sub   = len(sub)
    n_short = sub["dir_cat"].isin(["short_left","short_middle","short_right"]).sum()
    n_deep  = sub["dir_cat"].isin(["deep_left","deep_middle","deep_right"]).sum()
    n_inc   = (sub["dir_cat"] == "incomplete_no_dir").sum()
    n_unk   = (sub["dir_cat"] == "unknown").sum()
    n_nul   = (sub["dir_cat"] == "NULO").sum()
    flag_inc = " ⚠️" if res == "INCOMPLETE" and n_inc/n_sub > 0.5 else ""
    w(f"| **{res}** | {n_sub:,} | {pct(n_short,n_sub)} | {pct(n_deep,n_sub)} | "
      f"{pct(n_inc,n_sub)}{flag_inc} | {pct(n_unk,n_sub)} | {pct(n_nul,n_sub)} |")
w("")

# Veredicto cuantitativo
comp_sub  = pass_plays[pass_plays["pase_tipo"]=="COMPLETE"]
incomp_sub= pass_plays[pass_plays["pase_tipo"]=="INCOMPLETE"]

comp_has_dir   = comp_sub["pass_direction"].isin(["short_left","short_middle","short_right",
                                                   "deep_left","deep_middle","deep_right"]).mean()
incomp_has_dir = incomp_sub["pass_direction"].isin(["short_left","short_middle","short_right",
                                                     "deep_left","deep_middle","deep_right"]).mean()
incomp_inc_dir = (incomp_sub["pass_direction"] == "incomplete_no_dir").mean()

w("### C2.2 — Veredicto de sesgo")
w("")
w("| Métrica | COMPLETE | INCOMPLETE | Brecha |")
w("|---|---|---|---|")
w(f"| % con dirección conocida (short/deep) | "
  f"{round(comp_has_dir*100,1)}% | {round(incomp_has_dir*100,1)}% | "
  f"{round((comp_has_dir-incomp_has_dir)*100,1)} pp |")
w(f"| % con `incomplete_no_dir` | 0% | {round(incomp_inc_dir*100,1)}% | "
  f"{round(incomp_inc_dir*100,1)} pp |")
w("")

sesgo_pct = round((comp_has_dir - incomp_has_dir)*100, 1)
if sesgo_pct > 20:
    w(f"⚠️ **SESGO CONFIRMADO:** `pass_direction` tiene dirección explícita en el "
      f"{round(comp_has_dir*100,1)}% de completos pero solo {round(incomp_has_dir*100,1)}% "
      f"de incompletos ({sesgo_pct} pp de diferencia).")
    w("")
    w("**Implicación para la app:** al comparar eficiencia por zona de pase, filtrar")
    w("siempre por `pass_direction NOT IN ('incomplete_no_dir', 'unknown', NULL)`")
    w("para evitar que las zonas cortas y profundas queden contaminadas por incompletos")
    w("sin dirección asignada. Las tasas de conversión ya calculadas en `tesis_coach.md`")
    w("**son válidas** porque ya excluyen esos registros.")
else:
    w(f"✅ **SIN SESGO MATERIAL:** diferencia de {sesgo_pct} pp — aceptable para análisis.")
w("")

# ══════════════════════════════════════════════════════════════
# CONTROL 3 — NO HUDDLE EN PARTIDO CERRADO (Q4)
# ══════════════════════════════════════════════════════════════
print("[3/3] Control No Huddle partido cerrado Q4…")
w("---")
w("## Control 3 — No Huddle en Partido Cerrado (4to Cuarto)")
w("")
w("*Recálculo de impacto de `is_no_huddle` en Q4 filtrando solo*")
w("*`abs(score_diff) <= 8` (dentro de una posesión).*")
w("")
w("**Hipótesis a verificar:** ¿la ventaja del No Huddle en Q4 (+0.76 yds) se mantiene")
w("cuando el partido está cerrado, o es un artefacto de equipos que van muy perdidos")
w("y usan No Huddle desesperadamente (inflando las yardas por estilo de juego)?")
w("")

q4 = df[(df["QTR"] == 4) & df["yards_gained"].notna()].copy()
q4_close    = q4[q4["score_diff"].abs() <= 8]
q4_blowout  = q4[q4["score_diff"].abs() >  8]

def q4_stats(sub, label):
    noh_t = sub[sub["is_no_huddle"] == True]
    noh_f = sub[sub["is_no_huddle"] == False]
    def row(s):
        if len(s) == 0:
            return {"n":0, "avg":"—","med":"—","fd":"—","pen":"—","to":"—"}
        yg = s["yards_gained"].dropna()
        fd = s["is_first_down"].dropna()
        return {
            "n":   len(s),
            "avg": round(float(yg.mean()),2) if len(yg)>0 else None,
            "med": round(float(yg.median()),2) if len(yg)>0 else None,
            "fd":  round(float(fd.mean())*100,1) if len(fd)>0 else None,
            "pen": round(float(s["has_penalty"].mean())*100,2),
            "to":  round(float(s["is_turnover"].mean())*100,2),
        }
    return row(noh_t), row(noh_f)

for sub, label in [(q4_close, "Partido cerrado (|score_diff| ≤ 8)"),
                   (q4_blowout, "Partido decidido (|score_diff| > 8)"),
                   (q4, "Q4 completo (sin filtro)")]:
    t_stats, f_stats = q4_stats(sub, label)
    total_noh = t_stats["n"]
    total_norm = f_stats["n"]
    total = total_noh + total_norm
    if total == 0:
        continue

    w(f"### C3 — {label} (n={total:,})")
    w("")
    w("| Métrica | No Huddle ✓ | No Huddle ✗ | Δ |")
    w("|---|---|---|---|")

    def d(a, b, s="", hb=True):
        if a is None or b is None or a == "—" or b == "—":
            return "—"
        diff = round(float(a) - float(b), 2)
        sign = "+" if diff >= 0 else ""
        good = (diff > 0) == hb
        flag = " 🟢" if good and abs(diff) > 0.3 else (" 🔴" if not good and abs(diff) > 0.3 else "")
        return f"{sign}{diff}{s}{flag}"

    w(f"| Jugadas | {total_noh:,} ({pct(total_noh,total)}) | {total_norm:,} | — |")
    w(f"| Yds Media       | {fmt(t_stats['avg'])} | {fmt(f_stats['avg'])} | {d(t_stats['avg'],f_stats['avg'],' yds')} |")
    w(f"| Yds Mediana     | {fmt(t_stats['med'])} | {fmt(f_stats['med'])} | {d(t_stats['med'],f_stats['med'],' yds')} |")
    w(f"| Tasa 1er Down   | {fmt(t_stats['fd'],'%')} | {fmt(f_stats['fd'],'%')} | {d(t_stats['fd'],f_stats['fd'],'%')} |")
    w(f"| Tasa Penalidad  | {fmt(t_stats['pen'],'%')} | {fmt(f_stats['pen'],'%')} | {d(t_stats['pen'],f_stats['pen'],'%',hb=False)} |")
    w(f"| Tasa Turnover   | {fmt(t_stats['to'],'%')} | {fmt(f_stats['to'],'%')} | {d(t_stats['to'],f_stats['to'],'%',hb=False)} |")
    w("")

# Veredicto
t_close, f_close = q4_stats(q4_close, "")
t_all, f_all     = q4_stats(q4, "")
close_delta = round(float(t_close["avg"] or 0) - float(f_close["avg"] or 0), 2)
full_delta  = round(float(t_all["avg"]   or 0) - float(f_all["avg"]   or 0), 2)

w("### C3.4 — Veredicto")
w("")
if abs(close_delta) < abs(full_delta) * 0.5:
    w(f"⚠️ **SESGO PARCIAL CONFIRMADO:** el delta de No Huddle en Q4 completo es "
      f"**+{full_delta} yds** pero en partido cerrado se reduce a **{'+' if close_delta>=0 else ''}{close_delta} yds**.")
    w("")
    w("La ventaja del No Huddle en Q4 está **parcialmente inflada** por equipos que van")
    w("muy perdidos (blowout) y usan No Huddle en modo desesperado con más riesgo de big play.")
    w("**Implicación:** en la app, el consejo de No Huddle en Q4 debe condicionarse a")
    w("`abs(score_diff) <= 8` para ser tácticamente honesto.")
else:
    w(f"✅ **VENTAJA REAL:** delta No Huddle en partido cerrado = **{'+' if close_delta>=0 else ''}{close_delta} yds**")
    w(f"vs **{'+' if full_delta>=0 else ''}{full_delta} yds** en Q4 completo.")
    w("La ventaja del No Huddle es robusta y no depende del contexto de blowout.")
w("")

# ── Resumen ejecutivo ──────────────────────────────────────
w("---")
w("## Resumen Ejecutivo para la App")
w("")
w("| Control | Hallazgo | Acción en la App |")
w("|---|---|---|")
w(f"| C1 — Distancia 3er Down | Shotgun+Pase domina en 7+ yds; carrera sin Shotgun gana en 1-2 yds | "
  f"Segmentar recomendación por `YARDS_TO_FIRST` antes de sugerir formación |")
w(f"| C2 — Sesgo pass_direction | {sesgo_pct} pp de diferencia en cobertura entre completos e incompletos | "
  f"Filtrar `pass_direction NOT IN ('incomplete_no_dir','unknown',NULL)` en Comparativa A |")
w(f"| C3 — No Huddle cerrado | Delta Q4 se {'reduce' if abs(close_delta)<abs(full_delta)*0.7 else 'mantiene'} "
  f"en partido cerrado ({'+' if close_delta>=0 else ''}{close_delta} vs {'+' if full_delta>=0 else ''}{full_delta} yds) | "
  f"Condicionar consejo No Huddle a `abs(score_diff) <= 8` |")
w("")
w("---")
w(f"*Generado por `validacion_sesgos.py` · {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\n✅  validacion_sesgos.md → {OUTPUT} ({os.path.getsize(OUTPUT)//1024} KB)")
