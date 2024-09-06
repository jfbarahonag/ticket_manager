# app/controllers/ticket_controller.py

from fastapi import APIRouter, HTTPException
from app.services.ticket_service import TicketService
from app.schemas.ticket_schema import MoveTicketSchema, CreateTicketSchema

router = APIRouter()

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

@router.post("/tickets")
def create_ticket(ticket_data: CreateTicketSchema):
    try:
        new_ticket = TicketService.create_ticket(ticket_data.title, ticket_data.description)
        return {"status": "success", "ticket_id": new_ticket["ticket_id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
