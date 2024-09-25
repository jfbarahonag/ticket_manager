# app/controllers/reversals_controller.py

import os
from fastapi import APIRouter, HTTPException, File, UploadFile
import shutil
from typing import List

from app.services.reversals_service import ReversalsService
from app.schemas.reversal_schema import CreateReversalSchema

router = APIRouter(prefix="/reversals")

# Ruta del directorio temporal
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp')

# Asegurarse de que el directorio temporal existe
os.makedirs(TEMP_DIR, exist_ok=True)

# Endpoint para crear un ticket
@router.post("/")
def create(reversal_data: CreateReversalSchema):
    try:
        new_reversal = ReversalsService.create(reversal_data)
        return {"status": "success", "data": new_reversal}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
