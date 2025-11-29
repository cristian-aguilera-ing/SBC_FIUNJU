from rdflib import Graph, Literal, Namespace

g = Graph()
fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
g.bind("fiunju", fiunju)

g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneTarjetaDiagnostico, Literal("Test Diagnostico", lang="es")))

query = """
PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
SELECT ?diagnostico WHERE {
    fiunju:ArquetipoEquilibrado fiunju:tieneTarjetaDiagnostico ?diagnostico .
}
"""

print("Running query...")
results = list(g.query(query))
print(f"Results: {len(results)}")
for row in results:
    print(f"Diagnostico: {row.diagnostico}")
    print(f"Str: {str(row.diagnostico)}")
