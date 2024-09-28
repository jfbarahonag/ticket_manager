# app/main.py

from fastapi import FastAPI
from mangum import Mangum
from app.controllers import ticket_controller, reversals_controller, teams_controller

app = FastAPI()

# Registrar las rutas
app.include_router(ticket_controller.router)
app.include_router(reversals_controller.router)
app.include_router(teams_controller.router)

# Inicia el servidor con: uvicorn app.main:app --reload
handler = Mangum(app)