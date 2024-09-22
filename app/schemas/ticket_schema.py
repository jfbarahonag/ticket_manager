# app/schemas/ticket_schema.py

from pydantic import BaseModel
from typing import Optional
from app.models.ticket_model import TicketState

# Esquema para mover el ticket de estado
class MoveTicketSchema(BaseModel):
    new_state: TicketState
    user_email: Optional[str] = None  # Usuario opcional

# Esquema para crear un nuevo ticket
class CreateTicketSchema(BaseModel):
    title: str
    description: str
