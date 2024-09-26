import os
import requests

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers

class AttachmentsService:
    @staticmethod
    def upload_attachment(file_path: str):
        
        # Extraer el nombre del archivo de manera compatible con Linux y Windows
        file_name = os.path.basename(file_path)

        # Construir la URL usando el nombre del archivo extraído
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/attachments?fileName={file_name}&api-version=7.1"
        
        with open(file_path, 'rb') as file:
            response = requests.post(url, headers=create_headers(content_type="application/octet-stream"), data=file)

            if response.status_code in [200, 201]:
                return response.json()["url"]
            else:
                raise ValueError(f"Error al subir el archivo: {response.status_code} - {response.content.decode()}")

    # Método para adjuntar múltiples archivos a un ticket
    @staticmethod
    def attach_files_to_ticket(ticket_id: int, file_paths: list[str]):

        # Subir cada archivo y adjuntarlo al ticket
        relations = []
        for file_path in file_paths:
            attachment_url = AttachmentsService.upload_attachment(file_path)
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

    @staticmethod
    def remove_attachment_from_ticket(ticket_id: int, attachment_index: int):
        # URL para actualizar el Work Item en Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}?api-version=7.1"

        # Payload para eliminar la relación del archivo adjunto
        payload = [
            {
                "op": "remove",
                "path": f"/relations/{attachment_index}"
            }
        ]

        # Hacer la solicitud PATCH para eliminar la relación de adjunto
        response = requests.patch(url, headers=create_headers(), json=payload)

        if response.status_code in [200, 201]:
            return {"status": "success", "ticket_id": ticket_id, "attachment_index": attachment_index}
        else:
            raise ValueError(f"Error al eliminar el archivo adjunto: {response.status_code} - {response.content.decode()}")