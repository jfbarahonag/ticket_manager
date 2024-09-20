import os
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
def create_headers(
        username: str = PAT_TOKEN, 
        password: str = None,
        content_type: str = "application/json-patch+json"
    ):
    return {
        "Content-Type": content_type,
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
        current_state = TicketService.get_ticket_data(ticket_id)['estado']

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
    def get_ticket_data(ticket_id: int) -> TicketState:
        # Obtener el estado actual del work item de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"
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
            data["iteraciones"] = fields.get("Custom.Iteraciones")
            return data
        else:
            raise ValueError(f"Error al obtener el ticket {ticket_id}: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def create_ticket(title: str, description: str):
        # Crear un nuevo ticket en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/$Ticket?api-version=7.0"
        payload = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
        ]

        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return {"status": "success", "ticket_id": response.json()["id"]}
        else:
            raise ValueError(f"Error al crear el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def add_comment_to_ticket(ticket_id: int, comment: str):
        # Agregar un comentario a un ticket de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workItems/{ticket_id}/comments?api-version=7.0-preview.3"
        payload = {
            "text": comment
        }

        response = requests.post(url, headers=create_headers(content_type="application/json"), json=payload)

        if response.status_code in [200, 201]:
            return {
                "status": "success", 
                "comment_id": response.json()["id"],
                "comment_text": payload["text"]
            }
        else:
            raise ValueError(f"Error al agregar comentario al ticket {ticket_id}: {response.status_code} - {response.content.decode()}")
        
    @staticmethod
    def upload_attachment(file_path: str):
        
        # Extraer el nombre del archivo de manera compatible con Linux y Windows
        file_name = os.path.basename(file_path)

        # Construir la URL usando el nombre del archivo extraído
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/attachments?fileName={file_name}&api-version=7.1"
        
        print(url)
        
        with open(file_path, 'rb') as file:
            response = requests.post(url, headers=create_headers(content_type="application/octet-stream"), data=file)

            if response.status_code in [200, 201]:
                return response.json()["url"]
            else:
                raise ValueError(f"Error al subir el archivo: {response.status_code} - {response.content.decode()}")

    # Método para adjuntar múltiples archivos a un ticket
    @staticmethod
    def attach_files_to_ticket(ticket_id: int, file_paths: list[str], max_files: int = 10):
        # Validar que no se exceda el número máximo de archivos permitidos
        if len(file_paths) > max_files:
            raise ValueError(f"El número de archivos no puede exceder {max_files}. Archivos recibidos: {len(file_paths)}")

        # Subir cada archivo y adjuntarlo al ticket
        relations = []
        for file_path in file_paths:
            print(file_path)
            attachment_url = TicketService.upload_attachment(file_path)
            print(attachment_url, os.path.basename(file_path).split('/')[-1])
            relations.append({
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "AttachedFile",
                    "url": attachment_url,
                    "attributes": {
                        "comment": f"Archivo adjunto: {os.path.basename(file_path).split('/')[-1]}"
                    }
                }
            })
            
            print(relations)

        # Enviar la solicitud para adjuntar los archivos al ticket
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"
        response = requests.patch(url, headers=create_headers(), json=relations)
        if response.status_code in [200, 201]:
            data = response.json()
            return {
                "attachments": [
                    {
                        "url": r["url"], 
                        "comment": r["attributes"]["comment"], 
                        "name": r["attributes"]["name"]
                    } 
                    for r in data["relations"]
                ],
            }
        else:
            raise ValueError(f"Error al adjuntar archivos al ticket {ticket_id}: {response.status_code} - {response.content.decode()}")