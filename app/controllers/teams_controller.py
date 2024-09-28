# app/controllers/teams_controller.py

from fastapi import APIRouter, HTTPException

from app.services.teams_service import TeamsService

router = APIRouter(prefix="/teams")

# Endpoint para obtener un ticket
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
