# backend/app/services/recomendacion_service.py

from rdflib import Graph
from app.models.user import User
from app.models.enums import CondicionLaboral
from app.core.perfiles_pdf import PERFILES_DATA, obtener_perfil_id

def _enriquecer_materias_usuario(materias_usuario, kg: Graph):
    """Añade dificultad y créditos a las materias que el usuario ya seleccionó."""
    uris = " ".join([f"<{m.materia_uri}>" for m in materias_usuario])
    if not uris: return []

    query = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?materia ?label ?valDificultad ?creditos
    WHERE {{
        VALUES ?materia {{ {uris} }}
        ?materia rdfs:label ?label .
        OPTIONAL {{ 
            ?materia fiunju:tieneDificultadCursada ?dif . 
            ?dif fiunju:tieneValor ?valDificultad . 
        }}
        OPTIONAL {{ ?materia fiunju:otorgaCreditos ?creditos . }}
    }}
    """
    results = kg.query(query)
    
    enriquecidas = []
    for row in results:
        uri = str(row.materia)
        # Encontrar el objeto UserMateria correspondiente para mantener el ID
        user_obj = next((m for m in materias_usuario if m.materia_uri == uri), None)
        if user_obj:
            enriquecidas.append({
                "uri": uri,
                "label": str(row.label),
                "dificultad": int(row.valDificultad) if row.valDificultad else 2, # Default Normal
                "creditos": int(row.creditos) if row.creditos else 0,
                "estado_actual": user_obj.estado
            })
    return enriquecidas

def _get_materias_habilitadas(user: User, kg: Graph) -> list[dict]:
    """
    Retorna las materias que el usuario puede cursar (prerrequisitos cumplidos)
    y calcula cuántas materias futuras desbloquea cada una.
    """
    # 1. Obtener todas las materias del grafo
    query_materias = """
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?materia ?label WHERE {
        ?materia a fiunju:Materia ;
                 rdfs:label ?label .
    }
    """
    all_materias = kg.query(query_materias)
    
    # 2. Identificar estado del usuario
    # Consideramos "aprobado" para correlativas si está Regular o Aprobada
    materias_aprobadas_uris = {
        m.materia_uri for m in user.materias_cursadas 
        if m.estado in ["Regular", "Aprobada", "PreparandoFinal"]
    }
    
    # Materias que ya está cursando o aprobó (no se las sugerimos de nuevo como "habilitadas" para cursar)
    materias_no_disponibles = {
        m.materia_uri for m in user.materias_cursadas
    }

    habilitadas = []

    for row in all_materias:
        m_uri = str(row.materia)
        m_label = str(row.label)

        if m_uri in materias_no_disponibles:
            continue

        # 3. Verificar Prerrequisitos
        # Obtenemos los requisitos directos de esta materia
        query_reqs = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT ?req WHERE {{
            <{m_uri}> fiunju:tieneRequisito ?req .
        }}
        """
        reqs = kg.query(query_reqs)
        cumple_requisitos = True
        for r in reqs:
            if str(r.req) not in materias_aprobadas_uris:
                cumple_requisitos = False
                break
        
        if cumple_requisitos:
            # 4. Calcular Impacto (Desbloquea Count)
            # Cuántas materias futuras tienen a esta como requisito (transitivo)
            # Usamos property path + para transitividad
            query_impacto = f"""
            PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
            SELECT (COUNT(?future) as ?count) WHERE {{
                ?future fiunju:tieneRequisito+ <{m_uri}> .
            }}
            """
            res_impacto = kg.query(query_impacto)
            impacto = 0
            for r_imp in res_impacto:
                impacto = int(r_imp["count"])

            habilitadas.append({
                "uri": m_uri,
                "label": m_label,
                "desbloquea_count": impacto
            })
            
    return habilitadas


def generar_plan_cursada_optimo(user: User, kg: Graph) -> dict:
    # 1. Identificar Perfil
    pid = obtener_perfil_id(user)
    perfil_data = PERFILES_DATA[pid]
    reglas = perfil_data["cursada"]["reglas"]
    
    # 2. Obtener materias que el usuario marcó como "Cursando"
    seleccion_usuario = [m for m in user.materias_cursadas if m.estado == "Cursando"]
    materias_data = _enriquecer_materias_usuario(seleccion_usuario, kg)
    
    # 3. Aplicar Lógica de Selección (Filtro)
    plan_sugerido = []
    omitidas = []
    
    # Ordenar por dificultad (ascendente por defecto para perfiles saturados)
    # Si el perfil prioriza dificiles, invertimos luego.
    materias_data.sort(key=lambda x: x["dificultad"])
    
    max_qty = reglas.get("max_qty", 5)
    
    # Lógica específica por perfil para filtrar la selección del usuario
    if pid == 1: # Perfil Crítico (Antes Superviviente)
        # Lógica Dinámica de Planes (A, B, C, D)
        faciles = [m for m in materias_data if m["dificultad"] == 1]
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = ""
        texto_plan = ""

        # Prioridad de Selección de Plan
        if len(faciles) >= 2:
            plan_seleccionado = "A"
            # Plan A: 2 Fáciles
            plan_sugerido.extend(faciles[:2])
            omitidas.extend(faciles[2:] + normales + dificiles + muy_dificiles)
        elif len(normales) >= 1:
            plan_seleccionado = "B"
            # Plan B: 1 Normal (y rellenar con 1 fácil si hubiera, aunque la regla dice "Solo hay normales")
            # La regla estricta dice "1 materia Normal".
            plan_sugerido.append(normales[0])
            omitidas.extend(faciles + normales[1:] + dificiles + muy_dificiles)
        elif len(dificiles) >= 1:
            plan_seleccionado = "C"
            # Plan C: 1 Difícil
            plan_sugerido.append(dificiles[0])
            omitidas.extend(faciles + normales + dificiles[1:] + muy_dificiles)
        elif len(muy_dificiles) >= 1:
            plan_seleccionado = "D"
            # Plan D: 1 Muy Difícil (o nada, pero sugerimos 1 con advertencia)
            plan_sugerido.append(muy_dificiles[0])
            omitidas.extend(faciles + normales + dificiles + muy_dificiles[1:])
        else:
            # Caso borde: No hay materias o algo raro
            plan_seleccionado = "A" # Default
        
        # Inyectar el texto del plan específico
        texto_plan = perfil_data["cursada"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")
        perfil_data["cursada"]["recomendacion_texto"] = texto_plan # Pisamos el texto genérico para este request
                
    elif pid == 3: # Perfil Medio-Bajo
        # Lógica Dinámica de Planes (A, B, C, D)
        faciles = [m for m in materias_data if m["dificultad"] == 1]
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = ""
        
        # Plan A: 1 Difícil + 2 Normal
        if len(dificiles) >= 1 and len(normales) >= 2:
            plan_seleccionado = "A"
            plan_sugerido.append(dificiles[0])
            plan_sugerido.extend(normales[:2])
            omitidas.extend(faciles + normales[2:] + dificiles[1:] + muy_dificiles)
        
        # Plan B: 3 Normales (No hay dificiles)
        elif len(normales) >= 3:
            plan_seleccionado = "B"
            plan_sugerido.extend(normales[:3])
            omitidas.extend(faciles + normales[3:] + dificiles + muy_dificiles)
            
        # Plan C: 2 Difíciles (Solo hay dificiles)
        elif len(dificiles) >= 2:
            plan_seleccionado = "C"
            plan_sugerido.extend(dificiles[:2])
            omitidas.extend(faciles + normales + dificiles[2:] + muy_dificiles)
            
        # Plan D: 1 Muy Difícil + 1 Fácil
        elif len(muy_dificiles) >= 1 and len(faciles) >= 1:
            plan_seleccionado = "D"
            plan_sugerido.append(muy_dificiles[0])
            plan_sugerido.append(faciles[0])
            omitidas.extend(faciles[1:] + normales + dificiles + muy_dificiles[1:])
            
        else:
            # Fallback
            plan_seleccionado = "A"
            if dificiles: plan_sugerido.append(dificiles[0])
            if normales: plan_sugerido.extend(normales[:2])
            
        texto_plan = perfil_data["cursada"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")

    elif pid in [4, 5, 6, 7]: # Perfiles con capacidad media/alta
        # Intentamos meter las difíciles primero si el perfil lo sugiere
        # Reordenamos: Primero Muy Difíciles, luego Difíciles, luego Normales
        materias_data.sort(key=lambda x: x["dificultad"], reverse=True)
        
        for m in materias_data:
            if len(plan_sugerido) < max_qty:
                plan_sugerido.append(m)
            else:
                omitidas.append(m)
    
    elif pid == 2: # Perfil Bajo
        # Lógica Dinámica de Planes (A, B, C, D)
        faciles = [m for m in materias_data if m["dificultad"] == 1]
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = ""
        texto_plan = ""

        # Prioridad de Selección de Plan
        # Plan A: 2 Fáciles (Ideal)
        if len(faciles) >= 2:
            plan_seleccionado = "A"
            plan_sugerido.extend(faciles[:2])
            omitidas.extend(faciles[2:] + normales + dificiles + muy_dificiles)
        
        # Plan B: 2 Normales (Si no hay fáciles)
        elif len(normales) >= 2:
            plan_seleccionado = "B"
            plan_sugerido.extend(normales[:2])
            omitidas.extend(faciles + normales[2:] + dificiles + muy_dificiles)
            
        # Plan C: 1 Difícil (Si solo hay difíciles)
        elif len(dificiles) >= 1:
            plan_seleccionado = "C"
            plan_sugerido.append(dificiles[0])
            omitidas.extend(faciles + normales + dificiles[1:] + muy_dificiles)
            
        # Plan D: 1 Muy Difícil (Si solo hay muy difíciles)
        elif len(muy_dificiles) >= 1:
            plan_seleccionado = "D"
            plan_sugerido.append(muy_dificiles[0])
            omitidas.extend(faciles + normales + dificiles + muy_dificiles[1:])
            
        else:
            # Fallback si no encaja en ninguno (ej: 1 normal y 1 facil pero no 2 faciles)
            # El usuario pide 2 Faciles para Plan A. Si hay 1 normal y 1 facil, no encaja en A ni B.
            # Asumimos Plan A "relajado" o lo que mejor encaje.
            plan_seleccionado = "A"
            if faciles: plan_sugerido.append(faciles[0])
            if normales: plan_sugerido.append(normales[0])
            
        texto_plan = perfil_data["cursada"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")
        # perfil_data["cursada"]["recomendacion_texto"] = texto_plan # Avoid modifying global state

    else: # Default: Balanceado
        # Buscamos 1 facil y 1 normal primero
        faciles = [m for m in materias_data if m["dificultad"] == 1]
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] >= 3]
        
        # Llenar slots
        current_count = 0
        
        # Prioridad perfil 2: Normal + Facil
        if normales and current_count < max_qty: 
            plan_sugerido.append(normales.pop(0)); current_count+=1
        if faciles and current_count < max_qty: 
            plan_sugerido.append(faciles.pop(0)); current_count+=1
            
        # Relleno (si el usuario seleccionó otras cosas y sobra espacio)
        restantes = faciles + normales + dificiles
        for m in restantes:
            if current_count < max_qty:
                plan_sugerido.append(m)
                current_count += 1
            else:
                omitidas.append(m)
        
        # Default text if not Profile 1 or 2
        texto_plan = perfil_data["cursada"]["recomendacion_texto"]

    # Estructura de respuesta para el Frontend
    return {
        "plan_recomendado": [{
            "uri": m["uri"], "label": m["label"], "score": 1.0, "año": 0, 
            "dificultad": m["dificultad"], "desbloquea_count": 0, "creditos_otorgados": m["creditos"]
        } for m in plan_sugerido],
        
        "materias_omitidas": [{
            "uri": m["uri"], "label": m["label"], "score": 0.0, "año": 0, 
            "dificultad": m["dificultad"], "desbloquea_count": 0
        } for m in omitidas],
        
        "arquetipo": {
            "nombre": perfil_data["nombre_corto"], # Ej: "El Guerrero Solitario"
            "color": perfil_data["color"],         # Ej: "#eab308"
            "consejos": [perfil_data["cursada"]["comentario"]]
        },
        # Enviamos el texto de recomendación crudo, el frontend lo formateará
        "consejos_adicionales": [texto_plan]
    }

def generar_estrategia_examenes(user: User, kg: Graph) -> dict:
    # 1. Identificar Perfil y Reglas de Finales
    pid = obtener_perfil_id(user)
    perfil_data = PERFILES_DATA[pid]
    reglas = perfil_data["finales"]["reglas"]
    
    # 2. Obtener finales seleccionados ("PreparandoFinal")
    seleccion_usuario = [m for m in user.materias_cursadas if m.estado == "PreparandoFinal"]
    
    uris = " ".join([f"<{m.materia_uri}>" for m in seleccion_usuario])
    materias_data = []
    
    if uris:
        query = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?materia ?label ?valDificultad ?labelDificultad ?labelModalidad
        WHERE {{
            VALUES ?materia {{ {uris} }}
            ?materia rdfs:label ?label .
            OPTIONAL {{ 
                ?materia fiunju:tieneModalidadExamen ?mod .
                ?mod rdfs:label ?labelModalidad .
                ?mod fiunju:tieneDificultadExamen ?dif .
                ?dif fiunju:tieneValor ?valDificultad .
                ?dif rdfs:label ?labelDificultad .
            }}
        }}
        """
        results = kg.query(query)
        
        temp_map = {} 
        for row in results:
            uri = str(row.materia)
            dif = int(row.valDificultad) if row.valDificultad else 2
            label_dif = str(row.labelDificultad) if row.labelDificultad else "Normal"
            mod = str(row.labelModalidad) if row.labelModalidad else "Estándar"
            
            if uri not in temp_map:
                temp_map[uri] = {
                    "uri": uri, 
                    "label": str(row.label), 
                    "dificultad": dif,
                    "dificultad_label": label_dif,
                    "modalidades": {mod}
                }
            else:
                # Si tiene varias modalidades, nos quedamos con la más difícil para el cálculo
                if dif > temp_map[uri]["dificultad"]:
                    temp_map[uri]["dificultad"] = dif
                    temp_map[uri]["dificultad_label"] = label_dif
                temp_map[uri]["modalidades"].add(mod)
        
        materias_data = list(temp_map.values())

    # 3. Filtrar/Priorizar según reglas PDF
    recomendados = []
    otros = []
    
    # Ordenamos base por dificultad
    materias_data.sort(key=lambda x: x["dificultad"]) 
    
    max_qty = reglas.get("max_qty", 5)
    
    # Lógica específica de selección (Espejo de lógica de cursada pero para finales)
    # Lógica específica de selección (Espejo de lógica de cursada pero para finales)
    # Lógica específica de selección (Espejo de lógica de cursada pero para finales)
    texto_plan_final = perfil_data["finales"]["recomendacion_texto"]
    
    if pid == 1: # Superviviente / Crítico
        # 1. Determinar Plan (A, B, C) basado en disponibilidad TOTAL
        # Plan A: Normal (2)
        # Plan B: Dificil (3)
        # Plan C: Muy Dificil (4)
        
        hay_normales = any(m["dificultad"] == 2 for m in materias_data)
        hay_dificiles = any(m["dificultad"] == 3 for m in materias_data)
        hay_muy_dificiles = any(m["dificultad"] >= 4 for m in materias_data)
        
        plan_seleccionado = "A" # Default
        texto_plan_final = "Plan A: 1 Final Normal. (Ideal para mantener la constancia sin saturarte)."
        
        if hay_normales:
            plan_seleccionado = "A"
            texto_plan_final = "Plan A: 1 Final Normal. (Ideal para mantener la constancia sin saturarte)."
        elif hay_dificiles:
            plan_seleccionado = "B"
            texto_plan_final = "Plan B: 1 Final Difícil. (Advertencia: Preparalo con tiempo, tus bloques de estudio son cortos y fragmentados)."
        elif hay_muy_dificiles:
            plan_seleccionado = "C"
            texto_plan_final = "Plan C: 1 Final Muy Difícil. No rendir finales complejos mientras se cursa. Postergar para fechas sin cursada."

        # 2. Filtrar Recomendados según el Plan
        for m in materias_data:
            agregada = False
            if plan_seleccionado == "A":
                # Plan A: 1 Normal
                if m["dificultad"] == 2 and len(recomendados) < 1:
                    recomendados.append(m)
                    agregada = True
            elif plan_seleccionado == "B":
                # Plan B: 1 Difícil
                if m["dificultad"] == 3 and len(recomendados) < 1:
                    recomendados.append(m)
                    agregada = True
            elif plan_seleccionado == "C":
                # Plan C: 1 Muy Difícil
                if m["dificultad"] >= 4 and len(recomendados) < 1:
                    recomendados.append(m)
                    agregada = True
            
            if not agregada:
                otros.append(m)

    elif pid == 2: # Perfil Bajo
        # Plan A: 1 Normal + 1 Difícil
        # Plan B: 1 Difícil
        # Plan C: 2 Difíciles
        # Plan D: 1 Muy Difícil

        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = "A" # Default
        texto_plan_final = ""

        # Lógica de selección
        if len(normales) >= 1 and len(dificiles) >= 1:
            plan_seleccionado = "A"
            recomendados.append(normales[0])
            recomendados.append(dificiles[0])
            otros.extend(normales[1:] + dificiles[1:] + muy_dificiles)
        elif len(dificiles) >= 2:
             # Plan C: 2 Difíciles
             plan_seleccionado = "C"
             recomendados.extend(dificiles[:2])
             otros.extend(normales + dificiles[2:] + muy_dificiles)
        elif len(dificiles) >= 1:
             # Plan B: 1 Difícil
             plan_seleccionado = "B"
             recomendados.append(dificiles[0])
             otros.extend(normales + dificiles[1:] + muy_dificiles)
        elif len(muy_dificiles) >= 1:
             # Plan D: 1 Muy Difícil
             plan_seleccionado = "D"
             recomendados.append(muy_dificiles[0])
             otros.extend(normales + dificiles + muy_dificiles[1:])
        else:
             # Fallback (ej: solo normales)
             plan_seleccionado = "A"
             if normales: recomendados.append(normales[0])
             elif dificiles: recomendados.append(dificiles[0])
             elif muy_dificiles: recomendados.append(muy_dificiles[0])
        
        texto_plan_final = perfil_data["finales"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")
                
    elif pid == 3: # Perfil Medio-Bajo
        # Plan A: 1 Final Difícil
        # Plan B: 2 Finales Normales
        # Plan C: 1 Muy Difícil

        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = "A" # Default
        
        if len(dificiles) >= 1:
            plan_seleccionado = "A"
            recomendados.append(dificiles[0])
            otros.extend(normales + dificiles[1:] + muy_dificiles)
        elif len(normales) >= 2:
            plan_seleccionado = "B"
            recomendados.extend(normales[:2])
            otros.extend(normales[2:] + dificiles + muy_dificiles)
        elif len(muy_dificiles) >= 1:
            plan_seleccionado = "C"
            recomendados.append(muy_dificiles[0])
            otros.extend(normales + dificiles + muy_dificiles[1:])
        else:
            # Fallback
            plan_seleccionado = "A"
            if dificiles: recomendados.append(dificiles[0])
            elif normales: recomendados.extend(normales[:2])
            elif muy_dificiles: recomendados.append(muy_dificiles[0])
            
        texto_plan_final = perfil_data["finales"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")

    elif pid in [4]: # Priorizar la más difícil primero
        materias_data.sort(key=lambda x: x["dificultad"], reverse=True)
        # Tomar la primera difícil
        if materias_data:
            recomendados.append(materias_data[0])
            # El resto a "otros" si excede max_qty o si la estrategia es solo 1
            resto = materias_data[1:]
            if len(recomendados) < max_qty:
                 # Si el perfil permite más de 1, rellenamos con las siguientes
                 cupo_restante = max_qty - len(recomendados)
                 recomendados.extend(resto[:cupo_restante])
                 otros.extend(resto[cupo_restante:])
            else:
                 otros.extend(resto)
                 
    else: # Balanceado / Heredero (Llenar cupo)
        # Heredero (Perfil 6) o Equilibrado: puede rendir varias.
        # Ordenamos por dificultad descendente para aprovechar capacidad
        if pid in [6]: 
             materias_data.sort(key=lambda x: x["dificultad"], reverse=True)
        
        for m in materias_data:
            if len(recomendados) < max_qty:
                recomendados.append(m)
            else:
                otros.append(m)

    # 4. Formatear respuesta
    plan_final = []
    
    def map_to_output(m_list, habilitada, motivo=None):
        res = []
        for m in m_list:
            res.append({
                "uri": m["uri"],
                "label": m["label"],
                "dificultad_examen_label": m["dificultad_label"],
                "dificultad_examen_valor": m["dificultad"],
                "modalidades": list(m["modalidades"]),
                "esta_habilitada": habilitada,
                "motivo_bloqueo": motivo,
                "correlativas_pendientes": [],
                "consejo_personalizado": "Recomendado por tu perfil" if habilitada else "Excede la recomendación de tu perfil"
            })
        return res

    plan_final.extend(map_to_output(recomendados, True))
    plan_final.extend(map_to_output(otros, False, motivo="No recomendado por carga horaria"))



    return {
        "plan_recomendado": plan_final,
        # Inyección del Arquetipo (Igual que en Cursada)
        "arquetipo": {
            "nombre": perfil_data["nombre_corto"],
            "color": perfil_data["color"],
            "consejos": [perfil_data["cursada"]["comentario"]] # Usamos el comentario de cursada como "Diagnóstico" general
        },
        # Texto de recomendación técnica del PDF
        "consejos_adicionales": [
            texto_plan_final, # El plan seleccionado (A, B o C)
            perfil_data["finales"]["comentario"] # El "Consejo Clave"
        ]
    }