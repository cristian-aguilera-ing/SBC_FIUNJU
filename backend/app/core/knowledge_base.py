from rdflib import Graph
import owlrl
from pathlib import Path

def load_knowledge_base() -> Graph:
    """
    Crea un nuevo grafo, lo carga desde el archivo,
    lo razona y lo DEVUELVE.
    """
    g = Graph()
    
    # Apunta al archivo que 'generar_ontologia.py' crea
    # Usamos path relativo para que funcione local y en docker
    base_path = Path(__file__).resolve().parent.parent.parent
    ontology_file_path = base_path / "ontologies" / "fiunju_ontologia_GENERADA.ttl"
    
    try:
        print(f"Intentando cargar ontología desde: {ontology_file_path}")
        
        if not Path(ontology_file_path).is_file():
            print(f"ERROR FATAL: ¡El archivo no existe! {ontology_file_path}")
            print("Por favor, ejecuta 'python backend/generar_ontologia.py' primero.")
            return g # Devuelve el grafo vacío

        g.parse(ontology_file_path, format="turtle")
        print(f"Ontología cargada exitosamente.")
        
        print("Ejecutando razonador OWL (verificación)...")
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
        print("Razonamiento completado.")
        
    except Exception as e:
        print(f"Error al cargar/razonar la ontología: {e}")
    
    return g