# Este es el archivo: backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
from .perfil import UserMateria
from .enums import (
    CondicionLaboral,
    HorasEstudio,
    ColegioSecundario,
    MetodoEstudio,
    FacilidadAprendizaje,
    ConectividadInternet,
    EquipamientoInformatico,
    EntornoEstudio
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    # Changed func.now() to func.current_timestamp() for broader compatibility (SQLite)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())

    # Condicion laboral y horas de estudio
    condicion_laboral = Column(SAEnum(CondicionLaboral, native_enum=False), default=CondicionLaboral.NO_TRABAJA)
    horas_estudio = Column(SAEnum(HorasEstudio, native_enum=False), default=HorasEstudio.NORMAL)
    
    # Factor: Colegio Secundario
    colegio_secundario = Column(SAEnum(ColegioSecundario, native_enum=False), default=ColegioSecundario.BACHILLER)
    
    # Factor: Método de Estudio
    metodo_estudio_preferido = Column(SAEnum(MetodoEstudio, native_enum=False), default=MetodoEstudio.SOLO)

    # Factor: Situación de Hogar
    vive_solo = Column(Boolean, default=False)
    tiene_hijos = Column(Boolean, default=False)
    
    # Factor: Lugar de Residencia
    es_del_interior = Column(Boolean, default=False)
    residencia_capital = Column(Boolean, default=True)

    # --- NUEVAS COLUMNAS PARA ARQUETIPOS ---
    facilidad_aprendizaje = Column(SAEnum(FacilidadAprendizaje, native_enum=False), default=FacilidadAprendizaje.NORMAL)
    conectividad_internet = Column(SAEnum(ConectividadInternet, native_enum=False), default=ConectividadInternet.ESTABLE)
    equipamiento_informatico = Column(SAEnum(EquipamientoInformatico, native_enum=False), default=EquipamientoInformatico.PC_PROPIA)
    entorno_estudio = Column(SAEnum(EntornoEstudio, native_enum=False), default=EntornoEstudio.SILENCIOSO)
    realiza_actividad_fisica = Column(Boolean, default=True)
    # ---------------------------------------

    materias_cursadas = relationship("UserMateria", back_populates="owner")
