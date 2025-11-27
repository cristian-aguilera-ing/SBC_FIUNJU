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
        "nombre_corto": "Perfil Bajo",
        "color": "#f97316", # Orange-500
        "descripcion": "Trabaja mucho + Capital + Familia",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO and not u.es_del_interior,
        "cursada": {
            "comentario": "Tiene un poco más de tiempo gracias al apoyo familiar y vivir cerca.\n\n* trabajas tiempo completo\n* Vivis en Capital\n* No vives solo\n* tenes hijo/s\n\nConsejo: Balancea tus prioridades a las materias que querés cursar, procura que sea una materia con menor carga horaria y con parciales accesibles. Aprovecha tus tiempos libres, para estudiar en lugares tranquilos como la facultad.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo",
            "reglas": {"max_qty": 2, "max_dificultad": 2},
            "planes": {
                "A": "Plan A (Ideal): 2 materias Fácil. (Combinación segura gracias a que tenés buen soporte en casa).",
                "B": "Plan B (No hay Fáciles): 2 materias Normales. (Riesgoso: Solo recomendable si las fechas de parciales no caen en la misma semana).",
                "C": "Plan C (Solo hay Difíciles): 1 materia Difícil. (Advertencia: Estudiar en lugares tranquilos como la facultad, para evitar las distracciones del entorno).",
                "D": "Plan D (Solo hay Muy Difíciles): 1 materia Muy Difícil. (Solo si no hay otra opción y podes concentrar toda tu atención durante toda la cursada)."
            }
        },
        "finales": {
            "comentario": "Prioriza las materias con finales múltiple opción, para ir reduciendo las materias que tenes para rendir. Organiza un grupo de estudio para que se apoyen entre todos. Siempre consultá a la cátedra sobre el formato del final.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo",
            "reglas": {"max_qty": 2, "max_dificultad": 2},
            "planes": {
                "A": "Plan A: 1 Normal + 1 Difícil. (Aprovechá que una es múltiple choice y ve a consulta para ganar tiempo).",
                "B": "Plan B: 1 materia Difícil.",
                "C": "Plan C: 2 materias Difíciles (Solo si los exámenes están separados por 2 semanas).",
                "D": "Plan D: 1 Muy Difícil. (No se recomiendan 2 muy difíciles; el cansancio diario te va a jugar en contra)."
            }
        }
    },
    3: {
        "nombre_corto": "Perfil Medio-Bajo",
        "color": "#eab308", # Yellow-500
        "descripcion": "Trabaja medio tiempo + Interior + Solo",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO and u.es_del_interior,
        "cursada": {
            "comentario": "Tiene tiempo, pero viajar largas distancias más las tareas domésticas te quitan energía.\n\n* trabajas medio tiempo\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s\n\nConsejo: Prioriza las materias troncales, y organízate bien para no perder la promoción. Usá parciales de años anteriores y apuntes de compañeros.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo",
            "reglas": {"max_qty": 3, "max_dificultad": 3},
            "planes": {
                "A": "Plan A (Ideal): 1 Difícil + 2 Normal. (Tenés horas libres, pero el viaje largo consume mucha energía mental).",
                "B": "Plan B (No hay Difíciles): 3 Normales. (Debes dedicarle más tiempo al estudio sin perder el ritmo).",
                "C": "Plan C (Solo hay Difíciles): 2 materias Difíciles. (Riesgoso, requiere mucha disciplina y usar tus horas de viaje para leer).",
                "D": "Plan D (No hay Normales): 1 Muy Difícil + 1 Fácil. (Es el tope máximo de carga cognitiva para tu rutina)."
            }
        },
        "finales": {
            "comentario": "Organiza tus tiempos y centrate en rendir el final más difícil. Organiza un grupo de estudio para que se apoyen entre todos. Siempre consultá a la cátedra sobre el formato del final.",
            "recomendacion_texto": "Ver Plan A/B/C abajo",
            "reglas": {"max_qty": 2, "min_dificultad": 3},
            "planes": {
                "A": "Plan A: 1 Final Difícil. (Podés apuntar a nota alta si te organizas bien en tus otras tareas y dedicas tu tiempo a estudiar).",
                "B": "Plan B: 2 Finales Normales. (Averigua si las fechas de ambas están en la primera y segunda semana de la mesa de examen para tener margen de estudio).",
                "C": "Plan C: 1 Muy Difícil (Debes prepararte muy bien y en lo posible con un grupo de estudio)."
            }
        }
    },
    4: {
        "nombre_corto": "Perfil Equilibrado",
        "color": "#22c55e", # Green-500
        "descripcion": "Trabaja medio tiempo + Capital + Familia",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO and not u.es_del_interior and not u.vive_solo and not u.tiene_hijos,
        "cursada": {
            "comentario": "Es el balance perfecto. Puede asumir carga, pero no extrema.\n\n* trabajas medio tiempo\n* Vivis en Capital\n* No vivis solo\n* No tenes hijo/s\n\nConsejo: Prioriza las materias troncales, y organízate bien para no perder la promoción. Si no entiendes un tema, asiste a consultas. Estudiar en la facultad te ayuda a concentrarte más. Resuelve parciales de años anteriores.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo",
            "reglas": {"max_qty": 3, "max_dificultad": 4},
            "planes": {
                "A": "Plan A (Ideal): 1 Muy Difícil + 1 Difícil + 1 Normal. (Carga balanceada para no atrasarse y mantener buen ritmo).",
                "B": "Plan B (No hay Normales): 1 Muy Difícil + 1 Difícil. (Se prioriza calidad sobre cantidad para asegurar la promoción de ambas).",
                "C": "Plan C (Solo hay Normales): 3 materias Normales. (Ideal para limpiar materias pendientes, pero cuidado con subestimarlas y relajarte).",
                "D": "Plan D (Solo hay Muy Difíciles): 2 materias Muy Difíciles. (Advertencia: Solo si no tenés otras actividades extra curriculares previstas)."
            }
        },
        "finales": {
            "comentario": "Organiza tus tiempos y centrate en rendir el final mas dificil. Organiza un grupo de estudio para que se apoyen entre todos. Rendir a fin de cuatrimestre o al inicio puede ser estratégico. Aprovecha los horarios de consulta. Siempre consultá a la cátedra sobre el formato del final.",
            "recomendacion_texto": "Ver Plan A/C abajo",
            "reglas": {"max_qty": 2, "min_dificultad": 3},
            "planes": {
                "A": "Plan A: 1 Muy Difícil + 1 Normal. (Tenés las condiciones óptimas para concentrarte en temas complejos y aprovecha que tenes multiple choice en una).",
                "C": "Plan C: 2 Finales Difíciles. (Solo si hay al menos 10 días de separación entre mesas de examen)."
            }
        }
    },
    5: {
        "nombre_corto": "Perfil Medio-Alto",
        "color": "#0ea5e9", # Sky-500
        "descripcion": "No trabaja + Interior + Solo",
        "condiciones": lambda u: u.condicion_laboral == CondicionLaboral.NO_TRABAJA and u.es_del_interior and u.vive_solo and not u.tiene_hijos,
        "cursada": {
            "comentario": "Tiempo completo, pero vivir solo viene con tareas domésticas y viajar limita la \"energía mental\".\n\n* No trabajas\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s\n\nConsejo: Prioriza todas las materias, y organízate bien para no perder la promoción. No descuides tus tiempos libres, aprovéchalos para estudiar. Tenés mucho tiempo de estudio, pero vivir solo y lejos igual consume horas. Organízate, práctica parciales y usá apuntes de compañeros.",
            "recomendacion_texto": "Ver Plan A/B/C/D abajo",
            "reglas": {"max_qty": 4, "max_dificultad": 4},
            "planes": {
                "A": "Plan A (Ideal): 2 Muy Difícil + 2 Faciles. (Tu prioridad absoluta es estudiar, tenes tiempo, pero también lee durante tu viajes).",
                "B": "Plan B (No hay Normales): 1 Muy Difícil + 2 Difíciles. (Advertencia: Alto riesgo de saturación, aprovecha todos tus tiempos libres para estudiar).",
                "C": "Plan C (Solo Normales/Fáciles): 2 Normales + 2 Faciles. (Aprovechá para adelantar, pero ojo con coordinar grupos viviendo lejos).",
                "D": "Plan D (Solo Difíciles): 3 materias Difíciles. (Límite extremo: requiere una disciplina estricta de estudio diario)."
            }
        },
        "finales": {
            "comentario": "Organiza tus tiempos para poder rendir 2 materias en una misma mesa. Elige materias que no tengan fechas de exámenes cercanas. Organiza un grupo de estudio para que se apoyen entre todos. Intenta inscribirte a las materias que cursaste en ese año, es decir recién finalizadas. Siempre consultá a la cátedra sobre el formato del final.",
            "recomendacion_texto": "Ver Plan A/B abajo",
            "reglas": {"max_qty": 2, "min_dificultad": 1},
            "planes": {
                "A": "Plan A: 2 Finales (Cualquier tipo). (Al tener disponibilidad total, podés permitirte preparar dos temas en simultáneo).",
                "B": "Plan B: 1 Final (cualquier tipo). (Al tener disponibilidad total, podés permitirte prepararte para sacar buenas notas)."
            }
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