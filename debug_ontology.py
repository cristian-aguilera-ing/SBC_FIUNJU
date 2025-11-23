from rdflib import Graph

def load_knowledge_base():
    g = Graph()
    g.parse("ontologies/fiunju_ontologia_GENERADA.ttl", format="turtle")
    return g

kg = load_knowledge_base()
query_str = """
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?materia ?label ?requisito ?req_label
        WHERE {
            ?materia a fiunju:Materia ; rdfs:label ?label .
            OPTIONAL {
                ?materia fiunju:tieneRequisito ?requisito .
                OPTIONAL { ?requisito rdfs:label ?req_label }
                FILTER NOT EXISTS {
                    ?materia fiunju:tieneRequisito ?mid .
                    ?mid fiunju:tieneRequisito ?requisito
                }
            }
            FILTER (REGEX(STR(?label), "Arquitectura de Computadoras Paralelas", "i"))
        }
        ORDER BY ?label
"""

results = kg.query(query_str)
for row in results:
    print(f"Materia: {row.label}")
    print(f"  Requisito URI: {row.requisito}")
    print(f"  Requisito Label: {row.req_label}")
