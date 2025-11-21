# Este es el archivo: backend/app/models/perfil.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..core.database import Base
from sqlalchemy.sql import func

class UserMateria(Base):
    __tablename__ = "perfil_materias"

    id = Column(Integer, primary_key=True, index=True)
    materia_uri = Column(String, index=True, nullable=False)
    estado = Column(String, default="Cursando") # Ej. "Cursando", "Regular", "Aprobada"
    
    # Guarda la fecha y hora en que se marcó como regular
    fecha_regularidad = Column(DateTime(timezone=True), nullable=True) 

    # Clave foránea que vincula esta tabla con la tabla 'users'
    user_id = Column(Integer, ForeignKey("users.id"))

    # Define la relación inversa: "Este registro pertenece a un 'User'"
    owner = relationship("User", back_populates="materias_cursadas")