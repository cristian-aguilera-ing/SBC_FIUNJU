# Este es el archivo: backend/app/services/evaluacion_service.py

from rdflib import Graph
from app.models.user import User
from app.models.enums import CondicionLaboral

def evaluar_plan_cursada_actual(user: User, kg: Graph) -> list[str]:
    consejos = []
    materias_cursando = [m for m in user.materias_cursadas if m.estado == "Cursando"]
    
    if not materias_cursando:
        return ["No tienes materias marcadas como 'Cursando'. ¿Seguro que no quieres aprovechar el cuatrimestre?"]

    uris = " ".join([f"<{m.materia_uri}>" for m in materias_cursando])
    query = f"""PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?label ?dificultadVal
WHERE {{
    VALUES ?materia {{ {uris} }}
    ?materia rdfs:label ?label .
    OPTIONAL {{ ?materia fiunju:tieneDificultadCursada ?dif . ?dif fiunju:tieneValor ?dificultadVal . }}
}}"""
    results = kg.query(query)
    
    dif_alta = 0
    labels_alta = []
    total_materias = len(materias_cursando)
    
    for r in results:
        if int(r.dificultadVal or 1) >= 3:
            dif_alta += 1
            labels_alta.append(str(r.label))
            
    # Análisis de Carga vs Disponibilidad
    if user.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO:
        if total_materias > 2:
             consejos.append(f"⚠️ ALERTA ROJA: Trabajas 8hs y te anotaste en {total_materias} materias. Estadísticamente, es muy probable que abandones alguna. Te sugiero bajar a 2.")
        elif dif_alta >= 2:
             consejos.append(f"⚠️ Trabajas full-time y elegiste 2 materias difíciles ({', '.join(labels_alta)}). Es una combinación explosiva. Considera cursar solo una de ellas.")
        else:
             consejos.append("Para alguien que trabaja full-time, tu selección parece prudente. ¡Sigue así!")
    
    elif user.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO:
        if total_materias > 3:
            consejos.append(f"Estás cursando {total_materias} materias con trabajo parcial. Vas a tener poco margen de error. Organiza tu agenda al milímetro.")
        elif dif_alta > 2:
             consejos.append("Tres materias difíciles con trabajo parcial es arriesgado. Prioriza las correlativas.")
    
    else: # No trabaja
        if total_materias <= 2:
            consejos.append("Tienes todo el tiempo del mundo y cursas poco. ¡Acelera! Podrías sumar una materia más o adelantar finales.")
        elif total_materias >= 5:
             consejos.append("Un plan de 5 materias es valiente. Asegúrate de no descuidar tu salud mental.")

    return consejos

def evaluar_plan_examen_actual(user: User, kg: Graph) -> list[str]:
    consejos = []
    materias_rendir = [m for m in user.materias_cursadas if m.estado == "Regular"]
    
    if not materias_rendir:
        return ["No tienes finales pendientes marcados."]
    
    cant = len(materias_rendir)
    
    if user.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO and cant > 1:
        consejos.append("Trabajando 8hs, rendir más de un final por turno es titánico. Prioriza por vencimiento o correlatividad.")
    elif user.condicion_laboral == CondicionLaboral.MEDIO_TIEMPO and cant > 2:
        consejos.append("Rendir más de 2 finales trabajando medio tiempo es ambicioso. Prioriza.")
    elif cant > 3:
         consejos.append(f"Tienes {cant} finales pendientes. No intentes rendir todos. Enfócate en 2 o 3 máximo.")
    else:
        consejos.append(f"Tienes {cant} finales en carpeta. Revisa la estrategia recomendada arriba para ver cuál atacar primero.")
        
    return consejos

def evaluar_plan_hipotetico(user: User, plan_recomendado: list[dict], kg: Graph) -> list[str]:
    consejos = []
    if not plan_recomendado:
        return ["No hay materias disponibles para recomendar."]
        
    dificiles = [m["label"] for m in plan_recomendado if m["dificultad"] >= 3]
    count = len(plan_recomendado)
    
    if user.condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO:
        if count > 2: 
            consejos.append("El algoritmo encontró estas opciones, pero dado que trabajas full-time, te recomiendo encarecidamente cursar MÁXIMO 2.")
    
    if len(dificiles) >= 2:
        consejos.append(f"Este plan incluye materias filtro: {', '.join(dificiles[:2])}. Requerirá mucha dedicación.")
    else:
        consejos.append("Este es un plan sólido y equilibrado.")
        
    return consejos
