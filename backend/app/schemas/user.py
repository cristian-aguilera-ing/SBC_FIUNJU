# Este es el archivo: backend/app/schemas/user.py

from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from .perfil import UserMateriaOut
from ..models.enums import CondicionLaboral, HorasEstudio, ColegioSecundario, MetodoEstudio # <-- NUEVA IMPORTACIÓN

# --- Schema para crear un usuario (sigue igual) ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=15)
    full_name: str | None = None

# --- ¡NUEVO SCHEMA! ---
# Define los campos que el usuario PUEDE actualizar de su perfil
class UserPerfilUpdate(BaseModel):
    full_name: str | None = None
    condicion_laboral: CondicionLaboral | None = None
    horas_estudio: HorasEstudio | None = None
    # --- Nuevos campos ---
    colegio_secundario: ColegioSecundario | None = None
    metodo_estudio_preferido: MetodoEstudio | None = None
    vive_solo: bool | None = None
    tiene_hijos: bool | None = None
    es_del_interior: bool | None = None

# --- Schema para devolver un usuario (MODIFICADO) ---
class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None
    created_at: datetime
    materias_cursadas: list[UserMateriaOut] = [] 
    
    # Ahora el perfil del usuario incluye esta información
    condicion_laboral: CondicionLaboral | None
    horas_estudio: HorasEstudio | None
    # --- Nuevos campos ---
    colegio_secundario: ColegioSecundario | None
    metodo_estudio_preferido: MetodoEstudio | None
    vive_solo: bool | None
    tiene_hijos: bool | None
    es_del_interior: bool | None

    model_config = ConfigDict(from_attributes=True)

# --- Schemas de Token (siguen igual) ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None