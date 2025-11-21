# Este es el archivo: backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
from .perfil import UserMateria
from .enums import (
    CondicionLaboral,
    EquipamientoInformatico,
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    # Changed func.now() to func.current_timestamp() for broader compatibility (SQLite)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    # Condicion laboral
    condicion_laboral = Column(SAEnum(CondicionLaboral, native_enum=False), default=CondicionLaboral.NO_TRABAJA)
    
    # Factor: Situación de Hogar
    vive_solo = Column(Boolean, default=False)
    tiene_hijos = Column(Boolean, default=False)
    
    # Factor: Lugar de Residencia
    es_del_interior = Column(Boolean, default=False)
    residencia_capital = Column(Boolean, default=True)

    # --- NUEVAS COLUMNAS PARA ARQUETIPOS ---
    equipamiento_informatico = Column(SAEnum(EquipamientoInformatico, native_enum=False), default=EquipamientoInformatico.PC_PROPIA)
    # ---------------------------------------

    materias_cursadas = relationship("UserMateria", back_populates="owner")
