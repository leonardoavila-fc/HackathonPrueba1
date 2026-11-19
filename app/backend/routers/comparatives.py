"""
routers/comparatives.py — Comparativas tácticas (A, B, C) ya corregidas con sesgos
GET /api/comparatives/zones      → Comparativa A: Zonas de pase × DOWN
GET /api/comparatives/formation  → Comparativa B: Shotgun × play_category × DOWN
GET /api/comparatives/tempo      → Comparativa C: No Huddle × QTR (solo partido cerrado)
"""

from fastapi import APIRouter, Request
import pandas as pd
import numpy as np

router = APIRouter()

VALID_DIRS = ["short_left", "short_middle", "short_right",
              "deep_left",  "deep_middle",  "deep_right"]

DIR_LABELS = {
    "short_left":   "Short Left",
    "short_middle": "Short Middle",
    "short_right":  "Short Right",
    "deep_left":    "Deep Left",
    "deep_middle":  "Deep Middle",
    "deep_right":   "Deep Right",
}


def metrics(sub: pd.DataFrame) -> dict:
    if len(sub) == 0:
        return {"n": 0, "avg": None, "median": None, "fd_rate": None,
                "to_rate": None, "pen_rate": None}
    yg = sub["yards_gained"].dropna()
    fd = sub["is_first_down"].dropna().astype(float)
    return {
        "n":        int(len(sub)),
        "avg":      round(float(yg.mean()),   2) if len(yg) > 0 else None,
        "median":   round(float(yg.median()), 2) if len(yg) > 0 else None,
        "fd_rate":  round(float(fd.mean()) * 100, 1) if len(fd) > 0 else None,
        "to_rate":  round(float(sub["is_turnover"].mean()) * 100, 2),
        "pen_rate": round(float(sub["has_penalty"].mean()) * 100, 2),
    }


# ── Comparativa A — Zonas de pase ─────────────────────────
@router.get("/comparatives/zones")
def comparatives_zones(request: Request):
    """
    Comparativa A corregida: zonas de pase × DOWN.
    Excluye pass_direction == 'incomplete_no_dir' | 'unknown' | NULL (sesgo C2).
    """
    df = request.app.state.df

    pass_df = df[
        df["PLAY_TYPE"].astype(str).str.contains("PASS", na=False) &
        df["pass_direction"].isin(VALID_DIRS) &
        df["DOWN"].isin([1, 2, 3, 4])
    ].copy()

    result = {}
    for down in [1, 2, 3, 4]:
        sub_d = pass_df[pass_df["DOWN"] == down]
        down_data = []
        for d in VALID_DIRS:
            sub = sub_d[sub_d["pass_direction"] == d]
            m = metrics(sub)
            if m["n"] > 0:
                m["direction"] = d
                m["label"]     = DIR_LABELS[d]
                m["usage_pct"] = round(m["n"] / len(sub_d) * 100, 1) if len(sub_d) > 0 else 0
                down_data.append(m)
        down_data.sort(key=lambda x: -x["n"])
        result[f"down_{down}"] = {
            "total_pass_plays": int(len(sub_d)),
            "zones": down_data,
        }

    return {"comparative": "A", "title": "Zonas de Pase por Down", "data": result}


# ── Comparativa B — Formación × Tendencia ─────────────────
@router.get("/comparatives/formation")
def comparatives_formation(request: Request):
    """
    Comparativa B: Shotgun × play_category en 1er y 3er down.
    """
    df = request.app.state.df.copy()
    df["_cat"] = df["play_category"].apply(
        lambda x: "pase" if "PASS" in str(x) else ("carrera" if "RUN" in str(x) else "otro")
    )
    df = df[df["DOWN"].isin([1, 3])]

    result = {}
    for down in [1, 3]:
        sub_d = df[df["DOWN"] == down]
        total = len(sub_d)
        down_data = []
        for sg, sg_lbl in [(True, "Shotgun"), (False, "No Shotgun")]:
            for cat, cat_lbl in [("pase", "Pase"), ("carrera", "Carrera")]:
                sub = sub_d[(sub_d["is_shotgun"] == sg) & (sub_d["_cat"] == cat)]
                m = metrics(sub)
                m["formation"] = sg_lbl
                m["play_type"] = cat_lbl
                m["usage_pct"] = round(m["n"] / total * 100, 1) if total > 0 else 0
                down_data.append(m)
        result[f"down_{down}"] = {
            "total_plays": int(total),
            "breakdown": down_data,
        }

    return {"comparative": "B", "title": "Formación vs Tendencia", "data": result}


# ── Comparativa C — Ritmo No Huddle ───────────────────────
@router.get("/comparatives/tempo")
def comparatives_tempo(request: Request):
    """
    Comparativa C corregida: is_no_huddle × QTR.
    En Q4 solo partidos cerrados abs(score_diff) <= 8 (sesgo C3).
    """
    df = request.app.state.df.copy()
    df = df[df["DOWN"].isin([1, 2, 3, 4])]

    result = {}
    for qtr in [1, 2, 3, 4]:
        sub_q = df[df["QTR"] == qtr]
        # Corrección sesgo C3: Q4 solo partido cerrado
        if qtr == 4:
            sub_q = sub_q[sub_q["score_diff"].abs() <= 8]
        total = len(sub_q)
        noh_t = sub_q[sub_q["is_no_huddle"] == True]
        noh_f = sub_q[sub_q["is_no_huddle"] == False]
        mt = metrics(noh_t)
        mf = metrics(noh_f)

        def delta(a, b):
            if a is None or b is None:
                return None
            return round(a - b, 2)

        result[f"qtr_{qtr}"] = {
            "total_plays":    int(total),
            "no_huddle":      {**mt, "is_no_huddle": True},
            "normal":         {**mf, "is_no_huddle": False},
            "filtered_q4_close": qtr == 4,
            "delta": {
                "avg_yards":     delta(mt["avg"],      mf["avg"]),
                "median_yards":  delta(mt["median"],   mf["median"]),
                "fd_rate":       delta(mt["fd_rate"],  mf["fd_rate"]),
                "to_rate":       delta(mt["to_rate"],  mf["to_rate"]),
                "pen_rate":      delta(mt["pen_rate"], mf["pen_rate"]),
            },
        }

    return {"comparative": "C", "title": "Ritmo (No Huddle) por Cuarto", "data": result}
