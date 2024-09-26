import requests
from typing import Optional
from typing import Any

from app.models.ticket_model import TicketState
from app.services.comments_service import CommentsService
from app.services.attachments_service import AttachmentsService

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers

def filter_ticket_data(
    ticket_data, 
    comments_data = None, 
    include_comments = False, 
    include_attachments = False
):
    data = {}
    data["relations"] = []
    data["comments"] = []
    
    fields = ticket_data.get("fields", {})
    relations = ticket_data.get("relations", [])
    
    ## DTO
    data["id"] = ticket_data.get("id")
    data["title"] = fields.get("System.Title")
    data["state"] = fields.get("System.State")
    if include_attachments:
        data["relations"] = relations
    if include_comments and comments_data is not None:
        data["comments"] = comments_data
    data["azure"] = fields
    return data.copy()

class TicketService:
    @staticmethod
    def get_ticket_data(ticket_id: int) -> dict[str, Any]:
        # Obtener el estado actual del work item de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?$expand=relations&api-version=7.1"
        response = requests.get(url, headers=create_headers())
        
        if response.status_code == 200:
            data = response.json()
            comments = CommentsService.get_comments_of_a_ticket(ticket_id).get("comments")
            
            return filter_ticket_data(data, comments, True, True)
        else:
            raise ValueError(f"Error al obtener el ticket {ticket_id}: {response.status_code} - {response.content.decode()}")
    
    @staticmethod
    def create_ticket(type:str, payload: Any):
        # Crear un nuevo ticket en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/${type}?api-version=7.1"

        response = requests.patch(url, headers=create_headers(), json=payload)
        ticket_data = response.json()

        if response.status_code in [200, 201]:
            return filter_ticket_data(ticket_data)
        else:
            raise ValueError(f"Error al crear el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def move_ticket(ticket_id: int, new_state: TicketState,  user_email: Optional[str] = None):
        # Validar si el nuevo estado es válido
        valid_transitions = {
            TicketState.borrador: [TicketState.solicitado],
            TicketState.solicitado: [TicketState.asignado],
            TicketState.asignado: [TicketState.en_evaluacion],
            TicketState.en_evaluacion: [TicketState.borrador, TicketState.aprobado, TicketState.rechazado]
        }

        # Obtener el estado actual del ticket
        current_state = TicketService.get_ticket_data(ticket_id)['state']

        if new_state not in valid_transitions.get(current_state, []):
            raise ValueError(f"No se puede mover el ticket de {current_state} a {new_state}")

        # Payload básico para actualizar el estado
        payload = [
            {"op": "add","path": "/fields/System.State","value": new_state.value}
        ]
        
        # Si el nuevo estado es 'Asignado', es obligatorio recibir el 'user email'
        if new_state == 'Asignado':
            if not user_email:
                raise ValueError(f"El usuario es obligatorio cuando el estado es '{new_state}'")
            
            # Agregar al payload la asignación del usuario
            payload.append(
                {"op": "add","path": "/fields/System.AssignedTo","value": user_email
            })

        # Actualizar el estado en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"
        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return filter_ticket_data(response.json())
        else:
            raise ValueError(f"Error al mover el ticket: {response.status_code} - {response.content.decode()}")

    @staticmethod
    def add_comment_to_ticket(ticket_id: int, comment: str):
        CommentsService.add_comment_to_ticket(ticket_id, comment)
        return TicketService.get_ticket_data(ticket_id)

    # Método para adjuntar múltiples archivos a un ticket
    @staticmethod
    def attach_files_to_ticket(ticket_id: int, file_paths: list[str], max_files: int = 10):
        # Validar que no se exceda el número máximo de archivos permitidos
        if len(file_paths) > max_files:
            raise ValueError(f"El número de archivos no puede exceder {max_files}. Archivos recibidos: {len(file_paths)}")

        # Subir cada archivo y adjuntarlo al ticket
        AttachmentsService.attach_files_to_ticket(ticket_id, file_paths)
        return TicketService.get_ticket_data(ticket_id)

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
        AttachmentsService.remove_attachment_from_ticket(ticket_id, attachment_idx)
        return TicketService.get_ticket_data(ticket_id)