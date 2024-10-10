import requests

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers

class TeamsService:
    @staticmethod
    def get_team_members(team_name: str):
        """
        Obtiene los miembros de un equipo de Azure DevOps.
        """
        # URL para obtener los miembros del equipo
        url = f"{AZURE_ORG_URL}/_apis/projects/{PROJECT_NAME}/teams/{team_name}/members?api-version=7.1"
        # Hacer la solicitud GET para obtener los miembros del equipo
        response = requests.get(url, headers=create_headers())

        if response.status_code == 200:
            # Retornar los miembros del equipo
            data = response.json()
            team_members = data["value"]
            # Extraer los datos importantes de cada miembro
            members_info = [
                {
                    "name": member["identity"]["displayName"],
                    "email": member["identity"]["uniqueName"],
                }
                for member in team_members
            ]
            return {
                "count": data["count"],
                "members": members_info
            }
        else:
            raise ValueError(f"Error al obtener los miembros del equipo: {response.status_code} - {response.content.decode()}")
        
    @staticmethod
    def get_tickets_by_member(team_name: str, user_email: str, state: str):
        """
        Obtiene los tickets asignados a un usuario por su correo electrónico.
        """
        # Filtrar tickets por estado y asignado a usuario
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/{team_name}/_apis/wit/wiql?api-version=7.1"
        query = {
            "query": f"SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] "
                     f"FROM WorkItems "
                     f"WHERE [System.AssignedTo] = '{user_email}' "
                     f"AND [System.State] = '{state}'"
                     f"AND [System.AreaPath] = '{PROJECT_NAME}\\{team_name}'"
        }

        response = requests.post(url, headers=create_headers(content_type="application/json"), json=query)

        if response.status_code == 200:
            work_items = response.json()["workItems"]
            tickets = [{"id": item["id"]} for item in work_items]
            return {
                "member": user_email,
                "count": len(tickets),
                "tickets": tickets    
            }
        else:
            raise ValueError(f"Error al obtener los tickets: {response.status_code} - {response.content.decode()}")
    
    @staticmethod
    def assign_ticket_to_member(team_name: str, user_email: str, ticket_id: int):
        """
        Asigna un ticket a un miembro del equipo por su correo electrónico.
        """
        # URL para actualizar el ticket
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"
        # Datos para actualizar el ticket
        update_data = [
            { "op": "add", "path": "/fields/System.AssignedTo", "value": user_email },
            {"op": "add","path": "/fields/System.AreaPath","value": f"{PROJECT_NAME}\\{team_name}"}
        ]

        response = requests.patch(url, headers=create_headers(), json=update_data)

        if response.status_code == 200:
            return {
                "ticket_id": ticket_id,
                "assigned_to": user_email,
            }
        else:
            raise ValueError(f"Error al asignar el ticket: {response.status_code} - {response.content.decode()}")