
import sys
import os
from rdflib import Graph
from app.services.recomendacion_service import generar_estrategia_examenes
from app.models.user import User, MateriaCursada
from app.models.enums import CondicionLaboral, EstadoMateria

# Mock User
class MockUser:
    def __init__(self):
        self.id = 1
        self.email = "test@test.com"
        self.full_name = "Test User"
        self.condicion_laboral = CondicionLaboral.TIEMPO_COMPLETO
        self.es_del_interior = True # Perfil Critico
        self.vive_solo = True
        self.tiene_hijos = True
        self.creditos_totales = 0
        self.tiene_cuarto_ano_aprobado = False
        self.materias_cursadas = []

# Mock Materias (PreparandoFinal)
def add_materia(user, uri, estado="PreparandoFinal"):
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
# Add some finals
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#SistOpI") # Dificil (4)
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#SistInf") # Normal (2)
add_materia(user, "http://fi.unju.edu.ar/ontologia/informatica#IngSoft") # Normal (2)

print("Calling generar_estrategia_examenes...")
try:
    plan = generar_estrategia_examenes(user, g)
    print("Success!")
    print(f"Plan: {plan['consejos_adicionales'][0]}")
    print("Recomendados:")
    for m in plan['plan_recomendado']:
        if m['esta_habilitada']:
            print(f"- {m['label']} ({m['dificultad_examen_label']})")
except Exception as e:
    print("CRASH DETECTED!")
    import traceback
    traceback.print_exc()
