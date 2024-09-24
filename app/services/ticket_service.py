import os
import requests
from typing import Optional
from typing import Any

from app.models.ticket_model import TicketState
from app.services.comments_service import CommentsService
from app.services.attachments_service import AttachmentsService

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers

def get_ticket_object(ticket_object: dict[str, Any]):
    return {
        "id": ticket_object["id"],
        "url": ticket_object["url"],
        "state": ticket_object["fields"]["System.State"],
        "title": ticket_object["fields"]["System.Title"],
        "description": ticket_object["fields"]["System.Description"],
        "iterations": ticket_object["fields"]["Custom.Iteraciones"],
    }

class TicketService:
    @staticmethod
    def move_ticket(ticket_id: int, new_state: TicketState,  user_email: Optional[str] = None):
        # Validar si el nuevo estado es válido
        valid_transitions = {
            TicketState.borrador: [TicketState.solicitado],
            TicketState.solicitado: [TicketState.asignado],
            TicketState.asignado: [TicketState.en_evaluacion],
            TicketState.en_evaluacion: [TicketState.devuelto, TicketState.aprobado, TicketState.rechazado],
            TicketState.devuelto: [TicketState.borrador, TicketState.solicitado],
        }

        # Obtener el estado actual del ticket
        current_state = TicketService.get_ticket_data(ticket_id)['estado']

        if new_state not in valid_transitions.get(current_state, []):
            raise ValueError(f"No se puede mover el ticket de {current_state} a {new_state}")

        # Payload básico para actualizar el estado
        payload = [
            {
                "op": "add",
                "path": "/fields/System.State",
                "value": new_state.value
            }
        ]
        
        # Si el nuevo estado es 'Asignado', es obligatorio recibir el 'user email'
        if new_state == 'Solicitado' or new_state == 'Asignado':
            if not user_email:
                raise ValueError(f"El usuario es obligatorio cuando el estado es '{new_state}'")
            
            # Agregar al payload la asignación del usuario
            payload.append({
                "op": "add",
                "path": "/fields/System.AssignedTo",
                "value": user_email
            })

        # Actualizar el estado en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"
        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return get_ticket_object(response.json())
        else:
            raise ValueError(f"Error al mover el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def get_ticket_data(ticket_id: int) -> TicketState:
        # Obtener el estado actual del work item de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?$expand=relations&api-version=7.1"
        url_comments = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}/comments?$api-version=7.1-preview.4"
        
        response = requests.get(url, headers=create_headers())
        response_comments = requests.get(url_comments, headers=create_headers())
        
        if response.status_code == 200 and response_comments.status_code == 200:
            data = {}
            fields = response.json().get("fields", {})
            relations = response.json().get("relations", {})
            comments = CommentsService.get_comments_of_a_ticket(ticket_id).get("comments")
            
            ## DTO
            data["titulo"] = fields.get("System.Title")
            data["estado"] = fields.get("System.State")
            data["ultimoSolicitado"] = fields.get("Custom.Solicitadoen")
            data["ultimoAsignado"] = fields.get("Custom.Asignado")
            data["ultimoDevolucion"] = fields.get("Custom.Ultimadevolucion")
            data["ultimoInicioEvaluacion"] = fields.get("Custom.Inicioevaluacion")
            data["finEvaluacion"] = fields.get("Custom.Finevaluacion")
            data["iteraciones"] = fields.get("Custom.Iteraciones")
            data["relaciones"] = relations
            data["comentarios"] = comments
            return data
        else:
            raise ValueError(f"Error al obtener el ticket {ticket_id}: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def create_ticket(title: str, description: str):
        # Crear un nuevo ticket en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/$Ticket?api-version=7.1"
        payload = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
        ]

        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return get_ticket_object(response.json())
        else:
            raise ValueError(f"Error al crear el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def add_comment_to_ticket(ticket_id: int, comment: str):
        return CommentsService.add_comment_to_ticket(ticket_id, comment)

    # Método para adjuntar múltiples archivos a un ticket
    @staticmethod
    def attach_files_to_ticket(ticket_id: int, file_paths: list[str], max_files: int = 10):
        # Validar que no se exceda el número máximo de archivos permitidos
        if len(file_paths) > max_files:
            raise ValueError(f"El número de archivos no puede exceder {max_files}. Archivos recibidos: {len(file_paths)}")

        # Subir cada archivo y adjuntarlo al ticket
        return AttachmentsService.attach_files_to_ticket(ticket_id, file_paths)

    @staticmethod
    def find_attachment_relation_index(ticket_id: int, attachment_url: str) -> int:
        """
        Buscar la posición de la relación (adjunto) en el Work Item para eliminarla.
        """
        # Obtener los datos actuales del ticket para buscar el adjunto
        ticket_data = TicketService.get_ticket_data(ticket_id)

        # Iterar sobre las relaciones del ticket y encontrar el índice del archivo adjunto
        relations = ticket_data.get("relaciones", [])
        for index, relation in enumerate(relations):
            if relation.get("url") == attachment_url and relation.get("rel") == "AttachedFile":
                return index
        
        raise ValueError(f"El archivo adjunto con la URL {attachment_url} no fue encontrado en el ticket {ticket_id}")

    @staticmethod
    def remove_attachment_from_ticket(ticket_id: int, attachment_url: str):
        attachment_idx = TicketService.find_attachment_relation_index(ticket_id, attachment_url)
        response = AttachmentsService.remove_attachment_from_ticket(ticket_id, attachment_idx)
        response["attachment_url"] = attachment_url
        return response