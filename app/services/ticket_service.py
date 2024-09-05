# app/services/ticket_service.py

from typing import Dict
from app.models.ticket_model import Ticket, TicketState

# Simulación de base de datos de tickets
ticket_db: Dict[int, Ticket] = {
    1: Ticket(id=1, title="Ticket 1", description="Descripción 1", state=TicketState.solicitado),
    2: Ticket(id=2, title="Ticket 2", description="Descripción 2", state=TicketState.en_evaluacion),
}

# Reglas de transición
transition_rules = {
    TicketState.solicitado: [TicketState.devuelto, TicketState.asignado],
    TicketState.devuelto: [TicketState.solicitado],
    TicketState.asignado: [TicketState.en_evaluacion],
    TicketState.en_evaluacion: [TicketState.aprobado, TicketState.rechazado],
}

class TicketService:
    @staticmethod
    def move_ticket(ticket_id: int, new_state: TicketState) -> Ticket:
        # Buscar el ticket en la "base de datos"
        if ticket_id not in ticket_db:
            raise ValueError(f"Ticket con ID {ticket_id} no encontrado")

        ticket = ticket_db[ticket_id]
        current_state = ticket.state

        # Validar si la transición es permitida
        if new_state not in transition_rules.get(current_state, []):
            raise ValueError(f"No se puede mover el ticket de {current_state} a {new_state}")

        # Actualizar el estado del ticket
        ticket.state = new_state
        ticket_db[ticket_id] = ticket  # Guardar cambios
        return ticket
