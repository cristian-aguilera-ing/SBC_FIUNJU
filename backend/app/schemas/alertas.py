# Este es un archivo NUEVO: backend/app/schemas/alertas.py
from pydantic import BaseModel
from enum import Enum

class TipoAlerta(str, Enum):
    RIESGO_REGULARIDAD = "riesgo_regularidad"
    CUELLO_DE_BOTELLA = "cuello_de_botella"
    SOBRECARGA = "sobrecarga"
    OPORTUNIDAD_ACADEMICA = "oportunidad_academica"

class Alerta(BaseModel):
    tipo: TipoAlerta
    mensaje: str
    materia_uri: str | None = None
    materia_label: str | None = None