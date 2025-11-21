# Este es el archivo: backend/app/schemas/perfil.py

from pydantic import BaseModel, ConfigDict
from datetime import datetime

# Schema base (los datos mínimos)
class UserMateriaBase(BaseModel):
    materia_uri: str
    estado: str = "Cursando"

    fecha_regularidad: datetime | None = None
    
# Schema para crear un registro (lo que envía el frontend)
class UserMateriaCreate(UserMateriaBase):
    pass

# Schema para devolver datos (lo que envía el backend)
class UserMateriaOut(UserMateriaBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)