# glpi-bot/app.py
"""
Pequeńa API REST que expone:
  • GET  /ping          → health-check (200 OK)
  • POST /ticket        → crea un ticket en GLPI vía REST

Se asume que las variables de entorno:
  GLPI_API_URL, GLPI_APP_TOKEN y GLPI_USER_TOKEN
apuntan al endpoint REST de GLPI, token de aplicación y token de sesión.
"""

import logging
import os
from datetime import datetime

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# ──────────────────────────────────────────────
# Configuración básica de logging
# ──────────────────────────────────────────────
log_file = os.getenv("BOT_LOG_FILE", "/app/logs/glpi-bot.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# ──────────────────────────────────────────────
# FastAPI
# ──────────────────────────────────────────────
api = FastAPI(title="GLPI Bot", version="1.0")


class TicketIn(BaseModel):
    titulo: str
    descripcion: str
    entidad_id: int | None = None  # Opcional: asignar a entidad


def _get_headers() -> dict:
    """Cabeceras requeridas por la API de GLPI"""
    return {
        "Content-Type": "application/json",
        "App-Token": os.getenv("GLPI_APP_TOKEN", ""),
        "Session-Token": os.getenv("GLPI_USER_TOKEN", ""),
    }


@api.get("/ping")
def ping() -> dict:
    """Endpoint de salud"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@api.post("/ticket")
def crear_ticket(payload: TicketIn) -> dict:
    """Crea un ticket sencillo en GLPI"""
    url_base = os.getenv("GLPI_API_URL")
    if not url_base:
        raise HTTPException(status_code=500, detail="GLPI_API_URL no configurada")

    endpoint = f"{url_base.rstrip('/')}/Ticket"

    data = {
        "input": {
            "name": payload.titulo,
            "content": payload.descripcion,
            **({"entities_id": payload.entidad_id} if payload.entidad_id else {}),
            "status": 1,
        }
    }

    try:
        r = requests.post(endpoint, json=data, headers=_get_headers(), timeout=15)
        r.raise_for_status()
        ticket_id = r.json().get("id")
        logging.info("Ticket creado: %s", ticket_id)
        return {"ticket_id": ticket_id}
    except requests.RequestException as exc:
        logging.exception("Error al crear ticket: %s", exc)
        raise HTTPException(status_code=502, detail="Error al comunicarse con GLPI")
