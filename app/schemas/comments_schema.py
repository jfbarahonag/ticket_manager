# app/schemas/ticket_schema.py

from pydantic import BaseModel

# Esquema para agregar un comentario
class AddCommentSchema(BaseModel):
    text: str