import sys
from rdflib import Graph
from app.services.recomendacion_service import generar_plan_cursada_optimo, DIAGNOSTICOS_HARDCODED
from app.models.user import User, UserMateria
from app.core.knowledge_base import load_knowledge_base

# Mock User class
class MockUser:
    def __init__(self, id, email, materias_cursadas, condicion_laboral, horas_estudio, vive_con_padres, hijos):
        self.id = id
        self.email = email
        self.materias_cursadas = materias_cursadas
        self.condicion_laboral = condicion_laboral
        self.horas_estudio = horas_estudio
        self.vive_con_padres = vive_con_padres
        self.hijos = hijos

# Mock UserMateria class
class MockUserMateria:
    def __init__(self, materia_uri, estado):
        self.materia_uri = materia_uri
        self.estado = estado

def test_reproduction():
    print("Loading Knowledge Base...")
    try:
        kg = load_knowledge_base()
    except Exception as e:
        print(f"Error loading KB: {e}")
        kg = Graph()
        kg.parse("ontologies/fiunju_ontologia_GENERADA.ttl", format="turtle")

    print(f"KB Loaded. Triples: {len(kg)}")

    # --- Test Case: Super Alto Profile with Mixed Selection ---
    # Profile Logic for Super Alto (ID 6):
    # No trabaja, Vive en Capital, No vive solo, No tiene hijos.
    print("\n--- Test Case: Arquetipo Super Alto ---")
    
    # Subjects selected by user (from screenshot/description):
    # - Analisis Matematico II (Nivel 4)
    # - Fisica Mecanica (Nivel 4)
    # - Estructura de Datos (Nivel 1)
    # - Metodologia de la Programacion (Nivel 1)
    
    user_super_alto = MockUser(
        id=1,
        email="superalto@test.com",
        materias_cursadas=[
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#AnalMatemII", "Cursando"),
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#FisicaMec", "Cursando"),
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#EstDatos", "Cursando"),
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#MetProg", "Cursando"),
            # Add some approved prereqs to ensure they are valid
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#AnalMatemI", "Aprobada"),
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#AlgebraLineal", "Aprobada"),
            MockUserMateria("http://fi.unju.edu.ar/ontologia/informatica#IntroProg", "Aprobada"),
        ],
        condicion_laboral="No trabaja",
        horas_estudio=40, 
        vive_con_padres=True, 
        hijos=False
    )
    
    # Force profile ID detection check (optional, but good to know)
    from app.core.perfiles_pdf import obtener_perfil_id
    pid = obtener_perfil_id(user_super_alto)
    print(f"Detected Profile ID: {pid} (Expected 6 for Super Alto)")

    # Run Recommendation
    plan = generar_plan_cursada_optimo(user_super_alto, kg)
    
    print(f"\nDiagnostic: {plan['arquetipo']['diagnostico']}")
    print(f"Strategy Description: {plan['consejos_adicionales'][0]}")
    
    print("\nRecommended Subjects:")
    for m in plan['plan_recomendado']:
        print(f" - {m['label']} (Dif: {m['dificultad']})")
        
    print("\nOmitted Subjects:")
    for m in plan['materias_omitidas']:
        print(f" - {m['label']} (Dif: {m['dificultad']})")

    # Check Diagnostic Keys
    print("\n--- Diagnostic Keys Check ---")
    arquetipo_uri_map = {
        6: "ArquetipoSuperAlto"
    }
    uri = arquetipo_uri_map.get(pid)
    print(f"Archetype URI: {uri}")
    print(f"Key in Hardcoded: {uri in DIAGNOSTICOS_HARDCODED}")
    if uri in DIAGNOSTICOS_HARDCODED:
        print(f"Hardcoded Value: {DIAGNOSTICOS_HARDCODED[uri]}")

if __name__ == "__main__":
    with open("reproduce_results.txt", "w") as f:
        sys.stdout = f
        sys.stderr = f
        try:
            test_reproduction()
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
