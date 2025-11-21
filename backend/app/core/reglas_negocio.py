# Este es un archivo NUEVO: backend/app/core/reglas_negocio.py

from app.models.enums import CondicionLaboral

# Define la carga de trabajo máxima permitida según la condición laboral.
# Dificultad 3 = Difícil, Dificultad 4 = Muy Difícil
REGLAS_CURSADA = {
    # Valor del enum CondicionLaboral
    CondicionLaboral.NO_TRABAJA.value: {
        "max_materias_totales": 5,
        "max_materias_dificiles": 2, # (Nivel 3 o 4)
        "evitar_combinaciones": [] # Podría ser ["Nivel_4 + Nivel_4"]
    },
    CondicionLaboral.MEDIO_TIEMPO.value: {
        "max_materias_totales": 3,
        "max_materias_dificiles": 1,
        "evitar_combinaciones": ["Nivel_4 + Nivel_3", "Nivel_4 + Nivel_4"]
    },
    CondicionLaboral.TIEMPO_COMPLETO.value: {
        "max_materias_totales": 2,
        "max_materias_dificiles": 1,
        # Regla estricta: si trabaja full-time, no puede cursar Nivel 4 + Nivel 3.
        # Y solo puede llevar 1 materia Nivel 3 o 4, no más.
        "evitar_combinaciones": ["Nivel_4 + Nivel_3", "Nivel_4 + Nivel_4", "Nivel_3 + Nivel_3"]
    }
}

# Define los pesos para el algoritmo de scoring (Puntuación de 0 a 1)
# Un peso más alto significa que el factor es más importante.
FACTORES_SCORING = {
    "dificultad_cursada": {
        "peso": 0.25, 
        "min": 1, 
        "max": 4,
        "invertido": True # Menos dificultad = MÁS score
    },
    "correlativas_desbloqueadas": {
        "peso": 0.30, 
        "min": 0, 
        "max": 5, # Asumimos 5 como un máx. razonable de desbloqueo
        "invertido": False # Más desbloqueos = MÁS score
    },
    "año_carrera": {
        "peso": 0.15, 
        "min": 1, 
        "max": 5,
        "invertido": False # Año más alto = MÁS score (para priorizar)
    }
    # Se pueden añadir más factores del prompt aquí, como "preferencia_modalidad"
}