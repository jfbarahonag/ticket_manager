import base64
import requests
from app.models.ticket_model import TicketState

# URL base de Azure DevOps (ajústalo a tu organización y proyecto)
AZURE_ORG_URL = ""
PROJECT_NAME = ""
PAT_TOKEN = ""  # Tu token de acceso personal (PAT)

def get_auth_header(username: str, password: str|None = None):
    # Concatenar el usuario y la contraseña y codificar en base64
    auth_string = f"{username}:{password}"
    auth_bytes = auth_string.encode('ascii')
    auth_base64 = base64.b64encode(auth_bytes).decode('ascii')
    return f"Basic {auth_base64}"

# Headers de autenticación genérica
def create_headers(username: str = PAT_TOKEN, password: str = None):
    return {
        "Content-Type": "application/json-patch+json",
        "Authorization": get_auth_header(username, password)
    }

class TicketService:
    @staticmethod
    def move_ticket(ticket_id: int, new_state: TicketState):
        # Validar si el nuevo estado es válido
        valid_transitions = {
            TicketState.solicitado: [TicketState.asignado],
            TicketState.devuelto: [TicketState.solicitado],
            TicketState.asignado: [TicketState.en_evaluacion],
            TicketState.en_evaluacion: [TicketState.devuelto, TicketState.aprobado, TicketState.rechazado],
        }

        # Obtener el estado actual del ticket
        current_state = TicketService.get_ticket_state(ticket_id)

        if new_state not in valid_transitions.get(current_state, []):
            raise ValueError(f"No se puede mover el ticket de {current_state} a {new_state}")

        # Actualizar el estado en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.0"
        payload = [
            {
                "op": "add",
                "path": "/fields/System.State",
                "value": new_state.value
            }
        ]

        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return {"status": "success", "ticket_id": ticket_id, "new_state": new_state.value}
        else:
            raise ValueError(f"Error al mover el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def get_ticket_state(ticket_id: int) -> TicketState:
        # Obtener el estado actual del work item de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.0"
        response = requests.get(url, headers=create_headers())

        if response.status_code == 200:
            fields = response.json().get("fields", {})
            state = fields.get("System.State")
            return TicketState(state)
        else:
            raise ValueError(f"Error al obtener el ticket {ticket_id}: {response.status_code} - {response.content.decode()}")
    
    @staticmethod
    def get_ticket_data(ticket_id: int) -> TicketState:
        # Obtener el estado actual del work item de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.0"
        response = requests.get(url, headers=create_headers())
        
        if response.status_code == 200:
            data = {}
            fields = response.json().get("fields", {})
            data["titulo"] = fields.get("System.Title")
            data["estado"] = fields.get("System.State")
            data["ultimoSolicitado"] = fields.get("Custom.Solicitadoen")
            data["ultimoAsignado"] = fields.get("Custom.Asignado")
            data["ultimoDevolucion"] = fields.get("Custom.Ultimadevolucion")
            data["ultimoInicioEvaluacion"] = fields.get("Custom.Inicioevaluacion")
            data["finEvaluacion"] = fields.get("Custom.Finevaluacion")
            return data
        else:
            raise ValueError(f"Error al obtener el ticket {ticket_id}: {response.status_code} - {response.content.decode()}")
