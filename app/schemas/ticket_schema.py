# app/schemas/ticket_schema.py

from pydantic import BaseModel
from app.models.ticket_model import TicketState

# Esquema para mover el ticket de estado
class MoveTicketSchema(BaseModel):
    new_state: TicketState

# Esquema para crear un nuevo ticket
class CreateTicketSchema(BaseModel):
    title: str
    description: str
