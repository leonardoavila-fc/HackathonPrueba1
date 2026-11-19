"""
main.py — Backend FastAPI para NFL Coach Analytics
Cargar: uv run uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

from routers import scenarios, comparatives, coach

# ── Configuración ──────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "..", "data", "nfl_clean.parquet")

app = FastAPI(
    title="NFL Coach Analytics API",
    description="Análisis táctico play-by-play NFL 2002-2012",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Carga del dataset en memoria al arrancar ───────────────
@app.on_event("startup")
async def load_data():
    raw = pd.read_parquet(DATA_PATH)
    # Limpiar score_diff corrupto
    app.state.df = raw[raw["score_diff"].between(-59, 59)].copy()
    n = len(app.state.df)
    teams = sorted(app.state.df["OFF"].dropna().unique().tolist())
    app.state.teams = teams
    print(f"✅ Dataset cargado: {n:,} jugadas | {len(teams)} equipos")

# ── Registrar routers ──────────────────────────────────────
app.include_router(scenarios.router,    prefix="/api")
app.include_router(comparatives.router, prefix="/api")
app.include_router(coach.router,        prefix="/api")

@app.get("/")
def root():
    return {
        "status": "ok",
        "docs": "/docs",
        "endpoints": ["/api/scenario", "/api/comparatives", "/api/coach-advice", "/api/teams"]
    }

@app.get("/api/teams")
def get_teams():
    return {"teams": app.state.teams}
