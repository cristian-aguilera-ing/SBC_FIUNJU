# Este es el archivo: backend/app/schemas/recomendacion.py

from pydantic import BaseModel
from datetime import datetime
from ..models.enums import CondicionLaboral, EquipamientoInformatico

class MateriaRecomendada(BaseModel):
    uri: str
    label: str
    score: float
    año: int
    dificultad: int
    desbloquea_count: int
    creditos_otorgados: int = 0

class ArquetipoInfo(BaseModel):
    nombre: str
    color: str
    consejos: list[str]

class PlanCursadaRecomendado(BaseModel):
    plan_recomendado: list[MateriaRecomendada]
    materias_omitidas: list[MateriaRecomendada]
    arquetipo: ArquetipoInfo # Nuevo campo
    consejos_adicionales: list[str]

class MateriaExamenRecomendada(BaseModel):
    uri: str
    label: str
    # Eliminamos fecha y días restantes para limpiar la UI
    dificultad_examen_label: str
    dificultad_examen_valor: int
    modalidades: list[str]
    
    # Estado
    esta_habilitada: bool = True 
    motivo_bloqueo: str | None = None
    correlativas_pendientes: list[str] = []
    
    # Sugerencia personalizada
    consejo_personalizado: str | None = None 

class PlanExamenRecomendado(BaseModel):
    plan_recomendado: list[MateriaExamenRecomendada]
    consejos_adicionales: list[str]

class PlanCursadaSimuladoRequest(BaseModel):
    condicion_laboral: CondicionLaboral | None = None
    vive_solo: bool | None = None
    tiene_hijos: bool | None = None
    es_del_interior: bool | None = None
    equipamiento_informatico: EquipamientoInformatico | None = None
    residencia_capital: bool | None = None
