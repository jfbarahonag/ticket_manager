# app/models/ticket_model.py

from enum import Enum
from pydantic import BaseModel

# Estados posibles de un ticket
class TicketState(str, Enum):
    borrador = "Borrador"
    solicitado = "Solicitado"
    asignado = "Asignado"
    en_evaluacion = "En evaluacion"
    aprobado = "Aprobado"
    rechazado = "Rechazado"

# Modelo de ticket
class Ticket(BaseModel):
    id: int
    title: str
    description: str
    state: TicketState
