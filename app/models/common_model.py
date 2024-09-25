# app/models/common_model.py

from enum import Enum
from pydantic import BaseModel
from typing import Optional

class UserDocumentType(str, Enum):
    CC = "CC"
    PASAPORTE = "PASAPORTE"

# Modelo del cliente
class Client(BaseModel):
    companyName: str
    NIT: str
    obligationNumber: str
    username: str
    userDocumentType: UserDocumentType
    userDocumentNumber: str
    userEmail: str
    phone: Optional[str]

class Advisor(BaseModel):
    email: str