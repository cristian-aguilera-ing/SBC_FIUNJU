import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from app.services.recomendacion_service import generar_estrategia_examenes
from app.models.user import User, UserMateria
from app.models.enums import CondicionLaboral
from rdflib import Graph, Namespace, Literal, URIRef

# Mock User
def create_mock_user(profile_id):
    user = User(
        id=1,
        email="test@test.com",
        full_name="Test User",
        materias_cursadas=[],
        condicion_laboral=CondicionLaboral.TIEMPO_COMPLETO, # Default Profile 1 conditions
        es_del_interior=True,
        vive_solo=True,
        tiene_hijos=True
    )
    return user

# Mock Graph
def create_mock_graph():
    g = Graph()
    FIUNJU = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    
    # Define some subjects with difficulties
    subjects = [
        {"uri": "MateriaFacil", "label": "Materia Facil", "dificultad": 1},
        {"uri": "MateriaNormal", "label": "Materia Normal", "dificultad": 2},
        {"uri": "MateriaDificil", "label": "Materia Dificil", "dificultad": 3},
        {"uri": "MateriaMuyDificil", "label": "Materia Muy Dificil", "dificultad": 4},
    ]
    
    for s in subjects:
        m_uri = URIRef(FIUNJU[s["uri"]])
        g.add((m_uri, RDFS.label, Literal(s["label"])))
        
        # Add difficulty exam
        dif_node = URIRef(FIUNJU[f"Dificultad{s['dificultad']}"])
        mod_node = URIRef(FIUNJU[f"Modalidad{s['uri']}"])
        
        g.add((m_uri, FIUNJU.tieneModalidadExamen, mod_node))
        g.add((mod_node, RDFS.label, Literal("Escrito"))) # Added label
        g.add((mod_node, FIUNJU.tieneDificultadExamen, dif_node))
        g.add((dif_node, FIUNJU.tieneValor, Literal(s["dificultad"])))
        g.add((dif_node, RDFS.label, Literal(f"Dificultad {s['dificultad']}")))
        
    return g

def test_plan_selection():
    g = create_mock_graph()
    user = create_mock_user(1) # Profile 1
    
    # Case 1: Plan A (Normal available)
    user.materias_cursadas = [
        UserMateria(id=1, materia_uri="http://fi.unju.edu.ar/ontologia/informatica#MateriaNormal", estado="PreparandoFinal")
    ]
    
    result = generar_estrategia_examenes(user, g)
    print(f"Case 1 (Normal) -> Plan Text: {result['consejos_adicionales'][0]}")
    assert "Plan A" in result['consejos_adicionales'][0]
    # Verify that the Normal subject is enabled (esta_habilitada=True)
    normal_subject = next(m for m in result['plan_recomendado'] if m['dificultad_examen_valor'] == 2)
    assert normal_subject['esta_habilitada'] == True
    print("Plan A: Normal subject is enabled.")
    
    # Case 2: Plan B (Hard available)
    user.materias_cursadas = [
        UserMateria(id=1, materia_uri="http://fi.unju.edu.ar/ontologia/informatica#MateriaDificil", estado="PreparandoFinal")
    ]
    
    result = generar_estrategia_examenes(user, g)
    print(f"Case 2 (Hard) -> Plan Text: {result['consejos_adicionales'][0]}")
    assert "Plan B" in result['consejos_adicionales'][0]
    # Verify that the Hard subject is enabled (esta_habilitada=True)
    hard_subject = next(m for m in result['plan_recomendado'] if m['dificultad_examen_valor'] == 3)
    assert hard_subject['esta_habilitada'] == True
    print("Plan B: Hard subject is enabled.")

    # Case 3: Plan C (Very Hard available)
    user.materias_cursadas = [
        UserMateria(id=1, materia_uri="http://fi.unju.edu.ar/ontologia/informatica#MateriaMuyDificil", estado="PreparandoFinal")
    ]
    
    result = generar_estrategia_examenes(user, g)
    print(f"Case 3 (Very Hard) -> Plan Text: {result['consejos_adicionales'][0]}")
    assert "Plan C" in result['consejos_adicionales'][0]
    # Verify that the Very Hard subject is enabled (esta_habilitada=True)
    very_hard_subject = next(m for m in result['plan_recomendado'] if m['dificultad_examen_valor'] == 4)
    assert very_hard_subject['esta_habilitada'] == True
    print("Plan C: Very Hard subject is enabled.")
    
    print("All tests passed!")

if __name__ == "__main__":
    test_plan_selection()
