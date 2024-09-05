# app/schemas/ticket_schema.py

from pydantic import BaseModel
from app.models.ticket_model import TicketState

# Esquema para mover el ticket de estado
class MoveTicketSchema(BaseModel):
    new_state: TicketState
