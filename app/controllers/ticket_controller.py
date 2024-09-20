# app/controllers/ticket_controller.py

import os
from fastapi import APIRouter, HTTPException, File, UploadFile
import shutil
from typing import List

from app.services.ticket_service import TicketService
from app.schemas.ticket_schema import MoveTicketSchema, CreateTicketSchema
from app.schemas.comments_schema import AddCommentSchema

router = APIRouter()

# Ruta del directorio temporal
TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tmp')

# Asegurarse de que el directorio temporal existe
os.makedirs(TEMP_DIR, exist_ok=True)

# Endpoint para mover un ticket de estado
@router.put("/tickets/{ticket_id}")
def move_ticket(ticket_id: int, move_ticket_data: MoveTicketSchema):
    try:
        updated_ticket = TicketService.move_ticket(ticket_id, move_ticket_data.new_state)
        return {"status": "success", "ticket": updated_ticket}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener un ticket
@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    try:
        ticket = TicketService.get_ticket_data(ticket_id)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para crear un ticket
@router.post("/tickets")
def create_ticket(ticket_data: CreateTicketSchema):
    try:
        new_ticket = TicketService.create_ticket(ticket_data.title, ticket_data.description)
        return {"status": "success", "ticket_id": new_ticket["ticket_id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para comentar un ticket
@router.post("/tickets/{ticket_id}/comments")
def add_comment_to_ticket(ticket_id: int, comment_data: AddCommentSchema):
    try:
        comment_result = TicketService.add_comment_to_ticket(ticket_id, comment_data.text)
        return {
            "status": "success", 
            "comment_id": comment_result["comment_id"],
            "comment_text": comment_result["comment_text"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para adjuntar múltiples archivos
@router.post("/tickets/{ticket_id}/attach")
async def attach_files_to_ticket(ticket_id: int, files: List[UploadFile] = File(...), max_files: int = 10):
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
        result = TicketService.attach_files_to_ticket(ticket_id, file_paths, max_files=max_files)
        
        # Retornar el resultado
        return {"status": "success", "attachment_result": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        # Cerrar los archivos temporales
        for file in files:
            file_location = os.path.join(TEMP_DIR, file.filename)
            file.file.close()
            os.remove(file_location)