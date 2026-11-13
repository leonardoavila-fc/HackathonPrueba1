"""
Generador de gráficas para el dataset plays.csv (NFL 2017)
Ejecutar desde la raíz del proyecto: python visualizaciones/generar_graficas.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
import os

# ── Configuración general ──────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})
PALETTE = sns.color_palette("Set2")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(os.path.dirname(OUTPUT_DIR), "data", "plays.csv")

# ── Carga y limpieza ───────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, na_values=["NA", ""])

# Separar jugadas regulares de jugadas especiales
regular = df[df["isSTPlay"] == False].copy()
especiales = df[df["isSTPlay"] == True].copy()

print(f"Dataset cargado: {len(df):,} jugadas | {df['gameId'].nunique()} partidos")

# ══════════════════════════════════════════════════════════════════════════════
# 1. TIPO DE JUGADAS — Pasé, Carrera, Especiales
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 7))

tipos = {
    "Pase\n(completo/incompleto/sack)": regular["PassResult"].notna().sum(),
    "Carrera": regular["PassResult"].isna().sum(),
    "Jugadas especiales": len(especiales),
}
colores = [PALETTE[0], PALETTE[1], PALETTE[2]]
wedges, texts, autotexts = ax.pie(
    tipos.values(), labels=tipos.keys(), colors=colores,
    autopct="%1.1f%%", startangle=140,
    wedgeprops={"edgecolor": "white", "linewidth": 2},
    textprops={"fontsize": 12},
)
for a in autotexts:
    a.set_fontsize(13)
    a.set_fontweight("bold")
ax.set_title("Distribución de tipo de jugadas\n(14 193 jugadas totales)", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "01_tipo_jugadas.png"), bbox_inches="tight")
plt.close()
print("✓ 01_tipo_jugadas.png")

# ══════════════════════════════════════════════════════════════════════════════
# 2. FORMACIONES OFENSIVAS
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

formaciones = regular["offenseFormation"].value_counts().dropna()
bars = ax.barh(formaciones.index[::-1], formaciones.values[::-1],
               color=sns.color_palette("Set2", len(formaciones)))
ax.set_xlabel("Número de jugadas", fontsize=12)
ax.set_title("Formaciones ofensivas más usadas", fontsize=14, fontweight="bold")
for bar, val in zip(bars, formaciones.values[::-1]):
    ax.text(bar.get_width() + 30, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", fontsize=10)
ax.set_xlim(0, formaciones.max() * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "02_formaciones_ofensivas.png"), bbox_inches="tight")
plt.close()
print("✓ 02_formaciones_ofensivas.png")

# ══════════════════════════════════════════════════════════════════════════════
# 3. RESULTADO DE PASE
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 5))

labels_map = {"C": "Completo", "I": "Incompleto", "S": "Sack", "R": "Scramble", "IN": "Interceptado"}
pass_data = regular["PassResult"].value_counts().reindex(["C", "I", "S", "R", "IN"]).dropna()
colores_pass = [PALETTE[0], PALETTE[3], PALETTE[1], PALETTE[4], PALETTE[2]]
bars = ax.bar([labels_map[k] for k in pass_data.index], pass_data.values,
              color=colores_pass, edgecolor="white", linewidth=1.5)
ax.set_ylabel("Jugadas", fontsize=12)
ax.set_title("Resultados de jugadas de pase", fontsize=14, fontweight="bold")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
            f"{int(bar.get_height()):,}", ha="center", fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "03_resultado_pases.png"), bbox_inches="tight")
plt.close()
print("✓ 03_resultado_pases.png")

# ══════════════════════════════════════════════════════════════════════════════
# 4. DISTRIBUCIÓN DE YARDAS POR JUGADA (PlayResult)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5))

play_res = regular["PlayResult"].dropna()
play_res_clipped = play_res.clip(-20, 40)
ax.hist(play_res_clipped, bins=60, color=PALETTE[0], edgecolor="white", linewidth=0.5)
ax.axvline(play_res.median(), color=PALETTE[2], linewidth=2, linestyle="--",
           label=f"Mediana: {play_res.median():.1f} yds")
ax.axvline(play_res.mean(), color=PALETTE[1], linewidth=2, linestyle="-.",
           label=f"Promedio: {play_res.mean():.1f} yds")
ax.set_xlabel("Yardas ganadas (recortado en -20 / +40)", fontsize=12)
ax.set_ylabel("Frecuencia", fontsize=12)
ax.set_title("Distribución de yardas por jugada regular", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "04_distribucion_yardas.png"), bbox_inches="tight")
plt.close()
print("✓ 04_distribucion_yardas.png")

# ══════════════════════════════════════════════════════════════════════════════
# 5. YARDAS POR DOWN
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 5))

downs_data = regular[regular["down"].isin([1, 2, 3, 4])]
down_labels = {1: "1er down", 2: "2do down", 3: "3er down", 4: "4to down"}
groups = [downs_data[downs_data["down"] == d]["PlayResult"].dropna() for d in [1, 2, 3, 4]]
bp = ax.boxplot(groups, patch_artist=True, notch=False,
                medianprops={"color": "white", "linewidth": 2.5})
for patch, color in zip(bp["boxes"], PALETTE[:4]):
    patch.set_facecolor(color)
    patch.set_alpha(0.8)
ax.set_xticklabels(list(down_labels.values()), fontsize=12)
ax.set_ylabel("Yardas ganadas", fontsize=12)
ax.set_title("Yardas ganadas por down", fontsize=14, fontweight="bold")
ax.set_ylim(-25, 50)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "05_yardas_por_down.png"), bbox_inches="tight")
plt.close()
print("✓ 05_yardas_por_down.png")

# ══════════════════════════════════════════════════════════════════════════════
# 6. DEFENSORES EN LA CAJA vs YARDAS GANADAS
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

ditb = regular[regular["defendersInTheBox"].notna()].copy()
ditb["defendersInTheBox"] = ditb["defendersInTheBox"].astype(int)
ditb_filtered = ditb[ditb["defendersInTheBox"].between(4, 9)]
means = ditb_filtered.groupby("defendersInTheBox")["PlayResult"].mean()
counts = ditb_filtered.groupby("defendersInTheBox")["PlayResult"].count()

bars = ax.bar(means.index, means.values,
              color=sns.color_palette("coolwarm_r", len(means)), edgecolor="white")
ax.axhline(0, color="gray", linewidth=1, linestyle="--")
ax.set_xlabel("Defensores en la caja (box)", fontsize=12)
ax.set_ylabel("Yardas promedio ganadas", fontsize=12)
ax.set_title("Yardas promedio según defensores en la caja", fontsize=14, fontweight="bold")
for bar, (idx, cnt) in zip(bars, counts.items()):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
            f"n={cnt:,}", ha="center", fontsize=9, color="gray")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "06_defensores_caja_vs_yardas.png"), bbox_inches="tight")
plt.close()
print("✓ 06_defensores_caja_vs_yardas.png")

# ══════════════════════════════════════════════════════════════════════════════
# 7. JUGADAS POR CUARTO
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 5))

cuartos_map = {1: "Q1", 2: "Q2", 3: "Q3", 4: "Q4", 5: "OT"}
cuartos = df["quarter"].value_counts().reindex([1, 2, 3, 4, 5]).dropna()
bars = ax.bar([cuartos_map[k] for k in cuartos.index], cuartos.values,
              color=PALETTE[:5], edgecolor="white", linewidth=1.5)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
            f"{int(bar.get_height()):,}", ha="center", fontsize=11)
ax.set_ylabel("Jugadas", fontsize=12)
ax.set_title("Jugadas por cuarto del partido", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "07_jugadas_por_cuarto.png"), bbox_inches="tight")
plt.close()
print("✓ 07_jugadas_por_cuarto.png")

# ══════════════════════════════════════════════════════════════════════════════
# 8. PAQUETES DEFENSIVOS MÁS USADOS
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

def_personnel = regular["personnel.defense"].value_counts().head(8).dropna()
bars = ax.barh(def_personnel.index[::-1], def_personnel.values[::-1],
               color=sns.color_palette("rocket_r", 8))
ax.set_xlabel("Número de jugadas", fontsize=12)
ax.set_title("Paquetes defensivos más frecuentes", fontsize=14, fontweight="bold")
for bar, val in zip(bars, def_personnel.values[::-1]):
    ax.text(bar.get_width() + 20, bar.get_y() + bar.get_height() / 2,
            f"{val:,}", va="center", fontsize=10)
ax.set_xlim(0, def_personnel.max() * 1.15)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "08_paquetes_defensivos.png"), bbox_inches="tight")
plt.close()
print("✓ 08_paquetes_defensivos.png")

# ══════════════════════════════════════════════════════════════════════════════
# 9. PENALIZACIONES POR EQUIPO (top 15)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 6))

pen_data = df[df["isPenalty"] == True]["possessionTeam"].value_counts().head(15)
bars = ax.barh(pen_data.index[::-1], pen_data.values[::-1],
               color=sns.color_palette("OrRd_r", 15))
ax.set_xlabel("Penalizaciones en posesión", fontsize=12)
ax.set_title("Top 15 equipos con más penalizaciones en posesión", fontsize=14, fontweight="bold")
for bar, val in zip(bars, pen_data.values[::-1]):
    ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "09_penalizaciones_por_equipo.png"), bbox_inches="tight")
plt.close()
print("✓ 09_penalizaciones_por_equipo.png")

# ══════════════════════════════════════════════════════════════════════════════
# 10. HEATMAP — Formación ofensiva vs Resultado del pase
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

cross = pd.crosstab(
    regular["offenseFormation"],
    regular["PassResult"]
).reindex(columns=["C", "I", "S", "R", "IN"]).dropna(how="all")
cross.columns = ["Completo", "Incompleto", "Sack", "Scramble", "Interceptado"]
cross_pct = cross.div(cross.sum(axis=1), axis=0) * 100

sns.heatmap(cross_pct, annot=True, fmt=".1f", cmap="YlGnBu",
            linewidths=0.5, linecolor="white", ax=ax,
            cbar_kws={"label": "% del total de pases"})
ax.set_title("Resultado del pase (%) según formación ofensiva", fontsize=13, fontweight="bold")
ax.set_xlabel("Resultado del pase", fontsize=11)
ax.set_ylabel("Formación", fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "10_heatmap_formacion_vs_pase.png"), bbox_inches="tight")
plt.close()
print("✓ 10_heatmap_formacion_vs_pase.png")

# ══════════════════════════════════════════════════════════════════════════════
# 11. EVOLUCIÓN DEL MARCADOR — promedio por cuarto
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

score_q = df[df["quarter"].isin([1, 2, 3, 4])].groupby("quarter").agg(
    home_avg=("HomeScoreAfterPlay", "max"),
    away_avg=("VisitorScoreAfterPlay", "max")
)
# Usamos el score promedio final por partido y cuarto
score_per_game = df[df["quarter"].isin([1, 2, 3, 4])].groupby(["gameId", "quarter"]).agg(
    home=("HomeScoreAfterPlay", "max"),
    away=("VisitorScoreAfterPlay", "max")
).reset_index()

score_avg = score_per_game.groupby("quarter")[["home", "away"]].mean()
ax.plot(score_avg.index, score_avg["home"], marker="o", linewidth=2.5,
        color=PALETTE[0], label="Local (promedio)")
ax.plot(score_avg.index, score_avg["away"], marker="s", linewidth=2.5,
        color=PALETTE[1], label="Visitante (promedio)")
ax.fill_between(score_avg.index, score_avg["home"], score_avg["away"], alpha=0.1, color="gray")
ax.set_xticks([1, 2, 3, 4])
ax.set_xticklabels(["Q1", "Q2", "Q3", "Q4"], fontsize=12)
ax.set_ylabel("Puntos promedio acumulados", fontsize=12)
ax.set_title("Evolución del marcador promedio por cuarto", fontsize=14, fontweight="bold")
ax.legend(fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "11_evolucion_marcador.png"), bbox_inches="tight")
plt.close()
print("✓ 11_evolucion_marcador.png")

# ══════════════════════════════════════════════════════════════════════════════
# 12. YARDAS DESPUÉS DEL CATCH (YAC) por largo del pase
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))

completed = regular[regular["PassResult"] == "C"].dropna(subset=["PassLength", "YardsAfterCatch"])
completed["PassLength"] = pd.to_numeric(completed["PassLength"], errors="coerce")
completed["YardsAfterCatch"] = pd.to_numeric(completed["YardsAfterCatch"], errors="coerce")

bins = [-15, -1, 4, 9, 14, 20, 50]
labels_bins = ["Neg/0", "Corto\n(1-4)", "Med\n(5-9)", "Largo\n(10-14)", "Muy largo\n(15-20)", "Deep\n(>20)"]
completed["pass_bin"] = pd.cut(completed["PassLength"], bins=bins, labels=labels_bins)
yac_by_bin = completed.groupby("pass_bin", observed=False)["YardsAfterCatch"].mean()

bars = ax.bar(yac_by_bin.index, yac_by_bin.values,
              color=sns.color_palette("viridis", len(yac_by_bin)), edgecolor="white")
ax.set_ylabel("YAC promedio (yardas)", fontsize=12)
ax.set_xlabel("Largo del pase", fontsize=12)
ax.set_title("Yardas después del catch (YAC) según largo del pase", fontsize=13, fontweight="bold")
for bar in bars:
    if not np.isnan(bar.get_height()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                f"{bar.get_height():.1f}", ha="center", fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "12_yac_por_largo_pase.png"), bbox_inches="tight")
plt.close()
print("✓ 12_yac_por_largo_pase.png")

print("\n✅ Todas las gráficas generadas en:", OUTPUT_DIR)
