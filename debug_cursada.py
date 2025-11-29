
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from rdflib import Graph
from app.core.perfiles_pdf import PERFILES_DATA

# Load Ontology
print("Loading ontology...")
g = Graph()
try:
    g.parse("ontologies/fiunju_ontologia_GENERADA.ttl", format="turtle")
    print(f"Ontology loaded with {len(g)} triples.")
except Exception as e:
    print(f"Error loading ontology: {e}")
    sys.exit(1)

# Test for Profile 4 (Equilibrado) as seen in user screenshot (implied by context)
# Or just test all profiles
for pid, data in PERFILES_DATA.items():
    # URI Mapping
    ARQUETIPO_URIS = {
        1: "ArquetipoCritico",
        2: "ArquetipoBajo",
        3: "ArquetipoMedioBajo",
        4: "ArquetipoEquilibrado",
        5: "ArquetipoMedioAlto",
        6: "ArquetipoSuperAlto",
        7: "ArquetipoAtipico"
    }
    arquetipo_uri = ARQUETIPO_URIS.get(pid, "ArquetipoEquilibrado")
    print(f"Testing Profile {pid}: {nombre_arquetipo} (URI: fiunju:{arquetipo_uri})")

    query_estrategias = f"""
    PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?orden ?desc ?cant ?minReq ?difValor
    WHERE {{
        fiunju:{arquetipo_uri} fiunju:tieneEstrategiaPosible ?est .
        
        ?est fiunju:ordenPrioridad ?orden ;
             fiunju:descripcionPlan ?desc ;
             fiunju:cantidadMaterias ?cant ;
             fiunju:cantidadMinimaRequerida ?minReq .
             
        OPTIONAL {{ 
            ?est fiunju:requiereDisponibilidadDe ?difNode .
            ?difNode fiunju:tieneValor ?difValor .
        }}
    }}
    ORDER BY ?orden
    """
    
    results = list(g.query(query_estrategias))
    print(f"Found {len(results)} strategies for {nombre_arquetipo}.")
    for row in results:
        print(f" - Plan: {row.desc} (MinReq: {row.minReq}, Dif: {row.difValor})")
