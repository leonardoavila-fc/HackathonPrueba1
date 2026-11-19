"""
routers/coach.py — Endpoint /api/coach-advice impulsado por strands-agents
POST /api/coach-advice
"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os, json

router = APIRouter()


# ── Schema de entrada ──────────────────────────────────────
class ScenarioInput(BaseModel):
    down: int               = Field(..., ge=1, le=4,   description="Down actual (1-4)")
    yards_to_first: int     = Field(..., ge=0, le=70,  description="Yardas para 1er down")
    yards_to_goal: int      = Field(..., ge=0, le=100, description="Yardas para anotación")
    score_diff: int         = Field(..., ge=-59, le=59,description="OFF_SCORE - DEF_SCORE")
    qtr: int                = Field(..., ge=1, le=5,   description="Cuarto")
    off_team: Optional[str] = Field(None,              description="Equipo ofensivo (siglas)")
    # Métricas calculadas del escenario actual (del endpoint /api/scenario)
    avg_yards_pass:    Optional[float] = None
    avg_yards_run:     Optional[float] = None
    fd_rate_shotgun:   Optional[float] = None
    fd_rate_no_shotgun:Optional[float] = None
    best_pass_zone:    Optional[str]   = None
    no_huddle_delta:   Optional[float] = None


# ── Función de consejo sin strands (fallback analítico) ───
def rule_based_advice(s: ScenarioInput) -> str:
    """Genera consejo táctico basado en reglas derivadas de los datos."""
    lines = []
    team = s.off_team or "tu equipo"

    # Situación base
    if s.score_diff < -8:
        lines.append(f"**{team}** va perdiendo por más de una posesión. El modo urgente es necesario.")
    elif s.score_diff > 8:
        lines.append(f"**{team}** maneja ventaja cómoda. El control del balón es prioritario.")
    else:
        lines.append(f"Partido cerrado ({'+' if s.score_diff>=0 else ''}{s.score_diff} pts). Cada posesión cuenta.")

    # Down y distancia
    if s.down == 3 and s.yards_to_first >= 7:
        lines.append(
            f"3er down largo ({s.yards_to_first} yds): los datos sugieren **Shotgun + Pase**. "
            f"La tasa de conversión en 7+ yds con Shotgun+Pase es del 39%."
        )
        if s.best_pass_zone:
            zone_label = s.best_pass_zone.replace("_"," ").title()
            lines.append(f"Zona de pase recomendada por datos: **{zone_label}**.")
    elif s.down == 3 and s.yards_to_first <= 2:
        lines.append(
            f"3er down corto ({s.yards_to_first} yds): considera **carrera sin Shotgun**. "
            f"Históricamente convierte al 52.8% en distancias de 1-2 yds."
        )
    elif s.down == 1:
        if s.yards_to_first == 10:
            run_better = (s.avg_yards_run or 0) >= (s.avg_yards_pass or 0)
            rec = "carrera" if run_better else "pase"
            lines.append(
                f"1er down y 10: las métricas de este escenario favorecen el **{rec}** "
                f"(carrera: {s.avg_yards_run or 'N/A'} yds/jug · pase: {s.avg_yards_pass or 'N/A'} yds/jug)."
            )
    elif s.down == 4:
        lines.append(f"4to down: decisión crítica. Yardas restantes para anotación: {s.yards_to_goal}.")

    # No Huddle en Q4 cerrado
    if s.qtr == 4 and abs(s.score_diff) <= 8:
        if s.no_huddle_delta and s.no_huddle_delta > 0:
            lines.append(
                f"En Q4 con partido cerrado, el **No Huddle** genera +{s.no_huddle_delta} yds/jugada "
                f"adicionales según los datos históricos."
            )

    # Red zone
    if s.yards_to_goal <= 10:
        lines.append(
            "**Red Zone (< 10 yds):** el pase al centro (short_middle) tiene la mayor tasa de TD "
            "en estas situaciones. Considera también QB sneak en down corto."
        )

    return " ".join(f"- {l}" for l in lines) if lines else "Sin datos suficientes para esta situación."


# ── Función con strands-agents ─────────────────────────────
def strands_advice(s: ScenarioInput, rule_advice: str) -> str:
    """Llama a strands-agents con Bedrock. Si falla, retorna el consejo por reglas."""
    try:
        from strands import Agent
        from strands.models import BedrockModel

        model = BedrockModel(
            model_id="us.amazon.nova-lite-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        agent = Agent(model=model)

        situation = (
            f"Down: {s.down}, Yardas para 1er down: {s.yards_to_first}, "
            f"Yardas para anotación: {s.yards_to_goal}, "
            f"Marcador (ofensiva - defensiva): {s.score_diff:+d}, "
            f"Cuarto: {s.qtr}"
        )
        prompt = (
            f"Eres un coordinador ofensivo de la NFL. La situación es: {situation}. "
            f"Basándote en este análisis estadístico previo: {rule_advice} "
            f"Da UNA recomendación táctica concisa (máximo 3 líneas) para la siguiente jugada."
        )
        result = agent(prompt)
        return str(result).strip()

    except Exception as e:
        # Si Bedrock no está configurado, retornar consejo analítico
        return rule_advice


# ── Endpoint ───────────────────────────────────────────────
@router.post("/coach-advice")
def coach_advice(payload: ScenarioInput):
    """
    Recibe las métricas del escenario actual y genera una recomendación táctica
    usando strands-agents (Bedrock) con fallback a reglas analíticas.
    """
    rule_advice = rule_based_advice(payload)
    advice = strands_advice(payload, rule_advice)

    return {
        "advice": advice,
        "rule_based_advice": rule_advice,
        "source": "strands-agents" if advice != rule_advice else "rule-based",
        "scenario": {
            "down":           payload.down,
            "yards_to_first": payload.yards_to_first,
            "yards_to_goal":  payload.yards_to_goal,
            "score_diff":     payload.score_diff,
            "qtr":            payload.qtr,
        },
    }
