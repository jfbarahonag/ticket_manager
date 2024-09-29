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
        print(create_headers())
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
    def get_tickets_by_member(team_name: str, user_email: str):
        """
        Obtiene los tickets asignados a un usuario por su correo electrónico.
        """
        # Filtrar tickets por estado y asignado a usuario
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/{team_name}/_apis/wit/wiql?api-version=7.1"
        query = {
            "query": f"SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] "
                     f"FROM WorkItems "
                     f"WHERE [System.AssignedTo] = '{user_email}' "
                     f"AND [System.State] = 'En evaluacion'"
                     f"AND [System.AreaPath] = '{PROJECT_NAME}\\{team_name}'"
        }

        response = requests.post(url, headers=create_headers(content_type="application/json"), json=query)

        if response.status_code == 200:
            work_items = response.json()["workItems"]
            tickets = [{"id": item["id"]} for item in work_items]
            return {
                "count": len(tickets),
                "tickets": tickets    
            }
        else:
            raise ValueError(f"Error al obtener los tickets: {response.status_code} - {response.content.decode()}")