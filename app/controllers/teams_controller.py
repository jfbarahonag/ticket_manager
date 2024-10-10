# app/controllers/teams_controller.py

from fastapi import APIRouter, HTTPException

from app.services.teams_service import TeamsService

router = APIRouter(prefix="/teams")

# Endpoint para obtener los miembros de un team
@router.get("/{team_name}/members")
def get_members(team_name: str):
    try:
        members = TeamsService.get_team_members(team_name)
        return {
            "status": "success",
            "data": members,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener los tickets asignados de un miembro de un team
@router.get("/{team_name}/members/{member_email}/assigned")
def get_tickets_by_email(team_name: str, member_email: str):
    try:
        members = TeamsService.get_tickets_by_member(team_name, member_email, 'En evaluacion')
        return {
            "status": "success",
            "data": members,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para obtener los tickets asignados de todos los miembros de un team
@router.get("/{team_name}/members/assigned")
def get_tickets_by_email(team_name: str):
    try:
        members_data = TeamsService.get_team_members(team_name)
        count = members_data.get("count", 0)
        
        # No members found
        if count < 1:
            return {
                "status": "success",
                "data": "No members found",
            }
        
        members = members_data.get("members", [])
        
        data = []
        for member in members:
            tickets_data = TeamsService.get_tickets_by_member(team_name, member.get("email"), 'En evaluacion')
            data.append(tickets_data)
            
        return {
            "status": "success",
            "data": data,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint para asignar un ticket a un miembro de un team
@router.put("/{team_name}/members/{member_email}/assign/{ticket_id}")
def assign_ticket(team_name: str, member_email: str, ticket_id: int):
    try:
        data = TeamsService.assign_ticket_to_member(team_name, member_email, ticket_id)
        return {
            "status": "success",
            "data": data,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))