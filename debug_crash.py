
import sys
import os
from rdflib import Graph
from app.services.recomendacion_service import generar_plan_cursada_optimo
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
print("Calling generar_plan_cursada_optimo...")
try:
    plan = generar_plan_cursada_optimo(user, g)
    print("Success!")
    print(plan)
except Exception as e:
    print("CRASH DETECTED!")
    print(e)
    import traceback
    traceback.print_exc()
