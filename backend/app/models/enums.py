# Este es un archivo NUEVO: backend/app/models/enums.py

import enum

class CondicionLaboral(str, enum.Enum):
    NO_TRABAJA = "no_trabaja"
    MEDIO_TIEMPO = "medio_tiempo"
    TIEMPO_COMPLETO = "tiempo_completo"

class HorasEstudio(str, enum.Enum):
    POCAS = "pocas"  # Menos de 10 hs/semana
    NORMAL = "normal" # 10-20 hs/semana
    MUCHAS = "muchas" # Más de 20 hs/semana

# --- ¡NUEVO ENUM! ---
class ColegioSecundario(str, enum.Enum):
    TECNICA_INFORMATICA = "tecnica_informatica"
    TECNICA_OTRA = "tecnica_otra"
    BACHILLER = "bachiller"

class MetodoEstudio(str, enum.Enum):
    SOLO = "solo"
    GRUPO = "grupo"
    MIXTO = "mixto"
# --------------------