# Este es el archivo: backend/app/services/scoring_service.py

from rdflib import Graph
from app.models.user import User
from app.core.reglas_negocio import FACTORES_SCORING

def _normalizar(valor: int, min_val: int, max_val: int) -> float:
    """Convierte un valor a una escala de 0 a 1."""
    if max_val == min_val: return 0.0
    # Asegura que el valor esté dentro de los límites
    valor = max(min_val, min(valor, max_val))
    return (valor - min_val) / (max_val - min_val)

def calcular_score_materia(datos_materia: dict, user: User, kg: Graph) -> float:
    """
    Calcula un "score" (puntuación) de 0 a 1 para una materia, 
    indicando qué tan recomendable es cursarla AHORA.
    Considera: Dificultad, Impacto en Cadena (Desbloqueos), Año y Créditos.
    """
    score_total = 0.0
    
    # --- 1. Factor: Dificultad de Cursada ---
    # (Preferimos cursar las fáciles primero o las difíciles según el perfil, 
    # por defecto invertimos: menos dificultad = más score)
    factor_dificultad = FACTORES_SCORING["dificultad_cursada"]
    dificultad = datos_materia.get("dificultad", 1) # default 1 (fácil)
    score_dificultad = _normalizar(dificultad, 
                                 factor_dificultad["min"], 
                                 factor_dificultad["max"])
    if factor_dificultad["invertido"]:
        score_dificultad = 1.0 - score_dificultad 
    
    score_total += score_dificultad * factor_dificultad["peso"]
    
    # --- 2. Factor: Impacto Estratégico (Desbloqueos Transitivos) ---
    # Ahora 'desbloquea_count' trae la cuenta de TODA la cadena futura, no solo la inmediata.
    factor_desbloqueo = FACTORES_SCORING["correlativas_desbloqueadas"]
    desbloquea = datos_materia.get("desbloquea_count", 0)
    
    # Normalizamos sobre 30 (un número alto de materias futuras posibles)
    score_desbloqueo = _normalizar(desbloquea, 0, 30)
    score_total += score_desbloqueo * factor_desbloqueo["peso"]

    # --- 3. Factor: Año de Carrera (Prioridad a materias atrasadas) ---
    factor_año = FACTORES_SCORING["año_carrera"]
    año_materia = datos_materia.get("año", 1)
    
    # Si la materia es de 1ro o 2do año, le damos un empujón extra para que se las saque de encima
    bonus_atraso = 0.0
    if año_materia <= 2:
        bonus_atraso = 0.15

    score_año = _normalizar(año_materia, factor_año["min"], factor_año["max"])
    score_total += (score_año * factor_año["peso"]) + bonus_atraso
    
    # --- 4. Factor: Créditos (Nuevo) ---
    # Si otorga créditos (es optativa), suma un pequeño plus
    creditos = datos_materia.get("creditos_otorgados", 0)
    if creditos > 0:
        # Normalizamos: 90 créditos = 0.1 puntos extra
        score_total += (creditos / 100.0) * 0.1

    return score_total