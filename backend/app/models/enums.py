import enum

class CondicionLaboral(str, enum.Enum):
    NO_TRABAJA = "no_trabaja"
    MEDIO_TIEMPO = "medio_tiempo"
    TIEMPO_COMPLETO = "tiempo_completo"

class HorasEstudio(str, enum.Enum):
    POCAS = "pocas"  # Menos de 10 hs/semana
    NORMAL = "normal" # 10-20 hs/semana
    MUCHAS = "muchas" # Más de 20 hs/semana

class ColegioSecundario(str, enum.Enum):
    TECNICA_INFORMATICA = "tecnica_informatica"
    TECNICA_OTRA = "tecnica_otra"
    BACHILLER = "bachiller"

class MetodoEstudio(str, enum.Enum):
    SOLO = "solo"
    GRUPO = "grupo"
    MIXTO = "mixto"

# --- NUEVOS ENUMS PARA ARQUETIPOS ---
class FacilidadAprendizaje(str, enum.Enum):
    RAPIDA = "rapida"
    NORMAL = "normal"
    CUESTA = "cuesta"

class ConectividadInternet(str, enum.Enum):
    ESTABLE = "estable"
    INESTABLE = "inestable"
    NULA = "nula"

class EquipamientoInformatico(str, enum.Enum):
    PC_PROPIA = "pc_propia"
    PC_COMPARTIDA = "pc_compartida"
    SIN_PC = "sin_pc"

class EntornoEstudio(str, enum.Enum):
    SILENCIOSO = "silencioso"
    RUIDOSO = "ruidoso"
