# Este es el archivo: backend/app/schemas/ontologia.py

from pydantic import BaseModel

class MateriaOntology(BaseModel):
    uri: str
    label: str
    año: int | None = None 
    creditos: int = 0
    requisitos: list[str] = []

class TopicoOntology(BaseModel):
    uri: str
    label: str