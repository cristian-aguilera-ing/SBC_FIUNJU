# Este es el archivo: backend/app/services/alertas_service.py

from rdflib import Graph
from app.models.user import User
from app.schemas.alertas import Alerta, TipoAlerta
from app.services import recomendacion_service
from datetime import datetime, timedelta, timezone

# Definimos las reglas de alertas
DIAS_VENCIMIENTO_REGULARIDAD = 365 * 2 
DIAS_AVISO_VENCIMIENTO = DIAS_VENCIMIENTO_REGULARIDAD - 180 

def _check_riesgo_regularidad(user: User, materias_regulares: list, kg: Graph) -> list[Alerta]:
    """Comprueba si alguna materia regular está cerca de vencer."""
    alertas = []
    ahora = datetime.now(timezone.utc)
    
    materia_labels = {}
    if materias_regulares:
        uris_values = " ".join([f"<{m.materia_uri}>" for m in materias_regulares])
        # SIN INDENTACIÓN
        query_labels = f"""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?materia ?label WHERE {{
    VALUES ?materia {{ {uris_values} }}
    ?materia rdfs:label ?label .
}}"""
        results = kg.query(query_labels)
        materia_labels = {str(r.materia): str(r.label) for r in results}

    for materia in materias_regulares:
        if materia.fecha_regularidad:
            fecha_reg = materia.fecha_regularidad
            if fecha_reg.tzinfo is None:
                fecha_reg = fecha_reg.replace(tzinfo=timezone.utc)

            fecha_reg_utc = fecha_reg.astimezone(timezone.utc)
            dias_transcurridos = (ahora - fecha_reg_utc).days
            
            if dias_transcurridos > DIAS_VENCIMIENTO_REGULARIDAD:
                alertas.append(Alerta(
                    tipo=TipoAlerta.RIESGO_REGULARIDAD,
                    mensaje=f"¡Riesgo Alto! Tu regularidad para '{materia_labels.get(materia.materia_uri, 'Materia')}' ha vencido.",
                    materia_uri=materia.materia_uri,
                    materia_label=materia_labels.get(materia.materia_uri)
                ))
            elif dias_transcurridos > DIAS_AVISO_VENCIMIENTO:
                dias_restantes = DIAS_VENCIMIENTO_REGULARIDAD - dias_transcurridos
                alertas.append(Alerta(
                    tipo=TipoAlerta.RIESGO_REGULARIDAD,
                    mensaje=f"¡Atención! Tu regularidad para '{materia_labels.get(materia.materia_uri, 'Materia')}' vence en {dias_restantes} días.",
                    materia_uri=materia.materia_uri,
                    materia_label=materia_labels.get(materia.materia_uri)
                ))
    return alertas

def _check_cuellos_de_botella(user: User, kg: Graph) -> list[Alerta]:
    """
    Detecta materias habilitadas que el usuario NO está cursando
    pero que traban una gran parte del grafo FUTURO restante.
    """
    alertas = []
    
    # 1. Obtener qué puede cursar ahora
    # Esta función ya calcula el "desbloquea_count" TRANSITIVO (impacto real)
    materias_habilitadas = recomendacion_service._get_materias_habilitadas(user, kg)
    
    # 2. Ordenar por impacto
    materias_habilitadas.sort(key=lambda m: m["desbloquea_count"], reverse=True)
    
    # 3. Generar alertas solo para las Top 3 más críticas
    for materia in materias_habilitadas[:3]:
        impacto = materia["desbloquea_count"]
        
        # Solo alertar si el impacto es significativo (traba más de 5 materias futuras)
        if impacto > 5: 
            mensaje = f"'{materia['label']}' es un CUELLO DE BOTELLA CRÍTICO. Habilita el camino para {impacto} materias futuras."
            
            alertas.append(Alerta(
                tipo=TipoAlerta.CUELLO_DE_BOTELLA,
                mensaje=mensaje,
                materia_uri=materia["uri"],
                materia_label=materia["label"]
            ))
            
    return alertas

def generar_alertas_proactivas(user: User, kg: Graph) -> list[Alerta]:
    materias_regulares = [m for m in user.materias_cursadas if m.estado == "Regular"]
    alertas_regularidad = _check_riesgo_regularidad(user, materias_regulares, kg)
    alertas_cuello_botella = _check_cuellos_de_botella(user, kg)
    
    return alertas_regularidad + alertas_cuello_botella