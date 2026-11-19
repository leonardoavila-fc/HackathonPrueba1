"""
routers/scenarios.py — Endpoint de simulación de escenarios situacionales
GET /api/scenario
"""

from fastapi import APIRouter, Request, Query
from typing import Optional
import pandas as pd
import numpy as np

router = APIRouter()


def _metrics(sub: pd.DataFrame) -> dict:
    """Calcula métricas estándar para un subset de jugadas."""
    if len(sub) == 0:
        return {"n": 0, "avg_yards": None, "median_yards": None,
                "first_down_rate": None, "turnover_rate": None,
                "penalty_rate": None, "touchdown_rate": None, "sack_rate": None}

    yg  = sub["yards_gained"].dropna()
    fd  = sub["is_first_down"].dropna().astype(float)

    return {
        "n":               int(len(sub)),
        "avg_yards":       round(float(yg.mean()),  2) if len(yg) > 0 else None,
        "median_yards":    round(float(yg.median()),2) if len(yg) > 0 else None,
        "first_down_rate": round(float(fd.mean()) * 100, 1) if len(fd) > 0 else None,
        "turnover_rate":   round(float(sub["is_turnover"].mean()) * 100, 2),
        "penalty_rate":    round(float(sub["has_penalty"].mean()) * 100, 2),
        "touchdown_rate":  round(float(sub["is_touchdown"].mean()) * 100, 2),
        "sack_rate":       round(float(sub["is_sack"].mean()) * 100, 2),
    }


@router.get("/scenario")
def get_scenario(
    request: Request,
    down: Optional[int]  = Query(None, ge=1, le=4,  description="Down (1-4)"),
    ytf_min: Optional[int] = Query(None, ge=0,       description="YARDS_TO_FIRST mínimo"),
    ytf_max: Optional[int] = Query(None, ge=0,       description="YARDS_TO_FIRST máximo"),
    ytg_max: Optional[int] = Query(None, ge=0, le=100, description="YARDS_TO_GOAL máximo"),
    score_diff_min: Optional[int] = Query(None, ge=-59, description="score_diff mínimo"),
    score_diff_max: Optional[int] = Query(None, le=59,  description="score_diff máximo"),
    off: Optional[str]   = Query(None,               description="Equipo ofensivo (siglas)"),
    qtr: Optional[int]   = Query(None, ge=1, le=5,   description="Cuarto"),
):
    """
    Filtra jugadas según el escenario situacional solicitado y devuelve
    métricas agregadas desglosadas por play_category, is_shotgun y pass_direction.
    """
    df: pd.DataFrame = request.app.state.df.copy()

    # ── Aplicar filtros ────────────────────────────────────
    if down is not None:
        df = df[df["DOWN"] == down]
    if ytf_min is not None:
        df = df[df["YARDS_TO_FIRST"] >= ytf_min]
    if ytf_max is not None:
        df = df[df["YARDS_TO_FIRST"] <= ytf_max]
    if ytg_max is not None:
        df = df[df["YARDS_TO_GOAL"] <= ytg_max]
    if score_diff_min is not None:
        df = df[df["score_diff"] >= score_diff_min]
    if score_diff_max is not None:
        df = df[df["score_diff"] <= score_diff_max]
    if off is not None:
        df = df[df["OFF"] == off.upper()]
    if qtr is not None:
        df = df[df["QTR"] == qtr]

    total = len(df)

    if total == 0:
        return {"total": 0, "filters_applied": {}, "breakdown": {}}

    # ── Desglose por play_category simplificada ────────────
    def simple(cat):
        c = str(cat)
        if "PASS" in c or "SACK" in c or "INTERCEPTION" in c: return "pase"
        if "RUN"  in c: return "carrera"
        return "otro"

    df = df.copy()
    df["_cat"] = df["play_category"].apply(simple)

    breakdown_category = {}
    for cat_val in ["pase", "carrera", "otro"]:
        sub = df[df["_cat"] == cat_val]
        breakdown_category[cat_val] = _metrics(sub)

    # ── Desglose Shotgun ───────────────────────────────────
    breakdown_shotgun = {
        "shotgun":    _metrics(df[df["is_shotgun"] == True]),
        "no_shotgun": _metrics(df[df["is_shotgun"] == False]),
    }

    # ── Desglose por pass_direction (solo pases con dir conocida) ──
    valid_dirs = ["short_left","short_middle","short_right",
                  "deep_left","deep_middle","deep_right"]
    pass_df = df[df["_cat"] == "pase"]
    breakdown_direction = {}
    for d in valid_dirs:
        sub = pass_df[pass_df["pass_direction"] == d]
        if len(sub) > 0:
            breakdown_direction[d] = _metrics(sub)

    # ── Distribución YARDS_TO_FIRST ────────────────────────
    ytf_hist = df["YARDS_TO_FIRST"].value_counts().sort_index()
    ytf_distribution = {str(k): int(v) for k, v in ytf_hist.head(15).items()}

    return {
        "total":    total,
        "filters_applied": {
            "down": down, "ytf_min": ytf_min, "ytf_max": ytf_max,
            "ytg_max": ytg_max, "score_diff_min": score_diff_min,
            "score_diff_max": score_diff_max, "off": off, "qtr": qtr,
        },
        "overall":            _metrics(df),
        "by_category":        breakdown_category,
        "by_shotgun":         breakdown_shotgun,
        "by_pass_direction":  breakdown_direction,
        "ytf_distribution":   ytf_distribution,
    }
