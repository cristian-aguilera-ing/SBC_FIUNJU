import rdflib
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL, XSD
import owlrl
from pathlib import Path

print("--- INICIANDO SCRIPT DE GENERACIÓN DE ONTOLOGÍA ---")

# --- 1. Inicialización del Grafo y Namespaces ---
g = Graph()
fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
g.bind("fiunju", fiunju)
g.bind("rdf", RDF)
g.bind("rdfs", RDFS)
g.bind("owl", OWL)
g.bind("xsd", XSD)

# --- 2. Definición del Esquema (TBox) ---
g.add((fiunju.Materia, RDF.type, RDFS.Class))
g.add((fiunju.ModalidadExamenFinal, RDF.type, RDFS.Class))
g.add((fiunju.NivelDificultadCursada, RDF.type, RDFS.Class))
g.add((fiunju.NivelDificultadExamen, RDF.type, RDFS.Class))
g.add((fiunju.TopicoDeConsejo, RDF.type, RDFS.Class))
g.add((fiunju.ArquetipoEstudiante, RDF.type, RDFS.Class))
g.add((fiunju.EstrategiaRecomendacion, RDF.type, RDFS.Class))
g.add((fiunju.CondicionDisponibilidad, RDF.type, RDFS.Class))
g.add((fiunju.ComponentePlan, RDF.type, RDFS.Class))

g.add((fiunju.Optativa, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.Obligatoria, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.MateriaDeAltoEsfuerzo, RDFS.subClassOf, fiunju.Materia))

# Properties
g.add((fiunju.esRequisitoPara, RDF.type, OWL.ObjectProperty))
g.add((fiunju.esRequisitoPara, RDF.type, OWL.TransitiveProperty))
g.add((fiunju.tieneRequisito, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneRequisito, OWL.inverseOf, fiunju.esRequisitoPara))
g.add((fiunju.tieneModalidadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadCursada, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.esMasDificilQue, RDF.type, OWL.ObjectProperty))
g.add((fiunju.esMasDificilQue, RDF.type, OWL.TransitiveProperty))
g.add((fiunju.tieneTopicoRelevante, RDF.type, OWL.ObjectProperty))

g.add((fiunju.tieneEstrategiaPosible, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneEstrategiaPosible, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneEstrategiaPosible, RDFS.range, fiunju.EstrategiaRecomendacion))

g.add((fiunju.tieneCondicion, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneCondicion, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.tieneCondicion, RDFS.range, fiunju.CondicionDisponibilidad))

g.add((fiunju.requiereNivel, RDF.type, OWL.ObjectProperty))
g.add((fiunju.requiereNivel, RDFS.domain, fiunju.CondicionDisponibilidad))
g.add((fiunju.requiereNivel, RDFS.range, fiunju.NivelDificultadCursada))

g.add((fiunju.tieneComponente, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneComponente, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.tieneComponente, RDFS.range, fiunju.ComponentePlan))

g.add((fiunju.sugerirNivel, RDF.type, OWL.ObjectProperty))
g.add((fiunju.sugerirNivel, RDFS.domain, fiunju.ComponentePlan))
g.add((fiunju.sugerirNivel, RDFS.range, fiunju.NivelDificultadCursada))


# Data Properties
g.add((fiunju.perteneceAlAño, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneValor, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.otorgaCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCuartoAnoAprobado, RDF.type, OWL.DatatypeProperty))

g.add((fiunju.tieneNombreArquetipo, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneColorIdentificativo, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneConsejoBase, RDF.type, OWL.DatatypeProperty))

g.add((fiunju.ordenPrioridad, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.ordenPrioridad, RDFS.range, XSD.integer))
g.add((fiunju.descripcionPlan, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.cantidadMinimaRequerida, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.cantidadMinimaRequerida, RDFS.range, XSD.integer))
g.add((fiunju.sugerirCantidad, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.sugerirCantidad, RDFS.range, XSD.integer))

# --- Individuos: Niveles ---
niveles_cursada_data = {
    "Nivel_4": {"label": "Muy difícil", "valor": 4},
    "Nivel_3": {"label": "Difícil", "valor": 3},
    "Nivel_2": {"label": "Normal", "valor": 2},
    "Nivel_1": {"label": "Fácil", "valor": 1},
}
for k, v in niveles_cursada_data.items():
    u = fiunju[k]
    g.add((u, RDF.type, fiunju.NivelDificultadCursada))
    g.add((u, RDFS.label, Literal(v["label"], lang="es")))
    g.add((u, fiunju.tieneValor, Literal(v["valor"], datatype=XSD.integer)))

def crear_estrategia(uri_suffix, prioridad, descripcion, condiciones, acciones):
    est_uri = fiunju[uri_suffix]
    g.add((est_uri, RDF.type, fiunju.EstrategiaRecomendacion))
    g.add((est_uri, fiunju.ordenPrioridad, Literal(prioridad, datatype=XSD.integer)))
    g.add((est_uri, fiunju.descripcionPlan, Literal(descripcion, lang="es")))

    for i, (nivel_uri, min_qty) in enumerate(condiciones):
        cond_uri = fiunju[f"{uri_suffix}_cond_{i}"]
        g.add((cond_uri, RDF.type, fiunju.CondicionDisponibilidad))
        if nivel_uri:
            g.add((cond_uri, fiunju.requiereNivel, nivel_uri))
        g.add((cond_uri, fiunju.cantidadMinimaRequerida, Literal(min_qty, datatype=XSD.integer)))
        g.add((est_uri, fiunju.tieneCondicion, cond_uri))

    for i, (nivel_uri, qty) in enumerate(acciones):
        comp_uri = fiunju[f"{uri_suffix}_comp_{i}"]
        g.add((comp_uri, RDF.type, fiunju.ComponentePlan))
        g.add((comp_uri, fiunju.sugerirNivel, nivel_uri))
        g.add((comp_uri, fiunju.sugerirCantidad, Literal(qty, datatype=XSD.integer)))
        g.add((est_uri, fiunju.tieneComponente, comp_uri))

# --- Arquetipos ---
# 1. Superviviente
arq = fiunju.ArquetipoSuperviviente
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Superviviente")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("red")))
g.add((arq, fiunju.tieneConsejoBase, Literal("Usa Pomodoro.")))

crear_estrategia("Est_Superviviente_A", 1, "Plan A: 2 Materias Fáciles", [(fiunju.Nivel_1, 2)], [(fiunju.Nivel_1, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Superviviente_A))
crear_estrategia("Est_Superviviente_B", 2, "Plan B: 1 Materia Normal", [(fiunju.Nivel_2, 1)], [(fiunju.Nivel_2, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Superviviente_B))
crear_estrategia("Est_Superviviente_C", 3, "Plan C: 1 Materia Difícil", [(fiunju.Nivel_3, 1)], [(fiunju.Nivel_3, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Superviviente_C))
crear_estrategia("Est_Superviviente_D", 4, "Plan D: 1 Materia Muy Difícil", [(fiunju.Nivel_4, 1)], [(fiunju.Nivel_4, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Superviviente_D))

# 2. Malabarista
arq = fiunju.ArquetipoMalabarista
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Malabarista Urbano")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("orange")))
crear_estrategia("Est_Malabarista_A", 1, "Plan A: 1 Difícil + 2 Normales", [(fiunju.Nivel_3, 1), (fiunju.Nivel_2, 2)], [(fiunju.Nivel_3, 1), (fiunju.Nivel_2, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Malabarista_A))
crear_estrategia("Est_Malabarista_B", 2, "Plan B: 3 Normales", [(fiunju.Nivel_2, 3)], [(fiunju.Nivel_2, 3)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Malabarista_B))
crear_estrategia("Est_Malabarista_C", 3, "Plan C: 2 Difíciles", [(fiunju.Nivel_3, 2)], [(fiunju.Nivel_3, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Malabarista_C))
crear_estrategia("Est_Malabarista_D", 4, "Plan D: 1 Muy Difícil + 1 Fácil", [(fiunju.Nivel_4, 1), (fiunju.Nivel_1, 1)], [(fiunju.Nivel_4, 1), (fiunju.Nivel_1, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Malabarista_D))

# 3. Guerrero
arq = fiunju.ArquetipoGuerrero
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Guerrero Solitario")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("yellow")))
crear_estrategia("Est_Guerrero_A", 1, "Plan A: 2 Fáciles", [(fiunju.Nivel_1, 2)], [(fiunju.Nivel_1, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Guerrero_A))
crear_estrategia("Est_Guerrero_B", 2, "Plan B: 2 Normales", [(fiunju.Nivel_2, 2)], [(fiunju.Nivel_2, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Guerrero_B))
crear_estrategia("Est_Guerrero_C", 3, "Plan C: 1 Difícil", [(fiunju.Nivel_3, 1)], [(fiunju.Nivel_3, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Guerrero_C))
crear_estrategia("Est_Guerrero_D", 4, "Plan D: 1 Muy Difícil", [(fiunju.Nivel_4, 1)], [(fiunju.Nivel_4, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Guerrero_D))

# 4. Equilibrado
arq = fiunju.ArquetipoEquilibrado
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Equilibrado")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("green")))
crear_estrategia("Est_Equilibrado_A", 1, "Plan A: 1 Muy Difícil + 1 Difícil + 1 Normal", [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 1), (fiunju.Nivel_2, 1)], [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 1), (fiunju.Nivel_2, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_A))
crear_estrategia("Est_Equilibrado_B", 2, "Plan B: 1 Muy Difícil + 1 Difícil", [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 1)], [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_B))
crear_estrategia("Est_Equilibrado_C", 3, "Plan C: 3 Normales", [(fiunju.Nivel_2, 3)], [(fiunju.Nivel_2, 3)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_C))
crear_estrategia("Est_Equilibrado_D", 4, "Plan D: 2 Muy Difíciles", [(fiunju.Nivel_4, 2)], [(fiunju.Nivel_4, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_D))

# 5. Ermitaño
arq = fiunju.ArquetipoErmitano
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Ermitaño del Interior")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("blue")))
crear_estrategia("Est_Ermitano_A", 1, "Plan A: 2 Muy Dif + 2 Fáciles", [(fiunju.Nivel_4, 2), (fiunju.Nivel_1, 2)], [(fiunju.Nivel_4, 2), (fiunju.Nivel_1, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Ermitano_A))
crear_estrategia("Est_Ermitano_B", 2, "Plan B: 1 Muy Dif + 2 Dif", [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 2)], [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Ermitano_B))
crear_estrategia("Est_Ermitano_C", 3, "Plan C: 2 Normales + 2 Fáciles", [(fiunju.Nivel_2, 2), (fiunju.Nivel_1, 2)], [(fiunju.Nivel_2, 2), (fiunju.Nivel_1, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Ermitano_C))
crear_estrategia("Est_Ermitano_D", 4, "Plan D: 3 Difíciles", [(fiunju.Nivel_3, 3)], [(fiunju.Nivel_3, 3)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Ermitano_D))

# 6. Heredero
arq = fiunju.ArquetipoHeredero
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Heredero del Trono")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("violet")))
crear_estrategia("Est_Heredero_A", 1, "Plan A: 3 Muy Dif + 1 Dif", [(fiunju.Nivel_4, 3), (fiunju.Nivel_3, 1)], [(fiunju.Nivel_4, 3), (fiunju.Nivel_3, 1)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Heredero_A))
# Plan B (Mix)
crear_estrategia("Est_Heredero_B", 2, "Plan B: Mix Balanceado (5 Materias)", [], [(fiunju.Nivel_4, 1), (fiunju.Nivel_3, 1), (fiunju.Nivel_2, 1), (fiunju.Nivel_1, 2)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Heredero_B))
crear_estrategia("Est_Heredero_C", 3, "Plan C: Carga máxima de materias fáciles", [(fiunju.Nivel_1, 1)], [(fiunju.Nivel_1, 5)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Heredero_C))
crear_estrategia("Est_Heredero_D", 4, "Plan D: 3 Muy Difíciles", [(fiunju.Nivel_4, 3)], [(fiunju.Nivel_4, 3)])
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Heredero_D))

# 7. Padre
arq = fiunju.ArquetipoPadreFullTime
g.add((arq, RDF.type, fiunju.ArquetipoEstudiante))
g.add((arq, fiunju.tieneNombreArquetipo, Literal("El Padre/Madre Full-Time")))
g.add((arq, fiunju.tieneColorIdentificativo, Literal("brown")))
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_A))
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_B))
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_C))
g.add((arq, fiunju.tieneEstrategiaPosible, fiunju.Est_Equilibrado_D))

# --- Materias ---
# Adding just a few critical ones to keep file size small for this tool call,
# assuming previous tool call failure was size related.
# Wait, I must include all materias or the recommendation won't work.
# I will try to include all of them in a compressed format.


def add_materia(id, label, anio, dif, reqs=[], modalidad=None, creditos=None, cuarto_aprobado=False):
    uri = fiunju[id]
    g.add((uri, RDF.type, fiunju.Obligatoria)) # Default to Obligatoria
    g.add((uri, RDFS.label, Literal(label, lang="es")))
    g.add((uri, fiunju.perteneceAlAño, Literal(anio, datatype=XSD.integer)))
    if dif:
        g.add((uri, fiunju.tieneDificultadCursada, fiunju[dif]))
    for r in reqs:
        g.add((uri, fiunju.tieneRequisito, fiunju[r]))
    if modalidad:
        g.add((uri, fiunju.tieneModalidadExamen, fiunju[modalidad]))
    if creditos:
        g.add((uri, fiunju.otorgaCreditos, Literal(creditos, datatype=XSD.integer)))
        # Assuming otorgaCreditos is what we meant. The previous file had 'requiereCreditos' for some.
        # Let's support both.
    if cuarto_aprobado:
        g.add((uri, fiunju.requiereCuartoAnoAprobado, Literal(True, datatype=XSD.boolean)))
    g.add((uri, fiunju.esRequisitoPara, fiunju.PPS)) # Link all to PPS for graph connectivity

# Materias Data
add_materia("IntroProg", "Introducción a la Programación", 1, "Nivel_1")
add_materia("OrgComp", "Organización de Computadoras", 1, "Nivel_1", modalidad="ExamenMultipleChoice")
add_materia("MatDisc", "Matemática Discreta", 2, "Nivel_2", ["AlgebraLineal"])
add_materia("AlgebraLineal", "Algebra Lineal", 1, "Nivel_3", modalidad="ExamenMultipleChoice")
add_materia("AnalMatemI", "Análisis Matemático I", 1, "Nivel_4")
add_materia("AnalMatemII", "Análisis Matemático II", 1, "Nivel_4", ["AnalMatemI"])
add_materia("FisicaMec", "Fisica Mecanica", 1, "Nivel_4", ["AnalMatemI", "AlgebraLineal"])
add_materia("EstDatos", "Estructura de Datos", 1, "Nivel_1", ["IntroProg"])
add_materia("MetProg", "Metodología de la Programación", 1, "Nivel_1", ["IntroProg"])

add_materia("BaseDatos", "Bases de Datos", 2, "Nivel_2", ["MetProg", "EstDatos"])
add_materia("ProgCon", "Programación Concurrente", 2, "Nivel_4", ["MetProg", "EstDatos"])
add_materia("DesSistProg", "Desarrollo Sistemático de Programas", 2, "Nivel_1", ["MetProg", "EstDatos"])
add_materia("ElecMag", "Electricidad y Magnetismo", 2, "Nivel_3", ["FisicaMec"])
add_materia("CalcNum", "Cálculo Numérico", 2, "Nivel_2", ["AnalMatemII"])
add_materia("ProbEstad", "Probabilidad y Estadística", 2, "Nivel_2", ["AlgebraLineal", "AnalMatemII"])
add_materia("TIC", "Teoría de la Información y la Comunicación", 2, "Nivel_1", ["OrgComp"])

add_materia("SistOpI", "Sistemas Operativos I", 3, "Nivel_4", ["OrgComp", "MetProg", "EstDatos"])
add_materia("LogComp", "Lógica Computacional", 3, "Nivel_1", ["AlgebraLineal"])
add_materia("ModOrientObjetos", "Modelado Orientado a Objetos", 3, "Nivel_3", ["MetProg", "EstDatos"])
add_materia("TeoAutoLengComp", "Teoria de Automatas, lenguajes y Computación", 3, "Nivel_1", ["LogComp", "EstDatos"])
add_materia("OEMN", "Organización Empresarial y Modelos de Negocios", 3, "Nivel_2", ["MetProg", "EstDatos"])
add_materia("SistOpII", "Sistemas Operativos II", 3, "Nivel_1", ["SistOpI"])
add_materia("MetSim", "Metodos de Simulacion", 3, "Nivel_1", ["ProbEstad", "CalcNum"])

add_materia("ArqParalelas", "Arquitectura de Computadoras Paralelas", 4, "Nivel_3", ["SistOpII", "ArqRedes", "NivSufIng"])
# Note: In previous file, ArqParalelas required 90 credits.
g.add((fiunju.ArqParalelas, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))

add_materia("ArqRedes", "Arquitectura de Redes", 4, "Nivel_3", ["SistOpI"])
add_materia("CalSoftTest", "Calidad de Software y Testing", 4, "Nivel_1", ["ModOrientObjetos"])
add_materia("IngCon", "Ingeniería del Conocimiento", 4, "Nivel_1", ["LogComp", "NivSufIng", "ModOrientObjetos"])
g.add((fiunju.IngCon, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))

add_materia("FEPIED", "Formulacion, Evaluacion de Proyectos Informáticos y Emprendedorismo Digital", 4, "Nivel_2", ["MetProg", "EstDatos"])
add_materia("SegAudInf", "Seguridad y Auditoria informatica", 4, "Nivel_1", ["SistOpII", "NivSufIng"])
g.add((fiunju.SegAudInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))

add_materia("SistInf", "Sistemas de información", 4, "Nivel_4", ["ModOrientObjetos", "NivSufIng"])
g.add((fiunju.SistInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))

add_materia("IngSoftI", "Ingeniería de Software I", 5, "Nivel_4", ["SistInf", "NivAptIng"])
g.add((fiunju.IngSoftI, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))

add_materia("SistInt", "Sistemas Inteligentes", 5, "Nivel_4", ["MatDisc", "CalcNum", "ProbEstad", "NivAptIng"])
g.add((fiunju.SistInt, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))

add_materia("IngSoftII", "Ingeniería de Software II", 5, "Nivel_4", ["IngSoftI"])
add_materia("PPS", "Practica Profesional Supervisada", 5, None, cuarto_aprobado=True)
g.add((fiunju.PPS, fiunju.requiereCreditos, Literal(270, datatype=XSD.integer)))

add_materia("LegEticaProf", "Legislación, Etica y Ejercicio Profesional", 5, "Nivel_4", ["NivAptIng"])
g.add((fiunju.LegEticaProf, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))

add_materia("NivSufIng", "Nivel de Suficiencia de Ingles", 0, None) # Year 0/Null
add_materia("NivAptIng", "Nivel de Aptitud de Ingles", 0, None, ["NivSufIng"])


# Optativas (simplified add)
def add_optativa(id, label, reqs, dif, creds):
    uri = fiunju[id]
    g.add((uri, RDF.type, fiunju.Optativa))
    g.add((uri, RDFS.label, Literal(label, lang="es")))
    for r in reqs:
        g.add((uri, fiunju.tieneRequisito, fiunju[r]))
    g.add((uri, fiunju.tieneDificultadCursada, fiunju[dif]))
    g.add((uri, fiunju.otorgaCreditos, Literal(creds, datatype=XSD.integer)))

add_optativa("Compiladores", "Compiladores", ["ProgCon"], "Nivel_1", 90)
add_optativa("ABDI", "Aplicaciones de Base de Datos I", ["BaseDatos"], "Nivel_1", 90)
add_optativa("ABDII", "Aplicaciones de Base de Datos II", ["BaseDatos"], "Nivel_1", 90)
add_optativa("IPDI", "Introducción al Procesamiento Digital de Imágenes", ["ProgCon"], "Nivel_2", 90)
add_optativa("IntArt", "Inteligencia Artificial", ["TeoAutoLengComp"], "Nivel_1", 90)
add_optativa("RaIn", "Recuperación Avanzada de la Información", ["ModOrientObjetos"], "Nivel_1", 90)
add_optativa("DesArqAvanSoft", "Desarrollo y Arquitecturas Avanzadas de Software", ["ModOrientObjetos"], "Nivel_2", 90)
add_optativa("TallerFormProf", "Taller de Formación Profesional", ["ProbEstad"], "Nivel_1", 60)
add_optativa("TallerMetInvCient", "Taller de Metodología de la Investigación Científica", ["ProbEstad"], "Nivel_1", 60)
add_optativa("GestAmbiental", "Gestión Ambiental", ["ProbEstad"], "Nivel_1", 60)
add_optativa("ModProNeg", "Modelado y Proceso de Negocios", ["OEMN"], "Nivel_1", 90)


print("PASO 4: Ejecutando el razonador OWL (owlrl)...")
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
print(f"Grafo DESPUÉS del razonador tiene {len(g)} tripletas.")

print("PASO 5: Serializando el grafo...")
output_dir = Path("ontologies")
output_file = output_dir / "fiunju_ontologia_GENERADA.ttl"
output_dir.mkdir(parents=True, exist_ok=True)
g.serialize(destination=str(output_file), format="turtle")
print(f"¡ÉXITO! Ontología generada y guardada en: {output_file.resolve()}")

