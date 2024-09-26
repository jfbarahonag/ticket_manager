import os
import base64
from dotenv import load_dotenv

# Cargar variables de entorno desde .env en desarrollo
if os.getenv('ENVIRONMENT', 'dev') == 'dev':
    load_dotenv()  # Carga las variables del archivo .env

# Cargar las variables de entorno
AZURE_ORG_URL = os.getenv('AZURE_ORG_URL')
PROJECT_NAME = os.getenv('PROJECT_NAME')
PAT_TOKEN = os.getenv('PAT_TOKEN')

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