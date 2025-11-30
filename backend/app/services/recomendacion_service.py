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
    SELECT ?orden ?desc ?cant ?minReq ?difValor
    WHERE {{
        fiunju:{arquetipo_uri} fiunju:tieneEstrategiaPosible ?est .
        
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
    
    estrategia_encontrada = False
    
    # 4. Evaluar Estrategias
    # Si el usuario ya seleccionó materias ("Cursando"), buscamos la estrategia que MEJOR se ajuste a su selección.
    # Si no, usamos el orden de prioridad por defecto.
    
    # Analizar selección del usuario
    user_selection_counts = {4: 0, 3: 0, 2: 0, 1: 0}
    if uris_cursando:
        for m in materias_habilitadas:
            if m["uri"] in uris_cursando:
                d = m["dificultad"]
                if d in user_selection_counts:
                    user_selection_counts[d] += 1
                elif d >= 4:
                    user_selection_counts[4] += 1

    estrategias_validas = []
    for row in results:
        desc = str(row.desc)
        cant_a_sugerir = int(row.cant)
        min_req = int(row.minReq)
        dificultad_req = int(row.difValor) if row.difValor else None
        
        # Filtrar materias que cumplen con el requisito de dificultad de la estrategia
        candidatas = []
        if dificultad_req is not None:
            candidatas = [m for m in materias_habilitadas if m["dificultad"] == dificultad_req]
        else:
            candidatas = materias_habilitadas
            
        # Verificar si es válida
        if len(candidatas) >= min_req:
            # Calcular Score de Ajuste si hay selección de usuario
            score = 0
            if uris_cursando:
                # Priorizamos coincidencia en la dificultad requerida
                if dificultad_req:
                    user_count = user_selection_counts.get(dificultad_req, 0)
                    # Score base alto para dificultades altas
                    weight = dificultad_req * 100 
                    # Penalizamos la diferencia entre lo que pide el plan y lo que tiene el usuario
                    diff = abs(min_req - user_count)
                    score = weight - (diff * 10)
                    
                    # Bonus si el usuario tiene EXACTAMENTE o MÁS de lo requerido en esa dificultad
                    if user_count >= min_req:
                        score += 50
                else:
                    # Estrategia sin requisito de dificultad (ej: "Variadas")
                    score = 10 # Prioridad baja frente a matches específicos
            
            estrategias_validas.append({
                "row": row,
                "candidatas": candidatas,
                "score": score,
                "orden": int(row.orden)
            })

    # Ordenar estrategias válidas
    if uris_cursando:
        # Mayor score primero, luego menor orden de prioridad (original)
        estrategias_validas.sort(key=lambda x: (-x["score"], x["orden"]))
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
        if uris_cursando:
             # MODO FILTRADO: Ajustamos la selección del usuario a la estrategia recomendada
             
             # 1. Identificar materias seleccionadas por el usuario
             seleccion_usuario = [m for m in materias_habilitadas if m["uri"] in uris_cursando]
             
             # 2. Filtrar las que coinciden con el requisito de dificultad (si existe)
             if dificultad_req:
                 primary = [m for m in seleccion_usuario if m["dificultad"] == dificultad_req]
                 others = [m for m in seleccion_usuario if m["dificultad"] != dificultad_req]
             else:
                 primary = seleccion_usuario
                 others = []
                 
             # 3. Construir plan respetando cantidad sugerida
             plan_seleccionado = []
             
             # Tomar prioritarias (hasta cant_a_sugerir)
             # Ordenamos las primary por impacto o alguna metrica si hay muchas? 
             # Por ahora confiamos en el orden de 'materias_habilitadas' (que ya tiene logica de sort)
             plan_seleccionado.extend(primary[:cant_a_sugerir])
             
             # Si falta para llegar a la cantidad, rellenar con las otras
             if len(plan_seleccionado) < cant_a_sugerir:
                 faltantes = cant_a_sugerir - len(plan_seleccionado)
                 # Ordenar 'others' por dificultad ascendente (rellenar con lo más fácil posible de lo que eligió)
                 others.sort(key=lambda x: x["dificultad"]) 
                 plan_seleccionado.extend(others[:faltantes])
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
        # Tomar las top N por prioridad (ya ordenadas)
        default_qty = 3
        if uris_cursando:
             plan_seleccionado = [m for m in materias_habilitadas if m["uri"] in uris_cursando]
        else:
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
    
    # DEBUG: Force diagnostic if empty
    if tarjeta_diagnostico == "Diagnóstico no disponible.":
        tarjeta_diagnostico = "DEBUG: El backend está ejecutando el nuevo código, pero la query falló o no trajo datos."

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