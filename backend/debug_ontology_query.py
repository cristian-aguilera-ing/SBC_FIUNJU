from rdflib import Graph, Namespace

def debug_query():
    g = Graph()
    ontology_path = "ontologies/fiunju_ontologia_GENERADA.ttl"
    print(f"Loading ontology from {ontology_path}...")
    g.parse(ontology_path, format="turtle")
    print(f"Graph loaded with {len(g)} triples.")

    fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    
    # Test with ArquetipoEquilibrado as seen in user's screenshot
    arquetipo_id = "ArquetipoEquilibrado"
    
    query = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    SELECT ?est ?diagnostico ?consejo WHERE {{
        OPTIONAL {{ fiunju:{arquetipo_id} fiunju:tieneEstrategiaPosible ?est . }}
        OPTIONAL {{ fiunju:{arquetipo_id} fiunju:tieneTarjetaDiagnostico ?diagnostico . }}
        OPTIONAL {{ fiunju:{arquetipo_id} fiunju:tieneConsejoClave ?consejo . }}
    }}
    """
    
    print(f"Executing query for {arquetipo_id}...")
    results = list(g.query(query))
    
    if not results:
        print("No results found.")
    else:
        print(f"Found {len(results)} rows.")
        for i, row in enumerate(results):
            print(f"Row {i}:")
            print(f"  Estrategia: {row.est}")
            print(f"  Diagnostico: {row.diagnostico}")
            print(f"  Consejo: {row.consejo}")

if __name__ == "__main__":
    debug_query()
