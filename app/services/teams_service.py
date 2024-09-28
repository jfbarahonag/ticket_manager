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