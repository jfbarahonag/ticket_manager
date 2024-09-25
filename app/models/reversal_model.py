# app/models/reversal_model.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional

# Estados posibles de un ticket
class ReversalType(str, Enum):
    porErroresOperativos = "Reversion por errores operativos"
    porErroresCliente = "Reversion por errores del cliente"

class ReversalByOperational(BaseModel):
    errors: str
    correctiveActions: str

class ReversalByClient(BaseModel):
    dateOfIncorrectPayment: str

class ReversalData(BaseModel):
    type: ReversalType
    byOperational: Optional[ReversalByOperational] = None
    byClient: Optional[ReversalByClient] = None
    