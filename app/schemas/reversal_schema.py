# app/schemas/reversal_schema.py

from pydantic import BaseModel
from typing import Optional

from app.models.common_model import Client, Advisor
from app.models.reversal_model import ReversalData
from app.schemas.ticket_schema import MoveTicketSchema

# Esquema para mover la reversion de estado
class MoveReversalSchema(MoveTicketSchema):
    pass


# Esquema para crear una nueva reversion
class CreateReversalSchema(BaseModel):
    client: Client
    advisor: Advisor
    data: Optional[ReversalData] = {}
