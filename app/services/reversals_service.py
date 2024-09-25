from typing import Any

from app.schemas.reversal_schema import CreateReversalSchema
from app.models.reversal_model import ReversalType

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers
from app.services.comments_service import CommentsService
from app.services.ticket_service import TicketService

def create_payload(data: CreateReversalSchema):
    title = f"{data.client.NIT}-{data.client.obligationNumber}-{data.data.type}"
    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title},
        {"op": "add", "path": "/fields/Custom.Tipo", "value": data.data.type},
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
    
    if data.data.type == ReversalType.porErroresOperativos:
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Errores", "value": data.data.byOperational.errors},
            {"op": "add", "path": "/fields/Custom.Medidascorrectivas", "value": data.data.byOperational.correctiveActions},
        ])
    elif data.data.type == ReversalType.porErroresCliente:
        ##TODO: Validar si la fecha es mayor a 30 dias debe pedir VoBo R
        payload.extend([
            {"op": "add", "path": "/fields/Custom.Fechadelpagoerroneo", "value": data.data.byClient.dateOfIncorrectPayment},
        ])
    
    return payload

def feed_ticket_data(data: dict[str, Any]):
    azure_data = data["azure"]
            
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
            ticket_data = TicketService.create_ticket("Reversiones", payload)
            return feed_ticket_data(ticket_data)
        except ValueError as e:
            raise ValueError(f"Error al crear la reversion: {e}")
    
    def move():
        pass