# app/controllers/reversals_controller.py

import os
from fastapi import APIRouter, HTTPException, File, UploadFile
import shutil
from typing import List

from app.services.reversals_service import ReversalsService
from app.schemas.reversal_schema import CreateReversalSchema, MoveReversalSchema
from app.schemas.comments_schema import AddCommentSchema

router = APIRouter(prefix="/reversals")

# Ruta del directorio temporal
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp')

# Asegurarse de que el directorio temporal existe
os.makedirs(TEMP_DIR, exist_ok=True)

# Endpoint para crear un ticket
@router.post("")
def create(reversal_data: CreateReversalSchema):
    try:
        new_reversal = ReversalsService.create(reversal_data)
        return {"status": "success", "data": new_reversal}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener un ticket
@router.get("/{reversal_id}")
def get_ticket(reversal_id: int):
    try:
        ticket = ReversalsService.get(reversal_id)
        return {
            "status": "success",
            "data": ticket,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para mover un ticket de estado
@router.put("/{reversal_id}")
def move_ticket(reversal_id: int, move_ticket_data: MoveReversalSchema):
    try:
        # Obtener el nuevo estado y el user email opcional
        new_state = move_ticket_data.new_state
        user_email = move_ticket_data.user_email
        
        # Validar que el user email sea obligatorio si el estado es "Asignado"
        if (new_state == "Asignado") and not user_email:
            raise HTTPException(status_code=400, detail=f"El correo del usuario (user_email) es obligatorio cuando el estado es '{new_state}'")
        
        updated_ticket = ReversalsService.move(reversal_id, new_state, user_email)
        return {
            "status": "success", 
            "data": updated_ticket
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para comentar un ticket
@router.post("/{reversal_id}/comments")
def add_comment_to_ticket(reversal_id: int, comment_data: AddCommentSchema):
    try:
        result = ReversalsService.add_comment(reversal_id, comment_data.text, comment_data.user_email)
        return {
            "status": "success", 
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para adjuntar múltiples archivos
@router.post("/{reversal_id}/attachments")
async def attach_files_to_ticket(reversal_id: int, files: List[UploadFile] = File(...), max_files: int = 10):
    try:
        # Validar el número de archivos
        if len(files) > max_files:
            raise HTTPException(status_code=400, detail=f"El número de archivos no puede exceder {max_files}")

        # Guardar los archivos temporalmente en el servidor
        file_paths = []
        
        # Iterar sobre los archivos recibidos y guardarlos temporalmente
        for file in files:
            # Crear la ruta completa del archivo en el directorio temporal
            file_location = os.path.join(TEMP_DIR, file.filename)

            # Guardar el archivo en la ruta temporal
            with open(file_location, "wb") as f:
                shutil.copyfileobj(file.file, f)

            # Agregar la ruta del archivo a la lista
            file_paths.append(file_location)
        
        # Adjuntar los archivos al ticket
        result = ReversalsService.attach_files(reversal_id, file_paths, max_files=max_files)
        
        # Retornar el resultado
        return {
            "status": "success", 
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Cerrar los archivos temporales
        for file in files:
            file_location = os.path.join(TEMP_DIR, file.filename)
            file.file.close()
            os.remove(file_location)
