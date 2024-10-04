from typing import Any, Optional
from random import randint

from app.schemas.reversal_schema import CreateReversalSchema
from app.models.reversal_model import ReversalType, ReversalData
from app.models.ticket_model import TicketState

from app.services.ticket_service import TicketService

def reversal_data_to_payload(data: ReversalData|None):
    if data is None: return
    
    payload = [
        {"op": "add", "path": "/fields/Custom.Tipodereversion", "value": data.type}
    ]
    if data.type == ReversalType.porErroresOperativos:
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Errores", "value": data.byOperational.errors},
            {"op": "add", "path": "/fields/Custom.Medidascorrectivas", "value": data.byOperational.correctiveActions},
        ])
    elif data.type == ReversalType.porErroresCliente:
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Fechadelpagoerroneo", "value": data.byClient.dateOfIncorrectPayment},
        ])
    return payload

def create_payload(data: CreateReversalSchema, draft:bool = False):
    
    title = f"RR-{data.client.NIT}-{data.client.obligationNumber}-{''.join([chr(randint(ord('a'), ord('z'))) for _ in range(3)]).upper()}"
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/Custom.Razonsocial", "value": data.client.companyName},
        {"op": "add", "path": "/fields/Custom.NIT", "value": data.client.NIT},
        {"op": "add", "path": "/fields/Custom.Nombredeusuario", "value": data.client.username},
        {"op": "add", "path": "/fields/Custom.Tipodedocumento", "value": data.client.userDocumentType},
        {"op": "add", "path": "/fields/Custom.Numerodedocumento", "value": data.client.userDocumentNumber},
        {"op": "add", "path": "/fields/Custom.Correoelectronico", "value": data.client.userEmail},
        {"op": "add", "path": "/fields/Custom.Celular", "value": data.client.phone if data.client.phone else ""},
        {"op": "add", "path": "/fields/Custom.Numerodeobligacion", "value": data.client.obligationNumber},
        {"op": "add", "path": "/fields/Custom.Solicitadopor", "value": data.advisor.email},
    ]
    if draft is not False:
        payload.append(
            {"op": "add", "path": "/fields/Custom.Tipodereversion", "value": data.data.type},
        )
    
    if draft is not False and data.data.type == ReversalType.porErroresOperativos:
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Errores", "value": data.data.byOperational.errors},
            {"op": "add", "path": "/fields/Custom.Medidascorrectivas", "value": data.data.byOperational.correctiveActions},
        ])
    elif draft is not False and data.data.type == ReversalType.porErroresCliente:
        ##TODO: Validar si la fecha es mayor a 30 dias debe pedir VoBo R
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Fechadelpagoerroneo", "value": data.data.byClient.dateOfIncorrectPayment},
        ])
    
    return payload

def feed_ticket_data(data: dict[str, Any]):
    azure_data = data.get("azure", {})
            
    data["iterations"] = azure_data.get("Custom.Devoluciones")
    data["lastTimeInDraft"] = azure_data.get("Custom.Ultimavezenborrador", "")
    data["lastTimeRequested"] = azure_data.get("Custom.Ultimavezsolicitado", "")
    data["lastTimeAssigned"] = azure_data.get("Custom.Ultimavezasignado", "")
    data["lastTimeInEvaluation"] = azure_data.get("Custom.Ultimavezenevaluacion", "")
    data["lastTimeReturned"] = azure_data.get("Custom.Ultimavezquehubodevolucion", "")
    data["timeFinishEvaluation"] = azure_data.get("Custom.Findeevaluacion", "")          
    
    # remove azure metadata
    data.pop("azure")
    
    return data

class ReversalsService:
    @staticmethod
    def get(reversal_id: int):
        try:
            reversal_data = TicketService.get_ticket_data(reversal_id)
            return feed_ticket_data(reversal_data)
        except Exception as e:
            raise ValueError(f"Error al obtener la reversion: {e}")
    
    @staticmethod
    def create(data: CreateReversalSchema):
        try:
            payload = create_payload(data)
            ticket_data = TicketService.create_ticket("Reversion", payload)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al crear la reversion: {e}")
    
    @staticmethod
    def create_draft(data: CreateReversalSchema):
        try:
            payload = create_payload(data, draft=True)
            ticket_data = TicketService.create_ticket("Reversion", payload)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al crear la reversion: {e}")
    
    @staticmethod
    def move(id: int, new_state: TicketState,  user_email: Optional[str] = None, payload: ReversalData = None):
        try:
            iterations = ReversalsService.get(id).get("iterations")
            ticket_data = TicketService.move_ticket(id, new_state, user_email, iterations, reversal_data_to_payload(payload))
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al mover la reversion: {e}")
    
    @staticmethod
    def add_comment(id: int, text: str, sender_email: str):
        try:
            message = f"{sender_email}: {text}{'.' if text[-1] != '.' else ''}"
            ticket_data = TicketService.add_comment_to_ticket(id, message)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al agregar comentario la reversion: {e}")
    
    @staticmethod
    def attach_files(id: int, file_paths: list[str], max_files: int = 10):
        try:
            ticket_data = TicketService.attach_files_to_ticket(id, file_paths, max_files)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al adjuntar archivos a la reversion: {e}")
    
    @staticmethod
    def remove_attachment(id: int, attachment_url: str):
        try:
            ticket_data = TicketService.remove_attachment_from_ticket(id, attachment_url)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al remover adjunto de la reversion: {e}")