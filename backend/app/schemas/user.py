# Este es el archivo: backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from .perfil import UserMateriaOut
from ..models.enums import (
    CondicionLaboral,
    HorasEstudio,
    ColegioSecundario,
    MetodoEstudio,
    FacilidadAprendizaje,
    ConectividadInternet,
    EquipamientoInformatico,
    EntornoEstudio
)

# --- Schema para crear un usuario ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=15)
    full_name: str | None = None

# --- Schema para actualizar el perfil ---
class UserPerfilUpdate(BaseModel):
    full_name: str | None = None
    condicion_laboral: CondicionLaboral | None = None
    horas_estudio: HorasEstudio | None = None
    colegio_secundario: ColegioSecundario | None = None
    metodo_estudio_preferido: MetodoEstudio | None = None
    vive_solo: bool | None = None
    tiene_hijos: bool | None = None
    es_del_interior: bool | None = None

    # --- Nuevos campos ---
    facilidad_aprendizaje: FacilidadAprendizaje | None = None
    conectividad_internet: ConectividadInternet | None = None
    equipamiento_informatico: EquipamientoInformatico | None = None
    entorno_estudio: EntornoEstudio | None = None
    realiza_actividad_fisica: bool | None = None
    residencia_capital: bool | None = None

# --- Schema para devolver un usuario ---
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    created_at: datetime
    materias_cursadas: list[UserMateriaOut] = [] 
    
    # Perfil
    condicion_laboral: CondicionLaboral | None
    horas_estudio: HorasEstudio | None
    colegio_secundario: ColegioSecundario | None
    metodo_estudio_preferido: MetodoEstudio | None
    vive_solo: bool | None
    tiene_hijos: bool | None
    es_del_interior: bool | None

    # --- Nuevos campos ---
    facilidad_aprendizaje: FacilidadAprendizaje | None
    conectividad_internet: ConectividadInternet | None
    equipamiento_informatico: EquipamientoInformatico | None
    entorno_estudio: EntornoEstudio | None
    realiza_actividad_fisica: bool | None
    residencia_capital: bool | None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None
