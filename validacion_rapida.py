import pandas as pd

df = pd.read_parquet("data/nfl_clean.parquet")

print("=== 1. 3ER DOWN: SHOTGUN x JUGADA POR DISTANCIA ===")
d3 = df[(df["DOWN"] == 3) & (df["play_category"].isin(["PASS", "RUN"]))].copy()
d3["dist"] = pd.cut(d3["YARDS_TO_FIRST"], bins=[0, 2, 6, 100], labels=["1-2 yds", "3-6 yds", "7+ yds"])
print(d3.groupby(["dist", "is_shotgun", "play_category"], observed=False).agg(
    jugadas=("PLAY_ID", "count"),
    tasa_1st=("is_first_down", "mean"),
    yds_prom=("yards_gained", "mean")
).round(3))

print("\n=== 2. SESGO DE DIRECCION EN PASES INCOMPLETOS ===")
inc = df[df["PLAY_TYPE"].str.contains("PASS_INCOMPLETE", na=False)]["pass_direction"].isna().mean()
comp = df[df["PLAY_TYPE"].str.contains("PASS_COMPLETE", na=False)]["pass_direction"].isna().mean()
print(f"Nulos en INCOMPLETE: {inc:.1%} | Nulos en COMPLETE: {comp:.1%}")

print("\n=== 3. NO HUDDLE EN Q4 CERRADO (|score_diff| <= 8) ===")
q4 = df[(df["QTR"] == 4) & (df["score_diff"].abs() <= 8)]
print(q4.groupby("is_no_huddle").agg(
    jugadas=("PLAY_ID", "count"),
    yds_prom=("yards_gained", "mean"),
    tasa_turnover=("is_turnover", "mean"),
    tasa_castigo=("has_penalty", "mean")
).round(3))
