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

DIAGNOSTICOS_HARDCODED = {
    "ArquetipoCritico": "Tu perfil tiene 'muy poco tiempo para estudiar'. No se permiten errores.\n* trabajas tiempo completo\n* Vivis lejos\n* vivis solo\n* tenes hijo/s",
    "ArquetipoBajo": "Tiene un poco más de tiempo gracias al apoyo familiar y vivir cerca.\n* trabajas tiempo completo\n* Vivis en Capital\n* No vives solo\n* tenes hijo/s",
    "ArquetipoMedioBajo": "Tiene tiempo, pero viajar largas distancias más las tareas domésticas te quitan energía.\n* trabajas medio tiempo\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s",
    "ArquetipoEquilibrado": "Es el balance perfecto. Puede asumir carga, pero no extrema.\n* trabajas medio tiempo\n* Vivis en Capital\n* No vivis solo\n* No tenes hijo/s",
    "ArquetipoMedioAlto": "Tiempo completo, pero vivir solo viene con tareas domésticas y viajar limita la 'energía mental'.\n* No trabajas\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s",
    "ArquetipoSuperAlto": "Disponibilidad total. Su única restricción es su propia capacidad de concentración.\n* No trabajas\n* Vivis en Capital\n* No vivis solo\n* No tenes hijo/s",
    "ArquetipoAtipico": "Tiempo libre de trabajo, pero al tener hijos perdes el 'flujo' de estudio constante.\n* No trabajas\n* Vivis en Capital\n* No vivis solo\n* Tenes hijo/s"
}

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
    # IMPORTANTE: Si el usuario marca "Cursando", queremos que el sistema las considere como "Candidatas Preferidas"
    # para el plan, NO que las oculte. El Plan Cursada es para el cuatrimestre actual.
    # Por lo tanto, solo excluimos Aprobada, Regular, PreparandoFinal.
    # "Cursando" se deja pasar para ser priorizada.
    
    materias_no_sugeribles = [
        f"<{m.materia_uri}>" for m in user.materias_cursadas
        if m.estado in ["Regular", "Aprobada", "PreparandoFinal"]
    ]
    str_no_sugeribles = ", ".join(materias_no_sugeribles)

    # Identificar URIs que el usuario YA eligió ("Cursando") para priorizarlas
    uris_cursando = {m.materia_uri for m in user.materias_cursadas if m.estado == "Cursando"}

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
    tiene_cuarto = "false" 

    # 2. Query SPARQL Definitiva
    query = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?materia ?label ?dificultad ?creditos ?anio ?caracter (COUNT(?future) as ?impacto)
    WHERE {{
        ?materia a fiunju:Materia ;
                 rdfs:label ?label .
        
        # Excluir materias que el usuario ya tiene aprobadas/regularizadas
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
        OPTIONAL {{ ?materia fiunju:anioPlan ?anio . }}
        OPTIONAL {{ ?materia fiunju:caracter ?caracter . }}

        # Cálculo de Impacto (Subquery implícita con group by)
        OPTIONAL {{ ?future fiunju:tieneRequisito+ ?materia . }}
    }}
    GROUP BY ?materia ?label ?dificultad ?creditos ?anio ?caracter
    """
    
    results = kg.query(query)
    
    habilitadas = []
    for row in results:
        uri = str(row.materia)
        es_cursando = uri in uris_cursando
        es_obligatoria = str(row.caracter) == "Obligatoria" if row.caracter else True # Default True
        
        habilitadas.append({
            "uri": uri,
            "label": str(row.label),
            "dificultad": int(row.dificultad) if row.dificultad else 2, # Default Normal
            "creditos": int(row.creditos) if row.creditos else 0,
            "desbloquea_count": int(row.impacto),
            "anio": int(row.anio) if row.anio else 0,
            "es_obligatoria": es_obligatoria,
            "es_cursando": es_cursando # Flag de preferencia de usuario
        })
            
    return habilitadas


def generar_plan_cursada_optimo(user: User, kg: Graph) -> dict:
    # 1. Identificar Perfil y obtener sus datos básicos
    pid = obtener_perfil_id(user)
    perfil_data = PERFILES_DATA[pid]
    
    # 2. Obtener Materias Habilitadas (Query SPARQL optimizada)
    materias_habilitadas = _get_materias_habilitadas(user, kg)

    # Identificar URIs que el usuario YA eligió ("Cursando") para priorizarlas y usarlas en la estrategia
    uris_cursando = {m.materia_uri for m in user.materias_cursadas if m.estado == "Cursando"}
    
    # Ordenar pool inicial
    # Prioridad:
    # 1. User Preference (es_cursando=True)
    # 2. Obligatoria (True)
    # 3. Impacto (desbloquea_count DESC)
    # 4. Dificultad (ASC) - Preferimos fáciles primero si todo lo demás es igual
    materias_habilitadas.sort(key=lambda x: (
        not x["es_cursando"], # False < True, so True comes first
        not x["es_obligatoria"], 
        -x["desbloquea_count"], 
        x["dificultad"]
    ))

    # 3. Obtener Estrategias del Arquetipo desde la Ontología
    # Usamos mapeo directo de ID a URI para mayor robustez
    ARQUETIPO_URIS = {
        1: "ArquetipoCritico",
        2: "ArquetipoBajo",
        3: "ArquetipoMedioBajo",
        4: "ArquetipoEquilibrado",
        5: "ArquetipoMedioAlto",
        6: "ArquetipoSuperAlto",
        7: "ArquetipoAtipico"
    }
    arquetipo_uri = ARQUETIPO_URIS.get(pid, "ArquetipoEquilibrado")
    
    query_estrategias = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?orden ?desc ?cant ?minReq ?difValor ?difValor2 ?difValor3 ?cantReq2 ?cantReq3
    WHERE {{
        fiunju:{arquetipo_uri} fiunju:tieneEstrategiaPosible ?est .
        
        ?est fiunju:ordenPrioridad ?orden ;
             fiunju:descripcionPlan ?desc ;
             fiunju:cantidadMaterias ?cant ;
             fiunju:cantidadMinimaRequerida ?minReq .
             
        # Primer requisito de dificultad (OPCIONAL - para planes flexibles)
        OPTIONAL {{ 
            ?est fiunju:requiereDisponibilidadDe ?difNode .
            ?difNode fiunju:tieneValor ?difValor .
        }}
        
        # Segundo requisito de dificultad (OPCIONAL)
        OPTIONAL {{
            ?est fiunju:requiereDisponibilidadDe2 ?difNode2 .
            ?difNode2 fiunju:tieneValor ?difValor2 .
            ?est fiunju:cantidadRequerida2 ?cantReq2 .
        }}
        
        # Tercer requisito de dificultad (OPCIONAL)
        OPTIONAL {{
            ?est fiunju:requiereDisponibilidadDe3 ?difNode3 .
            ?difNode3 fiunju:tieneValor ?difValor3 .
            ?est fiunju:cantidadRequerida3 ?cantReq3 .
        }}
    }}
    ORDER BY ?orden
    """
    results = kg.query(query_estrategias)
    
    plan_seleccionado = []
    omitidas = []
    texto_recomendacion = "No se encontró una estrategia específica, mostrando mejores opciones disponibles."
    
    # Fetch diagnostic card and key advice from ontology (DECOUPLED)
    tarjeta_diagnostico = "Diagnóstico no disponible."
    consejo_clave = "Consejo no disponible."
    
    try:
        query_info = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT ?diagnostico ?consejo WHERE {{
            OPTIONAL {{ fiunju:{arquetipo_uri} fiunju:tieneTarjetaDiagnostico ?diagnostico . }}
            OPTIONAL {{ fiunju:{arquetipo_uri} fiunju:tieneConsejoClave ?consejo . }}
        }}
        """
        res_info = list(kg.query(query_info))
        if res_info:
            if res_info[0].diagnostico:
                tarjeta_diagnostico = str(res_info[0].diagnostico)
            if res_info[0].consejo:
                consejo_clave = str(res_info[0].consejo)
    except Exception as e:
        print(f"Error fetching archetype info: {e}")

    # Fallback Hardcoded para Diagnóstico (MÁS AGRESIVO)
    print(f"DEBUG: Diagnostico recuperado de ontologia: '{tarjeta_diagnostico}'")
    # Usar fallback si está vacío, es None, o es el mensaje por defecto
    if not tarjeta_diagnostico or tarjeta_diagnostico.strip() == "" or tarjeta_diagnostico == "Diagnóstico no disponible." or "DEBUG" in tarjeta_diagnostico:
        tarjeta_diagnostico = DIAGNOSTICOS_HARDCODED.get(arquetipo_uri, "Diagnóstico no disponible.")
        print(f"DEBUG: Usando fallback hardcoded para {arquetipo_uri}: '{tarjeta_diagnostico[:50]}...'")
    else:
        print(f"DEBUG: Usando diagnóstico de ontología: '{tarjeta_diagnostico[:50]}...'")
    
    estrategia_encontrada = False
    
    # 4. Evaluar Estrategias
    # Si el usuario ya seleccionó materias ("Cursando"), buscamos la estrategia que MEJOR se ajuste a su selección.
    # Si no, usamos el orden de prioridad por defecto.
    
    # Analizar selección del usuario
    user_selection_counts = {4: 0, 3: 0, 2: 0, 1: 0}
    if uris_cursando:
        print(f"DEBUG: Usuario seleccionó {len(uris_cursando)} materias para cursar")
        for m in materias_habilitadas:
            if m["uri"] in uris_cursando:
                d = m["dificultad"]
                print(f"DEBUG: Materia seleccionada: {m['label']} - Dificultad: {d}")
                if d in user_selection_counts:
                    user_selection_counts[d] += 1
                elif d >= 4:
                    user_selection_counts[4] += 1
        print(f"DEBUG: user_selection_counts = {user_selection_counts}")

    estrategias_validas = []
    print(f"DEBUG: Evaluando estrategias para arquetipo {arquetipo_uri}")
    for row in results:
        desc = str(row.desc)
        cant_a_sugerir = int(row.cant)
        
        # Construir lista de requisitos de dificultad
        requisitos_dificultad = []
        
        # Primer requisito
        dificultad_req = None # Initialize for the 'if dificultad_req is not None' later
        min_req = int(row.minReq) # Always define min_req from the first requirement
        if row.difValor:
            dificultad_req = int(row.difValor)
            requisitos_dificultad.append((dificultad_req, min_req))
        
        # Segundo requisito
        if row.difValor2 and row.cantReq2:
            dificultad_req2 = int(row.difValor2)
            cant_req2 = int(row.cantReq2)
            requisitos_dificultad.append((dificultad_req2, cant_req2))
        
        # Tercer requisito
        if row.difValor3 and row.cantReq3:
            dificultad_req3 = int(row.difValor3)
            cant_req3 = int(row.cantReq3)
            requisitos_dificultad.append((dificultad_req3, cant_req3))
        
        print(f"\nDEBUG: Evaluando estrategia: {desc}")
        print(f"DEBUG:   - requisitos_dificultad: {requisitos_dificultad}")
        print(f"DEBUG:   - cant_a_sugerir: {cant_a_sugerir}")
        
        # NUEVA VALIDACIÓN: Verificar requisitos múltiples de dificultad
        # Si hay requisitos, validar que se puedan cumplir TODOS EXACTAMENTE con la selección del usuario
        if uris_cursando and requisitos_dificultad:
            seleccion_usuario_plan = [m for m in materias_habilitadas if m["uri"] in uris_cursando]
            
            # Verificar que podemos cumplir TODOS los requisitos
            total_requerido = 0
            puede_cumplir = True
            
            for (dif_req, cant_req) in requisitos_dificultad:
                materias_con_dificultad = [m for m in seleccion_usuario_plan if m["dificultad"] == dif_req]
                total_requerido += cant_req
                
                print(f"DEBUG:     - Req: {cant_req} materias de dif {dif_req}, disponibles: {len(materias_con_dificultad)}")
                
                if len(materias_con_dificultad) < cant_req:
                    print(f"DEBUG:     - ❌ No cumple: falta {cant_req - len(materias_con_dificultad)} materias de dif {dif_req}")
                    puede_cumplir = False
                    break
            
            if not puede_cumplir:
                print(f"DEBUG:   - Estrategia descartada (no cumple todos los requisitos de dificultad)")
                continue
            
            # Verificar que la cantidad total coincide con cant_a_sugerir
            if total_requerido != cant_a_sugerir:
                print(f"DEBUG:   - ⚠️ Advertencia: total_requerido ({total_requerido}) != cant_a_sugerir ({cant_a_sugerir})")
        
        # Filtrar candidatas para MODO AUTOMÁTICO (antigua lógica)
        candidatas = []
        if dificultad_req is not None:
            candidatas = [m for m in materias_habilitadas if m["dificultad"] == dificultad_req]
        else:
            candidatas = materias_habilitadas
        
        print(f"DEBUG:   - candidatas disponibles: {len(candidatas)}")
        
        # Verificar candidatas suficientes para min_req
        # IMPORTANTE: Si es MODO FILTRADO con múltiples requisitos, ya validamos arriba,
        # así que saltamos esta validación antigua que solo mira la primera dificultad
        if uris_cursando and len(requisitos_dificultad) > 1:
            # Ya validamos todo arriba, continuar con el scoring
            print(f"DEBUG:   - Plan multi-requisito ya validado, continuar con scoring")
        elif len(candidatas) < min_req:
            print(f"DEBUG:   - Estrategia descartada (candidatas < min_req)")
            continue
        
        # Calcular Score de Ajuste si hay selección de usuario
        if len(candidatas) >= min_req or (uris_cursando and len(requisitos_dificultad) > 1):
            # Calcular Score de Ajuste si hay selección de usuario
            score = 0
            correlativas_count = 0
            
            if uris_cursando:
                # NUEVO SCORING: Dificultades BAJAS tienen MÁS prioridad
                if dificultad_req:
                    user_count = user_selection_counts.get(dificultad_req, 0)
                    
                    # Score base INVERTIDO: dificultades bajas = más puntos
                    # Dif 1 = 400, Dif 2 = 300, Dif 3 = 200, Dif 4 = 100
                    weight = (5 - dificultad_req) * 100
                    
                    # Penalizamos la diferencia entre lo que pide el plan y lo que tiene el usuario
                    diff = abs(min_req - user_count)
                    score = weight - (diff * 10)
                    
                    print(f"DEBUG:   - user_count para dif {dificultad_req}: {user_count}")
                    print(f"DEBUG:   - score inicial (invertido para priorizar fáciles): {score}")
                    
                    # Bonus si el usuario tiene EXACTAMENTE o MÁS de lo requerido en esa dificultad
                    if user_count >= min_req:
                        score += 50
                        print(f"DEBUG:   - bonus por match exacto (+50), score: {score}")
                    
                    # BONUS POR CORRELATIVAS: Contar materias que desbloquea este plan
                    # Simular el plan para ver cuántas correlativas desbloquea
                    if dificultad_req is not None:
                        primary = [m for m in seleccion_usuario_plan if m["dificultad"] == dificultad_req]
                        plan_simulado = primary[:min_req]
                        
                        # Contar cuántas materias se desbloquearían
                        for materia in plan_simulado:
                            # Cada materia que corta otras suma al score
                            # Esto es una estimación - asumimos que materias difíciles cortan más
                            correlativas_count += (5 - materia.get("dificultad", 1))
                        
                        # Bonus proporcional a correlativas desbloqueadas
                        correlativas_bonus = correlativas_count * 5
                        score += correlativas_bonus
                        print(f"DEBUG:   - bonus por correlativas estimadas (+{correlativas_bonus}), score: {score}")
                else:
                    # Estrategia sin requisito de dificultad - PRIORIDAD BAJA (es fallback)
                    score = 50  # Menor que cualquier plan con requisitos específicos
                    print(f"DEBUG:   - Sin requisito de dificultad (fallback), score: {score}")
            
            print(f"DEBUG:   - Score final: {score}")
            estrategias_validas.append({
                "row": row,
                "candidatas": candidatas,
                "score": score,
                "orden": int(row.orden),
                "nombre": str(row.desc),
                "correlativas_count": correlativas_count
            })
        else:
            print(f"DEBUG:   - Estrategia descartada (candidatas < min_req)")

    # Ordenar estrategias válidas
    if uris_cursando:
        # Ordenar por SCORE (mayor mejor) - prioriza dificultades bajas y correlativas
        estrategias_validas.sort(key=lambda x: -x["score"])
    else:
        # Solo orden original
        estrategias_validas.sort(key=lambda x: x["orden"])

    # Seleccionar la mejor
    if estrategias_validas:
        best = estrategias_validas[0]
        row = best["row"]
        candidatas = best["candidatas"]
        
        estrategia_encontrada = True
        texto_recomendacion = str(row.desc)
        cant_a_sugerir = int(row.cant)
        
        # Construir plan
        # Reconstruir requisitos_dificultad desde row para usar en construcción del plan
        requisitos_dificultad_plan = []
        min_req_plan = int(row.minReq)
        if row.difValor:
            requisitos_dificultad_plan.append((int(row.difValor), min_req_plan))
        if row.difValor2 and row.cantReq2:
            requisitos_dificultad_plan.append((int(row.difValor2), int(row.cantReq2)))
        if row.difValor3 and row.cantReq3:
            requisitos_dificultad_plan.append((int(row.difValor3), int(row.cantReq3)))
        
        if uris_cursando:
             # MODO FILTRADO: Seleccionar EXACTAMENTE según requisitos múltiples
             seleccion_usuario = [m for m in materias_habilitadas if m["uri"] in uris_cursando]
             plan_seleccionado = []
             
             if requisitos_dificultad_plan:
                 # Plan con requisitos específicos: seleccionar según cada requisito
                 print(f"DEBUG: Construyendo plan con requisitos: {requisitos_dificultad_plan}")
                 
                 for (dif_req, cant_req) in requisitos_dificultad_plan:
                     materias_dif = [m for m in seleccion_usuario if m["dificultad"] == dif_req and m not in plan_seleccionado]
                     seleccionadas = materias_dif[:cant_req]
                     plan_seleccionado.extend(seleccionadas)
                     print(f"DEBUG:   - Seleccionadas {len(seleccionadas)} de dif {dif_req} (requeridas: {cant_req})")
             else:
                 # Plan flexible (sin requisitos): tomar las primeras disponibles
                 print(f"DEBUG: Plan flexible, tomando {cant_a_sugerir} materias cualquiera")
                 plan_seleccionado.extend(seleccion_usuario[:cant_a_sugerir])
        else:
            # MODO AUTOMÁTICO: Llenamos según estrategia
            seleccion = candidatas[:cant_a_sugerir]
            plan_seleccionado.extend(seleccion)
            
            if len(plan_seleccionado) < cant_a_sugerir:
                faltantes = cant_a_sugerir - len(plan_seleccionado)
                uris_sel = {m["uri"] for m in plan_seleccionado}
                resto = [m for m in materias_habilitadas if m["uri"] not in uris_sel]
                plan_seleccionado.extend(resto[:faltantes])
            
            
        # Identificar omitidas
        uris_sel = {m["uri"] for m in plan_seleccionado}
        
        if uris_cursando:
            # Si el usuario seleccionó materias, "Omitidas" son las que él eligió
            # pero que la estrategia filtró por exceso de carga/dificultad.
            uris_plan = {m["uri"] for m in plan_seleccionado}
            omitidas = [m for m in materias_habilitadas if m["uri"] in uris_cursando and m["uri"] not in uris_plan] 
        else:
            # Comportamiento default: Todo lo que sobra
            omitidas = [m for m in materias_habilitadas if m["uri"] not in uris_sel]

    # 5. Fallback si ninguna estrategia coincide
    if not estrategia_encontrada:
        # Fallback inteligente: "Minimo 2 materias"
        # Intentamos recomendar al menos 2 materias, priorizando las más fáciles/impactantes.
        
        texto_recomendacion = "Plan de Emergencia: No se pudo aplicar ninguna estrategia estricta. Se recomiendan materias disponibles para mantener la regularidad."
        
        if uris_cursando:
             plan_seleccionado = [m for m in materias_habilitadas if m["uri"] in uris_cursando]
             # Si el usuario eligió menos de 2, intentamos rellenar para cumplir el mínimo
             if len(plan_seleccionado) < 2:
                 faltantes = 2 - len(plan_seleccionado)
                 uris_sel = {m["uri"] for m in plan_seleccionado}
                 resto = [m for m in materias_habilitadas if m["uri"] not in uris_sel]
                 # Ordenar resto por dificultad (lo más fácil posible)
                 resto.sort(key=lambda x: x["dificultad"])
                 plan_seleccionado.extend(resto[:faltantes])
        else:
             # Si es automático, tomamos 2 materias como base segura.
             default_qty = 2
             plan_seleccionado = materias_habilitadas[:default_qty]
             
        omitidas = [m for m in materias_habilitadas if m["uri"] not in {x["uri"] for x in plan_seleccionado}]

    # Helper para formatear dificultad
    def get_dificultad_label(val):
        if val == 1: return "Fácil"
        if val == 2: return "Normal"
        if val == 3: return "Difícil"
        if val >= 4: return "Muy Difícil"
        return "Normal"

    # 6. Formatear respuesta
    return {
        "plan_recomendado": [{
            "uri": m["uri"], 
            "label": m["label"], 
            "score": 1.0, 
            "año": m["anio"], 
            "dificultad": m["dificultad"],
            "dificultad_label": get_dificultad_label(m["dificultad"]),
            "desbloquea_count": m["desbloquea_count"], 
            "creditos_otorgados": m["creditos"],
            "es_cursando": m["es_cursando"],
            "es_obligatoria": m["es_obligatoria"]
        } for m in plan_seleccionado],
        
        "materias_omitidas": [{
            "uri": m["uri"], 
            "label": m["label"], 
            "score": 0.0, 
            "año": m["anio"], 
            "dificultad": m["dificultad"],
            "dificultad_label": get_dificultad_label(m["dificultad"]),
            "desbloquea_count": m["desbloquea_count"]
        } for m in omitidas],
        
        "arquetipo": {
            "nombre": perfil_data["nombre_corto"],
            "color": perfil_data["color"],
            "consejos": [consejo_clave],
            "consejo_clave": consejo_clave, # Nuevo campo explícito
            "diagnostico": tarjeta_diagnostico
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

    # 3. Motor de Recomendación Genérico (Basado en Ontología)
    recomendados = []
    otros = []
    texto_plan_final = "Plan Personalizado"
    
    # Obtener estrategias del arquetipo desde la ontología
    ARQUETIPO_URIS = {
        1: "ArquetipoCritico",
        2: "ArquetipoBajo",
        3: "ArquetipoMedioBajo",
        4: "ArquetipoEquilibrado",
        5: "ArquetipoMedioAlto",
        6: "ArquetipoSuperAlto",
        7: "ArquetipoAtipico"
    }
    arquetipo_uri = ARQUETIPO_URIS.get(pid, "ArquetipoEquilibrado")

    query_estrategias = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    SELECT ?estrategia ?orden ?descripcion ?cant ?min_req ?dificultad_req_valor WHERE {{
        fiunju:{arquetipo_uri} fiunju:tieneEstrategiaExamen ?estrategia .
        ?estrategia fiunju:ordenPrioridad ?orden .
        ?estrategia fiunju:descripcionPlan ?descripcion .
        ?estrategia fiunju:cantidadMaterias ?cant .
        ?estrategia fiunju:cantidadMinimaRequerida ?min_req .
        OPTIONAL {{ 
            ?estrategia fiunju:requiereDificultadExamen ?dificultad_req_uri .
            ?dificultad_req_uri fiunju:tieneValor ?dificultad_req_valor .
        }}
    }} ORDER BY ?orden
    """
    
    estrategias = []
    try:
        estrategias = list(kg.query(query_estrategias))
    except Exception as e:
        print(f"Error consultando estrategias de examen: {e}")

    estrategia_match = None
    
    # Ordenamos materias por dificultad descendente (heuristic default: sacar lo difícil primero)
    materias_data.sort(key=lambda x: x["dificultad"], reverse=True)
    
    for row in estrategias:
        min_req = int(row.min_req)
        cant_total = int(row.cant)
        req_diff = int(row.dificultad_req_valor) if row.dificultad_req_valor else None
        
        candidates = []
        if req_diff:
            # Buscamos coincidencia exacta de dificultad
            candidates = [m for m in materias_data if m["dificultad"] == req_diff]
        else:
            # Si no hay requisito de dificultad, todas son candidatas
            candidates = materias_data
            
        # Verificamos si cumplimos el requisito mínimo
        if len(candidates) >= min_req:
            # Validación estricta de "Relleno" (Filler)
            # Si el plan requiere X cantidad total, y ya cubrimos el min_req de la dificultad obligatoria,
            # verificamos si tenemos suficientes materias "más fáciles" para llenar el resto.
            # Esto evita que un plan "1 Normal + 1 Dificil" se active si solo tenemos "2 Dificiles".
            
            match_possible = True
            count_primary = min_req # Tomamos lo justo y necesario de la dificultad requerida
            slots_remaining = cant_total - count_primary
            
            if slots_remaining > 0:
                if req_diff:
                    # Si hay requisito de dificultad, el relleno debe ser ESTRICTAMENTE MENOR
                    # (Asumimos que los planes mixtos buscan balance, no saturación)
                    fillers = [m for m in materias_data if m["dificultad"] < req_diff]
                else:
                    # Si no hay requisito (ej: 2 Cualquiera), el relleno es cualquier cosa que sobre
                    # (Pero ojo, candidates ya son todas. Simplemente chequeamos total)
                    fillers = materias_data # Simplificación, chequeamos len total abajo
                    
                if req_diff and len(fillers) < slots_remaining:
                    match_possible = False
                elif not req_diff and len(materias_data) < cant_total:
                    match_possible = False
            
            if match_possible:
                estrategia_match = {
                    "descripcion": str(row.descripcion),
                    "cant": cant_total,
                    "min_req": min_req,
                    "req_diff": req_diff
                }
                break
            
    if estrategia_match:
        texto_plan_final = estrategia_match["descripcion"]
        target_qty = estrategia_match["cant"]
        req_diff = estrategia_match["req_diff"]
        
        taken_uris = set()
        
        # 1. Cumplir el requisito primario (min_req de la dificultad específica)
        if req_diff:
            primary_candidates = [m for m in materias_data if m["dificultad"] == req_diff]
            # Tomamos la cantidad mínima requerida de esta dificultad
            count_to_take = min(len(primary_candidates), estrategia_match["min_req"])
            # Si el plan pide SOLO esta dificultad (ej: "1 Dificil" y cant=1), tomamos hasta target_qty
            # Si el plan es mixto (ej: "1 Dificil + 1 Normal"), tomamos min_req y luego rellenamos.
            # Heurística: Tomamos min_req.
            
            for i in range(count_to_take):
                m = primary_candidates[i]
                recomendados.append(m)
                taken_uris.add(m["uri"])
                
            # 2. Rellenar hasta target_qty con el resto
            # Ordenamos el resto por dificultad ASCENDENTE (para equilibrar carga y evitar meter Muy Dificiles si no se piden)
            remaining = [m for m in materias_data if m["uri"] not in taken_uris]
            
            # FILTRO CLAVE: Si la estrategia pide una dificultad específica (ej: Dificil), 
            # no deberíamos rellenar con cosas MÁS difíciles (Muy Dificil) salvo que sea explícito.
            # Vamos a filtrar 'remaining' para que solo tenga dificultad <= req_diff (o un poco más flexible?)
            # Para ser seguros: solo rellenamos con dificultad <= req_diff si req_diff existe.
            # O mejor aún: Si el plan es "1 Normal + 1 Dificil" (req_diff=3), no queremos Muy Dificil (4).
            
            if req_diff:
                remaining = [m for m in remaining if m["dificultad"] <= req_diff]

            remaining.sort(key=lambda x: x["dificultad"]) # De menor a mayor dificultad para el relleno
            
            while len(recomendados) < target_qty and remaining:
                m = remaining.pop(0)
                recomendados.append(m)
                taken_uris.add(m["uri"])
                
            # El resto va a "otros"
            otros = [m for m in materias_data if m["uri"] not in taken_uris]
            
        else:
            # Sin requisito de dificultad específico (ej: "2 Cualquiera")
            # Tomamos las top N (ya ordenadas descendente arriba)
            recomendados = materias_data[:target_qty]
            otros = materias_data[target_qty:]
            
    else:
        # Fallback si no hay estrategia (o no hay materias suficientes para ninguna)
        # Recomendamos 1 si hay
        if materias_data:
            recomendados.append(materias_data[0])
            otros = materias_data[1:]
            texto_plan_final = "Plan Genérico (No se encontraron estrategias específicas aplicables)"
        else:
            texto_plan_final = "No tienes finales pendientes para rendir."

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

    # Fetch diagnostic card and key advice from ontology
    tarjeta_diagnostico = "Diagnóstico no disponible."
    consejo_clave = "Consejo no disponible."
    
    try:
        query_info = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT ?diagnostico ?consejo WHERE {{
            OPTIONAL {{ fiunju:{arquetipo_uri} fiunju:tieneTarjetaDiagnostico ?diagnostico . }}
            OPTIONAL {{ fiunju:{arquetipo_uri} fiunju:tieneConsejoClave ?consejo . }}
        }}
        """
        res_info = list(kg.query(query_info))
        if res_info:
            if res_info[0].diagnostico:
                tarjeta_diagnostico = str(res_info[0].diagnostico)
            if res_info[0].consejo:
                consejo_clave = str(res_info[0].consejo)
    except Exception as e:
        print(f"Error fetching archetype info: {e}")
    
    # Fallback Hardcoded para Diagnóstico
    if tarjeta_diagnostico == "Diagnóstico no disponible." or not tarjeta_diagnostico or "DEBUG" in tarjeta_diagnostico:
        tarjeta_diagnostico = DIAGNOSTICOS_HARDCODED.get(arquetipo_uri, "Diagnóstico no disponible.")

    return {
        "plan_recomendado": plan_final,
        "arquetipo": {
            "nombre": perfil_data["nombre_corto"],
            "color": perfil_data["color"],
            "consejos": [consejo_clave], # Mantener compatibilidad
            "consejo_clave": consejo_clave, # Nuevo campo explícito
            "diagnostico": tarjeta_diagnostico
        },
        "consejos_adicionales": [
            texto_plan_final,
            perfil_data["finales"]["comentario"]
        ]
    }