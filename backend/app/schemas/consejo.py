# Este es el archivo: backend/app/schemas/consejo.py

from pydantic import BaseModel

class ConsejoRequest(BaseModel):
    materia_uris_request: list[str]
    topico_uri: str | None = None # El tópico es opcional