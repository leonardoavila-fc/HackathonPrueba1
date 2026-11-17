"""API mínima de la plantilla. Ejecuta: .venv/bin/uvicorn backend.main:app --reload"""
from fastapi import FastAPI

app = FastAPI(title="Hackathon NFL UNAM")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
