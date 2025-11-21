# Este es el archivo: backend/app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base
from .perfil import UserMateria
from .enums import CondicionLaboral, HorasEstudio, ColegioSecundario, MetodoEstudio

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # --- ¡ESTA ES LA CORRECCIÓN! ---
    condicion_laboral = Column(SAEnum(CondicionLaboral, native_enum=False), default=CondicionLaboral.NO_TRABAJA)
    horas_estudio = Column(SAEnum(HorasEstudio, native_enum=False), default=HorasEstudio.NORMAL)
    # --- FIN DE LA CORRECCIÓN ---
    
    # --- ¡NUEVAS COLUMNAS! ---
    # Factor: Colegio Secundario
    colegio_secundario = Column(SAEnum(ColegioSecundario, native_enum=False), default=ColegioSecundario.BACHILLER)
    
    # Factor: Método de Estudio
    metodo_estudio_preferido = Column(SAEnum(MetodoEstudio, native_enum=False), default=MetodoEstudio.SOLO)

    # Factor: Situación de Hogar
    vive_solo = Column(Boolean, default=False)
    tiene_hijos = Column(Boolean, default=False)
    
    # Factor: Lugar de Residencia
    es_del_interior = Column(Boolean, default=False)
    # -------------------------

    materias_cursadas = relationship("UserMateria", back_populates="owner")