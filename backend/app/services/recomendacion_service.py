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
    Retorna las materias que el usuario puede cursar mediante una query SPARQL optimizada.
    Filtra por:
    - Prerrequisitos (FILTER NOT EXISTS de requisitos no aprobados)
    - Créditos requeridos
    - Requisito de 4to año aprobado
    - Excluye materias ya aprobadas/regularizadas/cursando
    """
    
    # 1. Preparar datos del usuario para la query
    # Materias Aprobadas/Regularizadas (cumplen requisitos)
    materias_aprobadas_uris = [
        f"<{m.materia_uri}>" for m in user.materias_cursadas 
        if m.estado in ["Regular", "Aprobada", "PreparandoFinal"]
    ]
    str_aprobadas = ", ".join(materias_aprobadas_uris)
    
    # Materias que NO se deben sugerir (ya las tiene o las está cursando)
    # Incluimos Cursando, Regular, Aprobada, PreparandoFinal
    materias_no_sugeribles = [
        f"<{m.materia_uri}>" for m in user.materias_cursadas
        if m.estado in ["Cursando", "Regular", "Aprobada", "PreparandoFinal"]
    ]
    str_no_sugeribles = ", ".join(materias_no_sugeribles)

    # Datos numéricos/booleanos
    # Calcular créditos del usuario consultando la ontología
    creditos_usuario = 0
    if materias_aprobadas_uris:
        uris_for_query = " ".join(materias_aprobadas_uris)
        query_creditos = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT (SUM(?creditos) as ?total) WHERE {{
            VALUES ?materia {{ {uris_for_query} }}
            ?materia fiunju:otorgaCreditos ?creditos .
        }}
        """
        try:
            res_cred = kg.query(query_creditos)
            for row in res_cred:
                if row.total:
                    creditos_usuario = int(row.total)
        except Exception:
            creditos_usuario = 0

    # Determinar si tiene 4to año aprobado (Simplificado: False por defecto o lógica futura)
    # Por ahora asumimos False para evitar errores si no está calculado
    tiene_cuarto = "false" 
    # Si quisieramos calcularlo real, deberíamos chequear todas las de 4to.


    # 2. Query SPARQL Definitiva
    query = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?materia ?label ?dificultad ?creditos (COUNT(?future) as ?impacto)
    WHERE {{
        ?materia a fiunju:Materia ;
                 rdfs:label ?label .
        
        # Excluir materias que el usuario ya tiene/cursa
        FILTER (?materia NOT IN ({str_no_sugeribles}))

        # Filtro de Prerrequisitos: 
        # No debe existir un requisito R tal que R NO esté en la lista de aprobadas
        FILTER NOT EXISTS {{
            ?materia fiunju:tieneRequisito ?req .
            FILTER (?req NOT IN ({str_aprobadas}))
        }}

        # Filtro de Créditos
        OPTIONAL {{ ?materia fiunju:requiereCreditos ?reqCred . }}
        FILTER (!BOUND(?reqCred) || ?reqCred <= {creditos_usuario})

        # Filtro de 4to Año
        OPTIONAL {{ ?materia fiunju:requiereCuartoAnoAprobado ?reqCuarto . }}
        FILTER (!BOUND(?reqCuarto) || ?reqCuarto = {tiene_cuarto} || {tiene_cuarto} = true)

        # Datos extra
        OPTIONAL {{ 
            ?materia fiunju:tieneDificultadCursada ?difNode .
            ?difNode fiunju:tieneValor ?dificultad .
        }}
        OPTIONAL {{ ?materia fiunju:otorgaCreditos ?creditos . }}

        # Cálculo de Impacto (Subquery implícita con group by)
        OPTIONAL {{ ?future fiunju:tieneRequisito+ ?materia . }}
    }}
    GROUP BY ?materia ?label ?dificultad ?creditos
    """
    
    results = kg.query(query)
    
    habilitadas = []
    for row in results:
        habilitadas.append({
            "uri": str(row.materia),
            "label": str(row.label),
            "dificultad": int(row.dificultad) if row.dificultad else 2, # Default Normal
            "creditos": int(row.creditos) if row.creditos else 0,
            "desbloquea_count": int(row.impacto)
        })
            
    return habilitadas


def generar_plan_cursada_optimo(user: User, kg: Graph) -> dict:
    # 1. Identificar Perfil y obtener sus datos básicos
    pid = obtener_perfil_id(user)
    perfil_data = PERFILES_DATA[pid]
    
    # 2. Obtener Materias Habilitadas (Query SPARQL optimizada)
    materias_habilitadas = _get_materias_habilitadas(user, kg)
    
    # Ordenar pool inicial por impacto (desbloquea_count) descendente y luego dificultad ascendente
    # Esto ayuda al fallback
    materias_habilitadas.sort(key=lambda x: (-x["desbloquea_count"], x["dificultad"]))

    # 3. Obtener Estrategias del Arquetipo desde la Ontología
    # Mapeo de ID de perfil a URI de arquetipo (Hardcodeo mínimo necesario o query inversa)
    # Asumimos que podemos construir la URI del arquetipo o buscarla por nombre
    # Para simplificar, usaremos una query que busque por nombre del arquetipo o ID si lo tuviéramos en la ontología
    # Como no guardamos el ID numérico en la ontología, usaremos el nombre del perfil_data
    nombre_arquetipo = perfil_data["nombre_corto"] # Ej "Perfil Crítico"
    
    query_estrategias = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?orden ?desc ?cant ?minReq ?difValor
    WHERE {{
        ?arquetipo a fiunju:ArquetipoEstudiante ;
                   fiunju:tieneNombreArquetipo ?nombre ;
                   fiunju:tieneEstrategiaPosible ?est .
        
        FILTER (STR(?nombre) = "{nombre_arquetipo}")
        
        ?est fiunju:ordenPrioridad ?orden ;
             fiunju:descripcionPlan ?desc ;
             fiunju:cantidadMaterias ?cant ;
             fiunju:cantidadMinimaRequerida ?minReq .
             
        OPTIONAL {{ 
            ?est fiunju:requiereDisponibilidadDe ?difNode .
            ?difNode fiunju:tieneValor ?difValor .
        }}
    }}
    ORDER BY ?orden
    """
    estrategias_res = kg.query(query_estrategias)
    
    plan_seleccionado = []
    omitidas = []
    texto_recomendacion = "No se encontró una estrategia específica, mostrando mejores opciones disponibles."
    
    estrategia_encontrada = False
    
    # 4. Evaluar Estrategias en orden
    for row in estrategias_res:
        if estrategia_encontrada: break
        
        desc = str(row.desc)
        cant_a_sugerir = int(row.cant)
        min_req = int(row.minReq)
        dificultad_req = int(row.difValor) if row.difValor else None
        
        # Filtrar materias que cumplen con el requisito de dificultad de la estrategia
        candidatas = []
        if dificultad_req is not None:
            candidatas = [m for m in materias_habilitadas if m["dificultad"] == dificultad_req]
        else:
            # Si no pide dificultad específica (ej. "Variadas"), usamos todas
            candidatas = materias_habilitadas
            
        # Verificar si cumplimos la cantidad mínima requerida para activar este plan
        if len(candidatas) >= min_req:
            estrategia_encontrada = True
            texto_recomendacion = desc
            
            # Seleccionar las materias para el plan
            # Si la estrategia pide X materias de dificultad Y, tomamos esas.
            # Si sobran slots (cant_a_sugerir > len(candidatas)), rellenamos con otras?
            # Por simplicidad del modelo actual: Tomamos las candidatas hasta llenar el cupo.
            # Si la estrategia es "2 Faciles" y cant=2, tomamos 2 faciles.
            # Si la estrategia es "1 Dificil + 2 Normales", esto requiere estrategias compuestas que simplificamos en la ontología.
            # En la ontología simplificada, definimos el requisito "Principal". 
            # El motor genérico tomará las candidatas principales y rellenará con el resto de habilitadas (ordenadas por impacto).
            
            seleccion = candidatas[:cant_a_sugerir]
            plan_seleccionado.extend(seleccion)
            
            # Relleno si falta para llegar a cant_a_sugerir
            if len(plan_seleccionado) < cant_a_sugerir:
                faltantes = cant_a_sugerir - len(plan_seleccionado)
                # Buscar en el resto de habilitadas que no estén ya seleccionadas
                uris_sel = {m["uri"] for m in plan_seleccionado}
                resto = [m for m in materias_habilitadas if m["uri"] not in uris_sel]
                plan_seleccionado.extend(resto[:faltantes])
            
            # Identificar omitidas
            uris_sel = {m["uri"] for m in plan_seleccionado}
            omitidas = [m for m in materias_habilitadas if m["uri"] not in uris_sel]

    # 5. Fallback si ninguna estrategia coincide
    if not estrategia_encontrada:
        # Tomar las top N por impacto/dificultad (ya ordenadas)
        default_qty = 3
        plan_seleccionado = materias_habilitadas[:default_qty]
        omitidas = materias_habilitadas[default_qty:]
        texto_recomendacion = "Plan Genérico: Basado en las materias que desbloquean más correlativas."

    # 6. Formatear respuesta
    return {
        "plan_recomendado": [{
            "uri": m["uri"], "label": m["label"], "score": 1.0, "año": 0, 
            "dificultad": m["dificultad"], "desbloquea_count": m["desbloquea_count"], "creditos_otorgados": m["creditos"]
        } for m in plan_seleccionado],
        
        "materias_omitidas": [{
            "uri": m["uri"], "label": m["label"], "score": 0.0, "año": 0, 
            "dificultad": m["dificultad"], "desbloquea_count": m["desbloquea_count"]
        } for m in omitidas],
        
        "arquetipo": {
            "nombre": perfil_data["nombre_corto"],
            "color": perfil_data["color"],
            "consejos": [perfil_data["cursada"]["comentario"]]
        },
        "consejos_adicionales": [texto_recomendacion]
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

    elif pid == 4: # Perfil Equilibrado
        # Plan A: 1 Muy Difícil + 1 Normal
        # Plan C: 2 Difíciles
        
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = "A" # Default
        
        if len(muy_dificiles) >= 1 and len(normales) >= 1:
            plan_seleccionado = "A"
            recomendados.append(muy_dificiles[0])
            recomendados.append(normales[0])
            otros.extend(normales[1:] + dificiles + muy_dificiles[1:])
        elif len(dificiles) >= 2:
            plan_seleccionado = "C"
            recomendados.extend(dificiles[:2])
            otros.extend(normales + dificiles[2:] + muy_dificiles)
        else:
             # Fallback
            plan_seleccionado = "A"
            if muy_dificiles: recomendados.append(muy_dificiles[0])
            if normales: recomendados.append(normales[0])
            
        texto_plan_final = perfil_data["finales"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")

    elif pid == 5: # Perfil Medio-Alto
        # Plan A: 2 Finales (Cualquier tipo)
        # Plan B: 1 Final (Cualquier tipo)
        
        # Simplemente tomamos las 2 primeras disponibles, priorizando las que ya están listas
        todas_disponibles = materias_data # Ya vienen filtradas por estado? No, materias_data son todas las del usuario enriquecidas?
        # No, materias_data en generar_estrategia_examenes son las "PreparandoFinal" enriquecidas.
        
        # Ordenamos por dificultad descendente para "Cualquier tipo" (o ascendente? El usuario dice "Cualquier tipo").
        # Vamos a priorizar variedad o simplemente cantidad. Plan A dice 2.
        
        plan_seleccionado = "A"
        
        if len(materias_data) >= 2:
            plan_seleccionado = "A"
            recomendados.extend(materias_data[:2])
            otros.extend(materias_data[2:])
        elif len(materias_data) == 1:
            plan_seleccionado = "B"
            recomendados.append(materias_data[0])
        else:
            plan_seleccionado = "B" # Fallback
            
        texto_plan_final = perfil_data["finales"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")

    elif pid == 6: # Perfil Super Alto
        # Plan A: 2 Finales (Cualquier tipo)
        # Plan B: 2 Difíciles + 1 Normal
        # Plan C: 3 materias Normales
        
        normales = [m for m in materias_data if m["dificultad"] == 2]
        dificiles = [m for m in materias_data if m["dificultad"] == 3]
        muy_dificiles = [m for m in materias_data if m["dificultad"] >= 4]

        plan_seleccionado = "A" # Default
        
        # Plan B: 2 Difíciles + 1 Normal
        if len(dificiles) >= 2 and len(normales) >= 1:
            plan_seleccionado = "B"
            recomendados.extend(dificiles[:2])
            recomendados.append(normales[0])
            otros.extend(normales[1:] + dificiles[2:] + muy_dificiles)
            
        # Plan C: 3 materias Normales
        elif len(normales) >= 3:
            plan_seleccionado = "C"
            recomendados.extend(normales[:3])
            otros.extend(normales[3:] + dificiles + muy_dificiles)
            
        # Plan A: 2 Finales (Cualquier tipo) - Fallback logic
        else:
            plan_seleccionado = "A"
            # Tomamos las 2 primeras disponibles (ya ordenadas por dificultad o como vengan)
            if len(materias_data) >= 2:
                recomendados.extend(materias_data[:2])
                otros.extend(materias_data[2:])
            elif materias_data:
                recomendados.extend(materias_data)
            
        texto_plan_final = perfil_data["finales"].get("planes", {}).get(plan_seleccionado, "Plan no determinado.")


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