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

    # 3. Motor de Recomendación Genérico (Basado en Ontología)
    recomendados = []
    otros = []
    texto_plan_final = "Plan Personalizado"
    
    # Obtener estrategias del arquetipo desde la ontología
    nombre_arquetipo = perfil_data["nombre_corto"]
    query_estrategias = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    SELECT ?estrategia ?orden ?descripcion ?cant ?min_req ?dificultad_req_valor WHERE {{
        ?arquetipo fiunju:tieneNombreArquetipo "{nombre_arquetipo}"@es .
        ?arquetipo fiunju:tieneEstrategiaExamen ?estrategia .
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