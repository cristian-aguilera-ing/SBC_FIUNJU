
import sys
import os
print("Starting script...", flush=True)
sys.path.append(os.path.join(os.getcwd(), 'backend'))
try:
    from rdflib import Graph
    print("Imported rdflib", flush=True)
    from app.services.recomendacion_service import generar_plan_cursada_optimo
    print("Imported service", flush=True)
except Exception as e:
    print(f"Import Error: {e}", flush=True)
    sys.exit(1)
from app.models.user import User, MateriaCursada
from app.models.enums import CondicionLaboral

# Mock User
class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "test@test.com"
        self.full_name = "Test User"
        self.condicion_laboral = CondicionLaboral.MEDIO_TIEMPO
        self.es_del_interior = False
        self.vive_solo = False
        self.tiene_hijos = False
        # Profile 4: Equilibrado
        self.materias_cursadas = []

# Mock Materias
def add_materia(user, uri, estado="Aprobada"):
    m = MateriaCursada()
    m.materia_uri = uri
    m.estado = estado
    user.materias_cursadas.append(m)

# Load Ontology
print("Loading ontology...")
g = Graph()
try:
    g.parse("ontologies/fiunju_ontologia_GENERADA.ttl", format="turtle")
    print(f"Ontology loaded with {len(g)} triples.")
except Exception as e:
    print(f"Error loading ontology: {e}")
    sys.exit(1)

# Test
user = MockUser()
# Add some approved subjects (prerequisites)
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#AnalisisMatematicoI", "Aprobada")
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#AlgebraGeometriaAnalitica", "Aprobada")
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#ProgramacionI", "Aprobada")

# Scenario: 2 Muy Dificiles + 2 Faciles
# MD: AnalisisMatematicoII (Dif 4), FisicaMecanica (Dif 4)
# F: Ingles (Dif 2 - wait, Facil is 1?), Logica (Dif 1)
# Let's check ontology for difficulties or just trust the script will pick up what's there.
# We'll use known URIs.
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#AnalisisMatematicoII", "Cursando") # MD
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#FisicaMecanica", "Cursando") # MD
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#NivelSuficienciaIngles", "Cursando") # F/N
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#LogicaComputacional", "Cursando") # F

print("Calling generar_plan_cursada_optimo...")
try:
    plan = generar_plan_cursada_optimo(user, g)
    print("Success!")
    print(f"Arquetipo: {plan['arquetipo']['nombre']}")
    print(f"Plan Seleccionado: {plan['consejos_adicionales'][0]}")
    
    print("\n[PLAN RECOMENDADO]")
    for m in plan['plan_recomendado']:
        print(f"- {m['label']} (Dif: {m['dificultad_label']})")
        
    print("\n[OMITIDAS / POSTERGAR]")
    for m in plan['materias_omitidas']:
        print(f"- {m['label']} (Dif: {m['dificultad_label']})")
        
except Exception as e:
    print("CRASH DETECTED!")
    import traceback
    traceback.print_exc()
