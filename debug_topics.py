from rdflib import Graph, Namespace, RDF, RDFS
from pathlib import Path
import owlrl

def debug_ontology():
    base_path = Path(".").resolve()
    ontology_file_path = base_path / "backend/ontologies/fiunju_ontologia_GENERADA.ttl"
    
    if not ontology_file_path.exists():
        print(f"File not found: {ontology_file_path}")
        return

    g = Graph()
    g.parse(ontology_file_path, format="turtle")
    print(f"Loaded {len(g)} triplets.")
    
    # Run reasoning
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    print(f"Reasoning complete. Total triplets: {len(g)}")

    fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    
    query = """
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?topico ?label ?es_final
        WHERE {
            ?topico rdfs:label ?label .
            
            # New Logic: Check if ANY type is a subclass of TopicoDeFinal
            BIND(EXISTS { 
                ?topico rdf:type ?clase .
                ?clase rdfs:subClassOf* fiunju:TopicoDeFinal 
            } AS ?es_final)
        }
    """
    
    results = g.query(query)
    
    print(f"{'Label':<40} | {'Es Final?':<10}")
    print("-" * 60)
    seen = set()
    for row in results:
        label = str(row.label)
        es_final = row.es_final
        
        if label in seen: continue
        seen.add(label)

        if "Tips Multiple Choice" in label or "Unidad" in label or "Estrategia" in label:
             print(f"{label:<40} | {es_final:<10}")

if __name__ == "__main__":
    debug_ontology()
