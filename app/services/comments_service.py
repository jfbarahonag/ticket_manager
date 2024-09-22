import requests

from app.services.common import AZURE_ORG_URL, PROJECT_NAME, create_headers

class CommentsService:
    @staticmethod
    def add_comment_to_ticket(ticket_id: int, comment: str):
        # Agregar un comentario a un ticket de Azure DevOps
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workItems/{ticket_id}/comments?api-version=7.0-preview.3"
        payload = {
            "text": comment
        }

        response = requests.post(url, headers=create_headers(content_type="application/json"), json=payload)

        if response.status_code in [200, 201]:
            return {
                "status": "success", 
                "comment_id": response.json()["id"],
                "comment_text": payload["text"]
            }
        else:
            raise ValueError(f"Error al agregar comentario al ticket {ticket_id}: {response.status_code} - {response.content.decode()}")
    
    @staticmethod
    def get_comments_of_a_ticket(ticket_id):
        url = f"{AZURE_ORG_URL}/{PROJECT_NAME}/_apis/wit/workitems/{ticket_id}/comments?$api-version=7.1-preview.4"
        response = requests.get(url, headers=create_headers())

        if response.status_code in [200, 201]:
            comments = [{
                "id": c['id'], 
                "text": c['text']
            } for c in response.json().get("comments", {})]
            return {
                "status": "success", 
                "comments": comments
            }
        else:
            raise ValueError(f"Error al obtener los comentario del ticket {ticket_id}: {response.status_code} - {response.content.decode()}")