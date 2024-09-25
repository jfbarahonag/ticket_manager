# app/schemas/reversal_schema.py

from pydantic import BaseModel
from app.models.common_model import Client, Advisor
from app.models.reversal_model import ReversalData

# Esquema para crear una nueva reversion
class CreateReversalSchema(BaseModel):
    client: Client
    advisor: Advisor
    data: ReversalData
