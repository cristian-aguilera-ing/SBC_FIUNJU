
from rdflib import Graph, Namespace
import sys

def test_ontology():
    g = Graph()
    try:
        g.parse("ontologies/fiunju_ontologia_GENERADA.ttl", format="turtle")
    except Exception as e:
        print(f"Error loading ontology: {e}")
        return

    fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    
    # Test get_topicos_for_materia for SistOpI
    materia_uri = "http://fi.unju.edu.ar/ontologia/informatica#SistOpI"
    query_str = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?topico ?label
            WHERE {{
                BIND(<{materia_uri}> AS ?materia) .
                ?materia fiunju:tieneTopicoRelevante ?topico .
                ?topico rdfs:label ?label .
            }}
    """
    results = g.query(query_str)
    print(f"Topics for {materia_uri}:")
    for row in results:
        print(f"URI: {row.topico}, Label: {row.label}")

    # Test getting description for a specific topic instance
    # Let's pick one from the results if any, or use a known one
    topic_uri = "http://fi.unju.edu.ar/ontologia/informatica#Consejo_SistOp_Vidas"
    query_desc = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        SELECT ?descripcion
        WHERE {{
            <{topic_uri}> fiunju:descripcion ?descripcion .
        }}
    """
    results_desc = g.query(query_desc)
    print(f"\nDescription for {topic_uri}:")
    for row in results_desc:
        print(f"{row.descripcion}")

if __name__ == "__main__":
    test_ontology()
