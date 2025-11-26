from app.models.enums import CondicionLaboral

# Mapeo de colores para el frontend (Tailwind CSS classes o valores hex)
# 1: Rojo, 2: Naranja, 3: Amarillo, 4: Verde, 5: Azul, 6: Violeta, 7: Marron

PERFILES_DATA = {
    1: {
        "nombre_corto": "Perfil Crítico", # Antes "El Superviviente"
        "color": "#ef4444", # Red-500
        "descripcion": "Trabaja mucho + Interior + Solo + Hijos",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO and u.es_del_interior,
        "cursada": {
            "comentario": "Tu perfil tiene 'muy poco tiempo para estudiar'. No se permiten errores.\n\n* trabajas tiempo completo\n* Vivis lejos\n* vivis solo\n* tenes hijo/s\n\nConsejo: Necesitas cursar muy pocas materias y priorizar las más fáciles.\nLa perseverancia es clave.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo", # Placeholder, se pisa dinámicamente
            "reglas": {"max_qty": 2, "max_dificultad": 1},
            "planes": {
                "A": "Plan A (Ideal): 2 materias Fáciles. (Es el límite real de tu energía diaria; no te sobreexijas).",
                "B": "Plan B (Solo hay Normales): 1 materia Normal. (No se recomienda cursar 2 normales, el riesgo de abandono es altísimo).",
                "C": "Plan C (Solo hay Difíciles): 1 materia Difícil. (Advertencia: Solo si es la única actividad académica).",
                "D": "Plan D (Solo hay Muy Difíciles): No cursar este cuatrimestre o cursar 1 Muy Difícil sabiendo que requerirá sacrificar fines de semana."
            }
        },
        "finales": {
            "comentario": "Te conviene rendir finales a final del cuatrimestre o al inicio, donde hay bastante demanda de chicos interesados en rendir un final.\nSiempre consultá a la cátedra sobre el formato del final.",
            "recomendacion_texto": "Ver Plan A/B/C abajo",
            "reglas": {"max_qty": 1, "max_dificultad": 1},
            "planes": {
                "A": "Plan A: 1 Final Fácil. (Ideal para mantener la constancia sin saturarte).",
                "B": "Plan B: 1 Final Normal. (Advertencia: Preparalo con tiempo, tus bloques de estudio son cortos y fragmentados).",
                "C": "Plan C: 1 Final Difícil. No rendir finales complejos mientras se cursa. Postergar para fechas sin cursada."
            }
        }
    },
    2: {
        "nombre_corto": "El Malabarista Urbano",
        "color": "#f97316", # Orange-500
        "descripcion": "Trabaja mucho + Capital + Familia",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO and not u.es_del_interior,
        "cursada": {
            "comentario": "Balancea tus prioridades. Procura materias con menor carga horaria y parciales accesibles.",
            "recomendacion_texto": "1 materia normal\n1 materia fácil\nEvitar difíciles",
            "reglas": {"max_qty": 2, "allowed_levels": [1, 2]}
        },
        "finales": {
            "comentario": "Prioriza las materias con finales multiple opción. Organiza un grupo de estudio.",
            "recomendacion_texto": "1 materia normal\n1 materia fácil",
            "reglas": {"max_qty": 2, "allowed_levels": [1, 2]}
        }
    },
    3: {
        "nombre_corto": "El Guerrero Solitario",
        "color": "#eab308", # Yellow-500
        "descripcion": "Trabaja poco + Interior + Solo",
        # Flexibilizamos: Si trabaja medio tiempo Y es del interior, es perfil 3 (sin importar si vive solo o no)
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO and u.es_del_interior,
        "cursada": {
            "comentario": "Prioriza las materias troncales. Usá parciales de años anteriores y clases grabadas.",
            "recomendacion_texto": "1 materia difícil\n1-2 materias normales\nEvitar muy difíciles",
            "reglas": {"max_qty": 3, "max_dificultad": 3}
        },
        "finales": {
            "comentario": "Organiza tus tiempos y centrate en rendir el final mas dificil.",
            "recomendacion_texto": "1 materia difícil",
            "reglas": {"max_qty": 1, "min_dificultad": 3}
        }
    },
    4: {
        "nombre_corto": "Trabaja poco + Capital + Familia",
        "color": "#22c55e", # Green-500
        "descripcion": "Trabaja poco + Capital + Familia",
        # Flexibilizamos: Si trabaja medio tiempo Y es de capital, es perfil 4
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO and not u.es_del_interior,
        "cursada": {
            "comentario": "Prioriza las materias troncales, y organizate bien para no perder la promocion. Si no entiendes un tema, anda a consulta. Estudiar en la facultad te ayuda a concentrarte más. Practica parciales de años anteriores.",
            "recomendacion_texto": "1 materia muy difícil\n1 materia difícil\n1 materia normal",
            "reglas": {"max_qty": 3, "target_distribution": {4:1, 3:1, 2:1}}
        },
        "finales": {
            "comentario": "Rendir a fin de cuatrimestre o al inicio puede ser estratégico.",
            "recomendacion_texto": "1 muy difícil\n1 difícil\n1 normal",
            "reglas": {"max_qty": 3}
        }
    },
    5: {
        "nombre_corto": "El Ermitaño del Interior",
        "color": "#3b82f6", # Blue-500
        "descripcion": "No trabaja + Interior + Solo",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.NO_TRABAJA and u.es_del_interior and u.vive_solo,
        "cursada": {
            "comentario": "Tenés mucho tiempo, pero vivir solo y lejos consume horas. Practicá parciales.",
            "recomendacion_texto": "1 materia muy difícil\n1 materia difícil\n1 materia normal",
            "reglas": {"max_qty": 3}
        },
        "finales": {
            "comentario": "Organiza tus tiempos para rendir 2 materias en una misma mesa.",
            "recomendacion_texto": "1 muy difícil\n1 difícil\n1 normal",
            "reglas": {"max_qty": 3}
        }
    },
    6: {
        "nombre_corto": "El Heredero del Trono",
        "color": "#a855f7", # Purple-500
        "descripcion": "No trabaja + Capital + Familia (Ideal)",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.NO_TRABAJA and not u.es_del_interior and not u.vive_solo and not u.tiene_hijos,
        "cursada": {
            "comentario": "Tenés el perfil con más disponibilidad. Prioriza todas las materias. No te quedes libre.",
            "recomendacion_texto": "3 materias (muy difícil/difícil)\n1 normal",
            "reglas": {"max_qty": 4, "min_dificultad": 2}
        },
        "finales": {
            "comentario": "Podés preparar varias materias a la vez. Intenta inscribirte a las materias recién cursadas.",
            "recomendacion_texto": "3 muy difícil/difícil\n1 normal",
            "reglas": {"max_qty": 4}
        }
    },
    7: {
        "nombre_corto": "El Padre/Madre Full-Time",
        "color": "#a16207", # Yellow-800/Brown
        "descripcion": "No trabaja (o poco) + Hijos",
        # Condición fuerte: Si tiene hijos y no trabaja full time (si trabaja full time cae en el 1 o 2)
        "condiciones": lambda u: u.tiene_hijos and u.condicion_laboral != CondicionLaboral.TIEMPO_COMPLETO,
        "cursada": {
            "comentario": "Cuidá tus tiempos, tomá buenas notas y mantené constancia.",
            "recomendacion_texto": "1 muy difícil\n1 difícil\n1 normal",
            "reglas": {"max_qty": 3}
        },
        "finales": {
            "comentario": "Enfócate en una materia troncal por mesa.",
            "recomendacion_texto": "1 muy difícil\n1 difícil\n1 normal",
            "reglas": {"max_qty": 3}
        }
    }
}

def obtener_perfil_id(user):
    """Evalúa las condiciones del usuario con prioridad jerárquica."""
    
    # 1. Prioridad Hijos + Trabajo Full Time (Perfil 1 o 2)
    if user.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO:
        if user.es_del_interior: return 1 # Superviviente
        return 2 # Malabarista (Capital)

    # 2. Prioridad Hijos (Perfil 7 si no trabaja full time, o casos bordes)
    if user.tiene_hijos:
        return 7 

    # 3. Prioridad Medio Tiempo (Perfil 3 o 4)
    if user.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO:
        if user.es_del_interior: return 3 # Guerrero
        return 4 # Equilibrado

    # 4. Prioridad No Trabaja (Perfil 5 o 6)
    if user.condicion_laboral == CondicionLaboral.NO_TRABAJA:
        if user.es_del_interior: return 5 # Ermitaño
        return 6 # Heredero (o default ideal)

    # Fallback seguro (Equilibrado)
    return 4