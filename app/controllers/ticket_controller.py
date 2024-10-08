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
        # Obtener el nuevo estado y el user email opcional
        new_state = move_ticket_data.new_state
        user_email = move_ticket_data.user_email
        
        # Validar que el user email sea obligatorio si el estado es "Asignado"
        if (new_state == "Asignado") and not user_email:
            raise HTTPException(status_code=400, detail=f"El correo del usuario (user_email) es obligatorio cuando el estado es '{new_state}'")
        
        updated_ticket = TicketService.move_ticket(ticket_id, new_state, user_email)
        return {
            "status": "success", 
            "ticket": updated_ticket
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener un ticket
@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):
    try:
        ticket = TicketService.get_ticket_data(ticket_id)
        return {
            "status": "success",
            "data": ticket,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para crear un ticket
@router.post("/tickets")
def create_ticket(ticket_data: CreateTicketSchema):
    try:
        new_ticket = TicketService.create_ticket(ticket_data.title, ticket_data.description)
        return {"status": "success", "data": new_ticket}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para comentar un ticket
@router.post("/tickets/{ticket_id}/comments")
def add_comment_to_ticket(ticket_id: int, comment_data: AddCommentSchema):
    try:
        result = TicketService.add_comment_to_ticket(ticket_id, comment_data.text)
        return {
            "status": "success", 
            "data": result
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

# Endpoint que permite eliminar un archivo adjunto de un ticket
@router.delete("/tickets/{ticket_id}/attachments")
def remove_attachment_from_ticket(ticket_id: int, attachmentUrl: str):
    try:
        # Llamar al servicio para eliminar el archivo adjunto
        result = TicketService.remove_attachment_from_ticket(ticket_id, attachmentUrl)
        return {
            "status": "success", 
            "data": result
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
