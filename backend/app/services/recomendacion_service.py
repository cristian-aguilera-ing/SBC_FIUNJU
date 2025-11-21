# Este es el archivo: backend/app/services/recomendacion_service.py

from rdflib import Graph
import copy 
from app.models.user import User
from app.models.enums import CondicionLaboral, MetodoEstudio, HorasEstudio
from app.services import scoring_service, evaluacion_service
from app.core.reglas_negocio import REGLAS_CURSADA
from app.schemas.recomendacion import PlanCursadaSimuladoRequest
from datetime import datetime, timedelta, timezone 
from collections import defaultdict

# --- CONSULTAS SPARQL (SIN INDENTACIÓN INICIAL PARA EVITAR ERRORES) ---

SPARQL_QUERY_MATERIAS_BASICO = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT 
    ?materia ?label 
    (COALESCE(?año_num, 0) as ?año)
    (COALESCE(?valorDificultad, 1) as ?dificultad)
    (COALESCE(?cred_otorgados, 0) as ?creditos_otorgados)
    (COALESCE(?cred_requeridos, 0) as ?creditos_requeridos)
    (COALESCE(?req_4to, false) as ?requiere_4to)
WHERE {
    ?materia a fiunju:Materia ;
             rdfs:label ?label .
    OPTIONAL { ?materia fiunju:perteneceAlAño ?año_num . }
    OPTIONAL { 
        ?materia fiunju:tieneDificultadCursada ?nivel . 
        ?nivel fiunju:tieneValor ?valorDificultad .
    }
    OPTIONAL { ?materia fiunju:otorgaCreditos ?cred_otorgados . }
    OPTIONAL { ?materia fiunju:requiereCreditos ?cred_requeridos . }
    OPTIONAL { ?materia fiunju:requiereCuartoAnoAprobado ?req_4to . }
} 
ORDER BY ?label"""

SPARQL_QUERY_REQUISITOS = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
SELECT ?materia ?req
WHERE {
    ?materia fiunju:tieneRequisito ?req .
}"""

# Impacto Transitivo (Desbloqueos futuros)
SPARQL_QUERY_IMPACTO_FUTURO = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
SELECT ?materia_actual (COUNT(DISTINCT ?materia_futura) as ?impacto)
WHERE {
    ?materia_actual fiunju:esRequisitoPara+ ?materia_futura .
} GROUP BY ?materia_actual"""


def _get_materias_habilitadas(user: User, kg: Graph) -> list[dict]:
    """
    Busca materias habilitadas validando estado, correlativas, créditos y 4to año.
    """
    materias_actuales_uris = {m.materia_uri for m in user.materias_cursadas}
    aprobadas_uris = {m.materia_uri for m in user.materias_cursadas if m.estado == "Aprobada"}

    # Ejecutar consultas
    results_basico = kg.query(SPARQL_QUERY_MATERIAS_BASICO)
    results_requisitos = kg.query(SPARQL_QUERY_REQUISITOS)
    results_impacto = kg.query(SPARQL_QUERY_IMPACTO_FUTURO)

    # Procesar mapas
    requisitos_map = defaultdict(set)
    for row in results_requisitos:
        requisitos_map[str(row.materia)].add(str(row.req))

    impacto_map = defaultdict(int)
    for row in results_impacto:
        impacto_map[str(row.materia_actual)] = int(row.impacto)

    # Calcular créditos y estado de 4to año
    creditos_acumulados = 0
    materias_obligatorias_1_a_4 = set()
    datos_materias = {} 

    for row in results_basico:
        uri = str(row.materia)
        anio = int(row.año)
        creditos = int(row.creditos_otorgados)
        
        datos_materias[uri] = {
            "label": str(row.label),
            "año": anio,
            "dificultad": int(row.dificultad),
            "cred_otorgados": creditos,
            "cred_req": int(row.creditos_requeridos),
            "req_4to": bool(row.requiere_4to)
        }
        
        if uri in aprobadas_uris:
            creditos_acumulados += creditos
        if 0 < anio <= 4:
            materias_obligatorias_1_a_4.add(uri)

    tiene_4to_completo = materias_obligatorias_1_a_4.issubset(aprobadas_uris)

    # Filtrar
    materias_habilitadas = []
    for uri, datos in datos_materias.items():
        if uri in materias_actuales_uris: continue
        
        reqs = requisitos_map.get(uri, set())
        if reqs and not reqs.issubset(aprobadas_uris): continue 
        
        if datos["cred_req"] > 0 and creditos_acumulados < datos["cred_req"]: continue
        if datos["req_4to"] and not tiene_4to_completo: continue

        materias_habilitadas.append({
            "uri": uri,
            "label": datos["label"],
            "año": datos["año"],
            "dificultad": datos["dificultad"],
            "creditos_otorgados": datos["cred_otorgados"],
            "desbloquea_count": impacto_map.get(uri, 0)
        })
        
    return materias_habilitadas


def _analizar_bloqueo_pps(user: User, kg: Graph, aprobadas_uris: set, creditos_acumulados: int) -> list[str]:
    avisos = []
    pps_uri = "http://fi.unju.edu.ar/ontologia/informatica#PPS"
    if any(m.materia_uri == pps_uri for m in user.materias_cursadas): return []

    query_avance = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    SELECT ?materia WHERE { ?materia fiunju:perteneceAlAño ?anio . FILTER(?anio >= 4) }"""
    results = kg.query(query_avance)
    materias_avanzadas = {str(r.materia) for r in results}
    
    if not aprobadas_uris.isdisjoint(materias_avanzadas):
        if creditos_acumulados < 270:
            faltan = 270 - creditos_acumulados
            avisos.append(f"⚠️ PARA LA PPS: Te faltan {faltan} créditos en optativas (Tienes {creditos_acumulados}/270).")
        
        query_1_a_4 = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT ?materia WHERE { ?materia a fiunju:Materia ; a fiunju:Obligatoria ; fiunju:perteneceAlAño ?anio . FILTER(?anio <= 4) }"""
        res_4to = kg.query(query_1_a_4)
        obligatorias_req = {str(r.materia) for r in res_4to}
        
        if not obligatorias_req.issubset(aprobadas_uris):
            avisos.append("⚠️ PARA LA PPS: Necesitas tener aprobado TODO hasta 4to año inclusive.")
    return avisos


def generar_plan_cursada_optimo(user: User, kg: Graph) -> dict:
    materias_habilitadas = _get_materias_habilitadas(user, kg)
    aprobadas_uris = {m.materia_uri for m in user.materias_cursadas if m.estado == "Aprobada"}
    
    # Calcular créditos
    query_cred = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#> SELECT (SUM(?cred) as ?t) WHERE { VALUES ?m { %s } ?m fiunju:otorgaCreditos ?cred . }""" % " ".join([f"<{u}>" for u in aprobadas_uris]) if aprobadas_uris else ""
    creditos_acumulados = 0
    if aprobadas_uris:
        try:
            for r in kg.query(query_cred): creditos_acumulados = int(r.t) if r.t else 0
        except: pass

    if not materias_habilitadas:
        return {
            "plan_recomendado": [], "materias_omitidas": [],
            "consejos_adicionales": ["¡No tienes materias pendientes habilitadas!"]
        }

    materias_con_score = []
    for materia in materias_habilitadas:
        score = scoring_service.calcular_score_materia(materia, user, kg)
        materia["score"] = score
        materias_con_score.append(materia)
    
    materias_con_score.sort(key=lambda m: m["score"], reverse=True)
    
    condicion_val = user.condicion_laboral.value if user.condicion_laboral else CondicionLaboral.NO_TRABAJA.value
    regla = REGLAS_CURSADA.get(condicion_val, REGLAS_CURSADA[CondicionLaboral.NO_TRABAJA.value])
    
    max_materias = regla["max_materias_totales"]
    max_dificiles = regla["max_materias_dificiles"]
    
    plan_recomendado = []
    materias_omitidas = []
    dificiles_count = 0
    
    for materia in materias_con_score:
        if len(plan_recomendado) >= max_materias:
            materias_omitidas.append(materia)
            continue
        es_dificil = materia["dificultad"] >= 3
        if es_dificil:
            if dificiles_count < max_dificiles:
                plan_recomendado.append(materia)
                dificiles_count += 1
            else:
                materias_omitidas.append(materia)
        else:
            plan_recomendado.append(materia)
            
    consejos = evaluacion_service.evaluar_plan_hipotetico(user, plan_recomendado, kg)
    avisos_pps = _analizar_bloqueo_pps(user, kg, aprobadas_uris, creditos_acumulados)
    consejos.extend(avisos_pps)
    
    return {
        "plan_recomendado": plan_recomendado,
        "materias_omitidas": materias_omitidas,
        "consejos_adicionales": consejos
    }


def generar_estrategia_examenes(user: User, kg: Graph) -> dict:
    materias_para_rendir = [m for m in user.materias_cursadas if m.estado == "Regular"]
    if not materias_para_rendir:
        return {"plan_recomendado": [], "consejos_adicionales": ["No tienes finales pendientes."]}

    aprobadas_uris = {m.materia_uri for m in user.materias_cursadas if m.estado == "Aprobada"}
    
    # 1. Labels Map
    query_labels = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?materia ?label WHERE { ?materia a <http://fi.unju.edu.ar/ontologia/informatica#Materia> ; rdfs:label ?label . }"""
    results_labels = kg.query(query_labels)
    labels_map = {str(r.materia): str(r.label) for r in results_labels}

    # 2. Créditos
    query_cred = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#> SELECT (SUM(?cred) as ?t) WHERE { VALUES ?m { %s } ?m fiunju:otorgaCreditos ?cred . }""" % " ".join([f"<{u}>" for u in aprobadas_uris]) if aprobadas_uris else ""
    creditos_acumulados = 0
    if aprobadas_uris:
        try:
            for r in kg.query(query_cred): creditos_acumulados = int(r.t) if r.t else 0
        except: pass
        
    # 3. Impacto Futuro (Para desempatar prioridades)
    query_impacto = """PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    SELECT ?materia_actual (COUNT(DISTINCT ?materia_futura) as ?impacto)
    WHERE { ?materia_actual fiunju:esRequisitoPara+ ?materia_futura . } GROUP BY ?materia_actual"""
    impacto_map = {}
    for row in kg.query(query_impacto):
        impacto_map[str(row.materia_actual)] = int(row.impacto)

    materias_values = " ".join([f"<{m.materia_uri}>" for m in materias_para_rendir])
    query_str = f"""PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?materia ?labelMateria ?labelModalidad ?labelDificultad (MAX(?valorNumerico) as ?maxValor) 
       (GROUP_CONCAT(DISTINCT ?req; separator=";") AS ?requisitos)
       (MAX(?cred_req) as ?creditos_requeridos)
WHERE {{
    VALUES ?materia {{ {materias_values} }}
    ?materia rdfs:label ?labelMateria .
    ?materia fiunju:tieneModalidadExamen ?modalidad .
    ?modalidad rdfs:label ?labelModalidad .
    ?modalidad fiunju:tieneDificultadExamen ?dificultadObj . 
    ?dificultadObj fiunju:tieneValor ?valorNumerico .
    ?dificultadObj rdfs:label ?labelDificultad . 
    OPTIONAL {{ ?materia fiunju:tieneRequisito ?req . }}
    OPTIONAL {{ ?materia fiunju:requiereCreditos ?cred_req . }}
}} GROUP BY ?materia ?labelMateria ?labelModalidad ?labelDificultad ?valorNumerico"""
    
    results = kg.query(query_str)
    datos_ontologia = {}
    for row in results:
        uri = str(row.materia)
        if uri not in datos_ontologia:
            datos_ontologia[uri] = {
                "label": str(row.labelMateria), "max_dif_valor": 0, "max_dif_label": "N/A", 
                "modalidades": set(), "requisitos": set(), "cred_req": 0
            }
        datos_ontologia[uri]["modalidades"].add(str(row.labelModalidad))
        if row.requisitos:
            for r in str(row.requisitos).split(';'): datos_ontologia[uri]["requisitos"].add(r)
        if row.creditos_requeridos:
            datos_ontologia[uri]["cred_req"] = int(row.creditos_requeridos)

        if int(row.maxValor) > datos_ontologia[uri]["max_dif_valor"]:
            datos_ontologia[uri]["max_dif_valor"] = int(row.maxValor)
            datos_ontologia[uri]["max_dif_label"] = str(row.labelDificultad)

    plan_recomendado = []
    ahora = datetime.now(timezone.utc)
    DIAS_VENCIMIENTO_REGULARIDAD = 365 * 2
    
    # Contadores para sugerencias globales
    count_habilitadas = 0
    count_dificiles = 0

    for materia in materias_para_rendir:
        datos = datos_ontologia.get(materia.materia_uri)
        if not datos: continue
        
        esta_habilitada = True
        motivo_bloqueo = None
        correlativas_pendientes = []
        
        faltantes = [r for r in datos["requisitos"] if r not in aprobadas_uris]
        for f in faltantes: correlativas_pendientes.append(labels_map.get(f, "Correlativa"))
            
        if faltantes:
            esta_habilitada = False
            motivo_bloqueo = "Falta aprobar correlativas"
        
        if esta_habilitada and datos["cred_req"] > 0 and creditos_acumulados < datos["cred_req"]:
            esta_habilitada = False
            motivo_bloqueo = f"Faltan créditos ({creditos_acumulados}/{datos['cred_req']})"
            
        if esta_habilitada:
            count_habilitadas += 1
            if datos["max_dif_valor"] >= 3:
                count_dificiles += 1

        dias_restantes = None
        if materia.fecha_regularidad:
            fecha_reg = materia.fecha_regularidad
            if fecha_reg.tzinfo is None: fecha_reg = fecha_reg.replace(tzinfo=timezone.utc)
            fecha_vencimiento = fecha_reg.astimezone(timezone.utc) + timedelta(days=DIAS_VENCIMIENTO_REGULARIDAD)
            dias_restantes = (fecha_vencimiento - ahora).days
            
        # --- GENERACIÓN DE CONSEJO PROFUNDO Y PERSONALIZADO ---
        consejo = ""
        modalidades_str = ", ".join(datos["modalidades"]).lower()
        es_dificil = datos["max_dif_valor"] >= 3
        es_oral = "oral" in modalidades_str
        es_escrito = "escrito" in modalidades_str
        impacto_futuro = impacto_map.get(materia.materia_uri, 0)
        
        # A. Prioridad Estratégica (¿Por qué rendir ESTA y no otra?)
        prioridad_msg = ""
        if impacto_futuro > 5:
            prioridad_msg = f"🔥 PRIORIDAD ALTA: Esta materia traba {impacto_futuro} materias futuras. ¡Ríndela YA!"
        elif impacto_futuro > 0:
            prioridad_msg = "Rindirla te habilitará nuevas materias para cursar."
        else:
            prioridad_msg = "No traba correlativas directas, puedes dejarla para el final del turno."
        
        # B. Consejo según Perfil (¿CÓMO rendirla?)
        tip_estudio = ""
        
        # 1. Situación Laboral
        if user.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO:
            if count_habilitadas > 1 and es_dificil:
                tip_estudio = "Trabajas 8hs: Si tienes otro final más fácil, quizás convenga priorizar ese y dejar este 'tanque' para una fecha donde tengas vacaciones. "
            elif es_oral:
                tip_estudio = "Con poco tiempo por el trabajo, el oral es peligroso. Practica 'speechs' cortos en el almuerzo o viaje. "
            else:
                tip_estudio = "Organiza bloques de estudio de 1h al día después del trabajo. La constancia le gana a la intensidad aquí. "
        
        elif user.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO:
            if es_dificil:
                tip_estudio = "Aprovecha tu media jornada libre para los temas prácticos de esta materia, que suelen llevar más tiempo. "
            else:
                tip_estudio = "Tienes buen balance tiempo/estudio. Es una oportunidad ideal para preparar este final con profundidad. "
        
        else: # No trabaja
            if es_dificil:
                tip_estudio = "Tienes todo el tiempo disponible: No hay excusas. Profundiza en la bibliografía, no solo en apuntes. "
            else:
                tip_estudio = "Deberías poder liquidar este final en 1 o 2 semanas de estudio intensivo. "

        # 2. Horas de Estudio (Refinamiento)
        if user.horas_estudio == HorasEstudio.POCAS and es_dificil and not tip_estudio:
            tip_estudio += "Tienes pocas horas y es difícil: Enfócate 100% en resolver exámenes de años anteriores (pareto). "

        # 3. Método (Refinamiento)
        if user.metodo_estudio_preferido == MetodoEstudio.SOLO and es_oral:
            tip_estudio += "Estudias solo: Ojo con el oral. Grábate explicando los temas para detectar fallos."
        elif user.metodo_estudio_preferido == MetodoEstudio.GRUPO and es_escrito:
            tip_estudio += "Te gusta el grupo: Sirve para teoría, pero para este escrito necesitas sentarte solo a resolver problemas."

        # Armado final del consejo
        if not esta_habilitada:
             consejo = "⛔ Aún no puedes rendir. Primero debes aprobar las correlativas o sumar créditos."
        else:
            consejo = f"{prioridad_msg} \n💡 {tip_estudio}"

        plan_recomendado.append({
            "uri": materia.materia_uri,
            "label": datos["label"],
            "fecha_regularidad": materia.fecha_regularidad,
            "dias_restantes": dias_restantes, 
            "dificultad_examen_label": datos["max_dif_label"],
            "dificultad_examen_valor": datos["max_dif_valor"],
            "modalidades": list(datos["modalidades"]),
            "esta_habilitada": esta_habilitada,
            "motivo_bloqueo": motivo_bloqueo,
            "correlativas_pendientes": correlativas_pendientes,
            "consejo_personalizado": consejo,
            
            # Datos internos para el sort
            "_impacto": impacto_futuro
        })

    # ORDENAMIENTO INTELIGENTE FINAL
    plan_recomendado.sort(key=lambda m: (
        not m["esta_habilitada"], # 1. Habilitadas primero
        -m["_impacto"],           # 2. Las que más traban primero (Estrategia pura)
        m["dias_restantes"] if m["dias_restantes"] is not None else 9999 # 3. Las que se vencen
    ))

    consejos = evaluacion_service.evaluar_plan_examen_actual(user, kg)
    return {
        "plan_recomendado": plan_recomendado,
        "consejos_adicionales": consejos
    }
    
def generar_plan_cursada_simulado(user, data, kg):
    user_temp = copy.deepcopy(user)
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        if hasattr(user_temp, k): setattr(user_temp, k, v)
    return generar_plan_cursada_optimo(user_temp, kg)