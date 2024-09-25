import requests

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

class ReversalsService:
    @staticmethod
    def get(reversal_id: int):
        try:
            reversal_data = TicketService.get_ticket_data(reversal_id)
            
            reversal_data["lastTimeInDraft"] = reversal_data["azure"]["Custom.Ultimavezenborrador"]
            reversal_data["lastTimeRequested"] = reversal_data["azure"]["Custom.Ultimavezsolicitado"]
            reversal_data["lastTimeAssigned"] = reversal_data["azure"]["Custom.Ultimavezasignado"]
            reversal_data["lastTimeInEvaluation"] = reversal_data["azure"]["Custom.Ultimavezenevaluacion"]
            reversal_data["lastTimeReturned"] = reversal_data["azure"]["Custom.Ultimavezquehubodevolucion"]
            reversal_data["timeFinishEvaluation"] = reversal_data["azure"]["Custom.Findeevaluacion"]
            
            # remove azure metadata
            reversal_data.pop("azure")
            
            return reversal_data
            
        except Exception as e:
            raise ValueError(f"Error al obtener la reversion: {e}")
    
    @staticmethod
    def create(data: CreateReversalSchema):
        try:
            payload = create_payload(data)
            ticket_data = TicketService.create_ticket("Reversion", payload)
            reversal_data = ReversalsService.get(ticket_data["id"])
            return reversal_data
        except ValueError as e:
            raise ValueError(f"Error al crear la reversion: {e}")
    
    def move():
        pass