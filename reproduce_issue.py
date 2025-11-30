import sys
import os
sys.path.append(os.path.abspath("backend"))
print("Script started", file=sys.stderr)

try:
    from rdflib import Graph
    print("rdflib imported", file=sys.stderr)
    from app.services.recomendacion_service import generar_plan_cursada_optimo
    print("service imported", file=sys.stderr)
    from app.models.user import User, UserMateria
    from app.core.knowledge_base import load_knowledge_base
except Exception as e:
    print(f"Import Error: {e}", file=sys.stderr)
    sys.exit(1)

# Mock User
class MockUser:
    def __init__(self, id, email, materias_cursadas):
        self.id = id
        self.email = email
        self.materias_cursadas = materias_cursadas
        self.perfil_personal = None
        self.perfil_academico = None
        self.perfil_test_result = None

# Mock UserMateria
class MockUserMateria:
    def __init__(self, uri, estado):
        self.materia_uri = uri
        self.estado = estado

def reproduce():
    print("Loading Knowledge Base...", file=sys.stderr)
    kg = load_knowledge_base()
    print("KB Loaded", file=sys.stderr)

    
    # Define subjects (URIs)
    # Level 4
    analisis_ii = "http://fi.unju.edu.ar/ontologia/informatica#AnalMatemII"
    fisica_mec = "http://fi.unju.edu.ar/ontologia/informatica#FisicaMec"
    # Level 1
    est_datos = "http://fi.unju.edu.ar/ontologia/informatica#EstDatos"
    met_prog = "http://fi.unju.edu.ar/ontologia/informatica#MetProg"
    # Requisites (Approved)
    analisis_i = "http://fi.unju.edu.ar/ontologia/informatica#AnalMatemI"
    algebra = "http://fi.unju.edu.ar/ontologia/informatica#AlgebraLineal"
    intro_prog = "http://fi.unju.edu.ar/ontologia/informatica#IntroProg"

    # User with 4 subjects marked as "Cursando"
    # And requisites approved
    materias = [
        MockUserMateria(analisis_i, "Aprobada"),
        MockUserMateria(algebra, "Aprobada"),
        MockUserMateria(intro_prog, "Aprobada"),
        
        MockUserMateria(analisis_ii, "Cursando"),
        MockUserMateria(fisica_mec, "Cursando"),
        MockUserMateria(est_datos, "Cursando"),
        MockUserMateria(met_prog, "Cursando")
    ]
    
    # Profile ID 4 (Equilibrado) is derived from user data in the real app, 
    # but here we need to ensure `obtener_perfil_id` returns 4.
    # We can mock `obtener_perfil_id` or just rely on the service using the user.
    # Let's mock the user to have the right attributes if needed, 
    # but `generar_plan_cursada_optimo` calls `obtener_perfil_id`.
    # Let's patch `obtener_perfil_id` in the service for simplicity.
    
    user = MockUser(1, "test@test.com", materias)
    
    print("Generating Plan...")
    # We need to patch obtener_perfil_id to return 4 (Equilibrado)
    import app.services.recomendacion_service as service
    original_obtener = service.obtener_perfil_id
    service.obtener_perfil_id = lambda u: 4
    
    try:
        plan = service.generar_plan_cursada_optimo(user, kg)
        
        print(f"\nRecommended Strategy: {plan['consejos_adicionales'][0]}")
        print(f"Number of subjects in plan: {len(plan['plan_recomendado'])}")
        print("Subjects:")
        for m in plan['plan_recomendado']:
            print(f"- {m['label']} (Diff: {m['dificultad']})")
            
        if len(plan['plan_recomendado']) > 2:
            print("\nFAIL: Plan has more than 2 subjects, but Strategy likely specifies 2.")
        else:
            print("\nSUCCESS: Plan filtered correctly.")
            
    finally:
        service.obtener_perfil_id = original_obtener

if __name__ == "__main__":
    reproduce()
