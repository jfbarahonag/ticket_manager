# app/controllers/teams_controller.py

from fastapi import APIRouter, HTTPException

from app.services.teams_service import TeamsService

router = APIRouter(prefix="/teams")

# Endpoint para obtener los miembros de un team
@router.get("/{team_name}/members")
def get_ticket(team_name: str):
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
        ## TODO: Change this
        members = TeamsService.get_tickets_by_member(team_name, member_email)
        return {
            "status": "success",
            "data": members,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
