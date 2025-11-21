import enum

class CondicionLaboral(str, enum.Enum):
    NO_TRABAJA = "no_trabaja"
    MEDIO_TIEMPO = "medio_tiempo"
    TIEMPO_COMPLETO = "tiempo_completo"

class EquipamientoInformatico(str, enum.Enum):
    PC_PROPIA = "pc_propia"
    PC_COMPARTIDA = "pc_compartida"
    SIN_PC = "sin_pc"
