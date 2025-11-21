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
print("PASO 1: Grafo y namespaces inicializados.")

# --- 2. Definición del Esquema (TBox) - El "Diccionario" ---
# Aquí definimos TODAS nuestras clases, propiedades y reglas.
print("PASO 2: Definiendo el Esquema (TBox)...")

# --- 2.1. Clases Base ---
# Son los conceptos principales de nuestro dominio.
g.add((fiunju.Materia, RDF.type, RDFS.Class))
g.add((fiunju.ModalidadExamenFinal, RDF.type, RDFS.Class))
g.add((fiunju.NivelDificultadCursada, RDF.type, RDFS.Class)) # Para Cursada
g.add((fiunju.NivelDificultadExamen, RDF.type, RDFS.Class)) # Para Examen
g.add((fiunju.TopicoDeConsejo, RDF.type, RDFS.Class))

g.add((fiunju.FactorPersonal, RDF.type, RDFS.Class))
g.add((fiunju.FactorAcademico, RDF.type, RDFS.Class))
g.add((fiunju.FactorPlanificacion, RDF.type, RDFS.Class))
g.add((fiunju.FactorMentalidad, RDF.type, RDFS.Class))

# --- 2.2. Jerarquías de Clases (Subclases) ---
# Aquí organizamos las clases y especificamos tipos.
g.add((fiunju.Optativa, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.Obligatoria, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.MateriaDeAltoEsfuerzo, RDFS.subClassOf, fiunju.Materia))

# --- 2.3. Propiedades de Objeto (ObjectProperty) ---
# Reglas que conectan URI -> URI
g.add((fiunju.esRequisitoPara, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneRequisito, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneModalidadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadCursada, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.esMasDificilQue, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneTopicoRelevante, RDF.type, OWL.ObjectProperty))

# --- 2.4. Propiedades de Dato (DatatypeProperty) ---
# Reglas que conectan URI -> Literal (texto, número, etc.)
g.add((fiunju.perteneceAlAño, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.comentarioExperto, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneValor, RDF.type, OWL.DatatypeProperty)) # Usada por los niveles

# --- 2.5. Axiomas y Reglas Avanzadas ---
# Aquí le damos "inteligencia" a nuestras propiedades y clases.
g.add((fiunju.Obligatoria, OWL.disjointWith, fiunju.Optativa)) # No se puede ser ambas
g.add((fiunju.esRequisitoPara, RDF.type, OWL.TransitiveProperty)) # A->B, B->C => A->C
g.add((fiunju.esMasDificilQue, RDF.type, OWL.TransitiveProperty)) # NO ESTA AGREGADA A LAS MATERIAS
g.add((fiunju.tieneRequisito, OWL.inverseOf, fiunju.esRequisitoPara)) # A esRequisitoPara B <=> B tieneRequisito A
g.add((fiunju.perteneceAlAño, RDF.type, OWL.FunctionalProperty)) # Solo un año por materia
g.add((fiunju.tieneDificultadCursada, RDF.type, OWL.FunctionalProperty)) # Solo una dificultad por materia

# Restricciones de Dominio/Rango (Buena práctica)
g.add((fiunju.perteneceAlAño, RDFS.domain, fiunju.Obligatoria))
g.add((fiunju.tieneTopicoRelevante, RDFS.domain, fiunju.Materia))
g.add((fiunju.tieneTopicoRelevante, RDFS.range, fiunju.TopicoDeConsejo))

# --- ¡PROPIEDADES PARA CRÉDITOS! ---
# Define cuántos créditos da una materia al aprobarla (ej: 90)
g.add((fiunju.otorgaCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.otorgaCreditos, RDFS.domain, fiunju.Materia))
g.add((fiunju.otorgaCreditos, RDFS.range, XSD.integer))

# Define cuántos créditos NECESITA el alumno para cursarla (ej: 270 para PPS)
g.add((fiunju.requiereCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCreditos, RDFS.domain, fiunju.Materia))
g.add((fiunju.requiereCreditos, RDFS.range, XSD.integer))

# Define si requiere tener TODO aprobado hasta 4to año (True/False)
g.add((fiunju.requiereCuartoAnoAprobado, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCuartoAnoAprobado, RDFS.domain, fiunju.Materia))
g.add((fiunju.requiereCuartoAnoAprobado, RDFS.range, XSD.boolean))

# --- 2.6. Definición de Subclases de Modalidad (Aún TBox) ---
# Estas son CLASES (conceptos), no individuos.
modalidades_data = {
    "ExamenMultipleChoice": {"label": "Examen Multiple Choice", "dificultad": fiunju.ExamenNormal},
    "ExamenTeoricoEscrito": {"label": "Examen Teórico Escrito", "dificultad": fiunju.ExamenDificil},
    "ExamenTeoricoOral": {"label": "Examen Teórico Oral", "dificultad": fiunju.ExamenMuyDificil}
}
for uri_key, data in modalidades_data.items():
    mod_uri = fiunju[uri_key]
    g.add((mod_uri, RDF.type, RDFS.Class))
    g.add((mod_uri, RDFS.subClassOf, fiunju.ModalidadExamenFinal))
    g.add((mod_uri, RDFS.label, Literal(data["label"], lang="es")))
    if data["dificultad"] is not None:
        g.add((mod_uri, fiunju.tieneDificultadExamen, data["dificultad"]))

# Axiomas de disyunción para las modalidades (Aún TBox)
all_modalities_uris = [fiunju[m] for m in modalidades_data.keys()]
for i in range(len(all_modalities_uris)):
    for j in range(i + 1, len(all_modalities_uris)):
        g.add((all_modalities_uris[i], OWL.disjointWith, all_modalities_uris[j]))

print("TBox (Esquema) definido.")

# --- 3. Población del Grafo (ABox) - Los "Hechos" ---
# Aquí creamos los INDIVIDUOS (instancias) y los conectamos.
print("PASO 3: Poblando el grafo (ABox)...")

# --- 3.1. Individuos: Niveles de Dificultad (Examen) ---
niveles_examen_data = {
    "ExamenMuyDificil": {"label": "Muy Difícil", "valor": 4},
    "ExamenDificil": {"label": "Difícil", "valor": 3},
    "ExamenNormal": {"label": "Normal", "valor": 2},
    "ExamenFacil": {"label": "Fácil", "valor": 1}
}
for uri_key, data in niveles_examen_data.items():
    nivel_uri = fiunju[uri_key]
    g.add((nivel_uri, RDF.type, fiunju.NivelDificultadExamen))
    g.add((nivel_uri, RDFS.label, Literal(data["label"], lang="es")))
    g.add((nivel_uri, fiunju.tieneValor, Literal(data["valor"], datatype=XSD.integer)))

# --- 3.2. Individuos: Niveles de Dificultad (Cursada) ---
niveles_cursada_data = {
    "Nivel_4": {"label": "Muy difícil", "valor": 4},
    "Nivel_3": {"label": "Difícil", "valor": 3},
    "Nivel_2": {"label": "Normal", "valor": 2},
    "Nivel_1": {"label": "Fácil", "valor": 1},
}
for uri_key, data in niveles_cursada_data.items():
    nivel_uri = fiunju[uri_key]
    g.add((nivel_uri, RDF.type, fiunju.NivelDificultadCursada))
    g.add((nivel_uri, RDFS.label, Literal(data["label"], lang="es")))
    g.add((nivel_uri, fiunju.tieneValor, Literal(data["valor"], datatype=XSD.integer)))

# --- 3.3. Individuos: Tópicos de Consejo ---
g.add((fiunju.TopicoGestionTiempo, RDF.type, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoGestionTiempo, RDFS.label, Literal("Gestión del Tiempo", lang="es")))
g.add((fiunju.TopicoMaterialEstudio, RDF.type, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoMaterialEstudio, RDFS.label, Literal("Material de Estudio", lang="es")))
g.add((fiunju.TopicoAprobacionTI, RDF.type, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoAprobacionTI, RDFS.label, Literal("Aprobación de Trabajos Integrador", lang="es")))
g.add((fiunju.TopicoExamenOral, RDF.type, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoExamenOral, RDFS.label, Literal("Preparación para Examen Oral", lang="es")))
g.add((fiunju.TopicoExamenEscrito, RDF.type, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoExamenEscrito, RDFS.label, Literal("Preparación para Examen Escrito", lang="es")))

# --- 3.4. Individuos: Materias ---
print("Cargando datos de materias...")

# --- 3.x. Individuos: Factores Personales ---
g.add((fiunju.FP_Trabaja, RDF.type, fiunju.FactorPersonal))
g.add((fiunju.FP_Trabaja, RDFS.label, Literal("Trabaja", lang="es")))
g.add((fiunju.FP_Trabaja, fiunju.tienePrioridad, Literal(1))) # Prioridad 1 (la más alta)

g.add((fiunju.FP_SituacionHogar, RDF.type, fiunju.FactorPersonal))
g.add((fiunju.FP_SituacionHogar, RDFS.label, Literal("Situación de Hogar (vive solo, tiene hijos)", lang="es")))
g.add((fiunju.FP_SituacionHogar, fiunju.tienePrioridad, Literal(2)))

g.add((fiunju.FP_TipoTrabajo, RDF.type, fiunju.FactorPersonal))
g.add((fiunju.FP_TipoTrabajo, RDFS.label, Literal("El trabajo está relacionado con la informática", lang="es")))
g.add((fiunju.FP_TipoTrabajo, fiunju.tienePrioridad, Literal(3)))

g.add((fiunju.FP_LugarResidencia, RDF.type, fiunju.FactorPersonal))
g.add((fiunju.FP_LugarResidencia, RDFS.label, Literal("Lugar de Residencia (Interior vs. Capital)", lang="es")))
g.add((fiunju.FP_LugarResidencia, fiunju.tienePrioridad, Literal(4))) # El experto mencionó el tiempo de viaje como menos importante

# --- 3.x. Individuos: Factores Académicos ---
g.add((fiunju.FA_HabitoEstudio, RDF.type, fiunju.FactorAcademico))
g.add((fiunju.FA_HabitoEstudio, RDFS.label, Literal("Hábito de Estudio (constante vs. último momento)", lang="es")))
g.add((fiunju.FA_HabitoEstudio, fiunju.tienePrioridad, Literal(1))) # Prioridad 1 (la más alta)

g.add((fiunju.FA_MetodoEstudio, RDF.type, fiunju.FactorAcademico))
g.add((fiunju.FA_MetodoEstudio, RDFS.label, Literal("Método de Estudio (solo vs. grupo, leer vs. escuchar)", lang="es")))
g.add((fiunju.FA_MetodoEstudio, fiunju.tienePrioridad, Literal(2)))

g.add((fiunju.FA_ColegioSecundario, RDF.type, fiunju.FactorAcademico))
g.add((fiunju.FA_ColegioSecundario, RDFS.label, Literal("Colegio Secundario (Técnica vs. Bachiller)", lang="es")))
g.add((fiunju.FA_ColegioSecundario, fiunju.tienePrioridad, Literal(3)))

# --- Sistemas Operativos I ---
g.add((fiunju.SistOpI, RDF.type, fiunju.Obligatoria)) 
g.add((fiunju.SistOpI, RDF.type, fiunju.MateriaDeAltoEsfuerzo)) # Se pueden tener MÚLTIPLES tipos
g.add((fiunju.SistOpI, RDFS.label, Literal("Sistemas Operativos I", lang="es")))
g.add((fiunju.SistOpI, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.SistOpI, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.SistOpI, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SistOpI, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.SistOpI, fiunju.tieneRequisito, fiunju.OrgComp))
g.add((fiunju.SistOpI, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.SistOpI, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, fiunju.TopicoGestionTiempo))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, fiunju.TopicoExamenOral))

# --- Estructura de Datos ---
g.add((fiunju.EstDatos, RDF.type, fiunju.Obligatoria)) 
g.add((fiunju.EstDatos, RDFS.label, Literal("Estructura de Datos", lang="es")))
g.add((fiunju.EstDatos, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.EstDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.EstDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.EstDatos, fiunju.tieneRequisito, fiunju.IntroProg))
g.add((fiunju.EstDatos, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Metodología de la Programación ---
g.add((fiunju.MetProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MetProg, RDFS.label, Literal("Metodología de la Programación", lang="es")))
g.add((fiunju.MetProg, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.MetProg, fiunju.tieneRequisito, fiunju.IntroProg))
g.add((fiunju.MetProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.MetProg, fiunju.tieneTopicoRelevante, fiunju.TopicoAprobacionTI))

# --- Introducción a la Programación ---
g.add((fiunju.IntroProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.IntroProg, RDFS.label, Literal("Introducción a la Programación", lang="es")))
g.add((fiunju.IntroProg, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.IntroProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.IntroProg, fiunju.tieneTopicoRelevante, fiunju.TopicoAprobacionTI))

# --- Organización de Computadoras ---
g.add((fiunju.OrgComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.OrgComp, RDFS.label, Literal("Organización de Computadoras", lang="es")))
g.add((fiunju.OrgComp, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.OrgComp, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.OrgComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Bases de Datos ---
g.add((fiunju.BaseDatos, RDF.type, fiunju.Obligatoria)) 
g.add((fiunju.BaseDatos, RDFS.label, Literal("Bases de Datos", lang="es")))
g.add((fiunju.BaseDatos, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.BaseDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.BaseDatos, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.BaseDatos, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.BaseDatos, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, fiunju.TopicoMaterialEstudio))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, fiunju.TopicoExamenOral))

# --- Programación Concurrente---
g.add((fiunju.ProgCon, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ProgCon, RDFS.label, Literal("Programación Concurrente", lang="es")))
g.add((fiunju.ProgCon, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ProgCon, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ProgCon, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.ProgCon, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.ProgCon, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Arquitectura de Computadoras Paralelas ---
g.add((fiunju.ArqParalelas, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ArqParalelas, RDFS.label, Literal("Arquitectura de Computadoras Paralelas", lang="es")))
g.add((fiunju.ArqParalelas, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.ArqParalelas, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ArqParalelas, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.ArqParalelas, fiunju.tieneRequisito, fiunju.SistOpII))
g.add((fiunju.ArqParalelas, fiunju.tieneRequisito, fiunju.ArqRedes))
g.add((fiunju.ArqParalelas, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.ArqParalelas, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.ArqParalelas, fiunju.tieneDificultadCursada, fiunju.Nivel_3))

# --- Arquitectua de Redes ---
g.add((fiunju.ArqRedes, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ArqRedes, RDF.type, fiunju.MateriaDeAltoEsfuerzo))
g.add((fiunju.ArqRedes, RDFS.label, Literal("Arquitectura de Redes", lang="es")))
g.add((fiunju.ArqRedes, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.ArqRedes, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ArqRedes, fiunju.tieneRequisito, fiunju.SistOpI))
g.add((fiunju.ArqRedes, fiunju.tieneDificultadCursada, fiunju.Nivel_3))

# --- Desarrollo Sistemático de Programas ---
g.add((fiunju.DesSistProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.DesSistProg, RDFS.label, Literal("Desarrollo Sistemático de Programas", lang="es")))
g.add((fiunju.DesSistProg, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.DesSistProg, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.DesSistProg, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.DesSistProg, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.DesSistProg, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.DesSistProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Lógica Computacional ---
g.add((fiunju.LogComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.LogComp, RDFS.label, Literal("Lógica Computacional", lang="es")))
g.add((fiunju.LogComp, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.LogComp, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.LogComp, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.LogComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Algebra Lineal ---
g.add((fiunju.AlgebraLineal, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AlgebraLineal, RDFS.label, Literal("Algebra Lineal", lang="es")))
g.add((fiunju.AlgebraLineal, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AlgebraLineal, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.AlgebraLineal, fiunju.tieneDificultadCursada, fiunju.Nivel_3))

# --- Calidad de Software y Testing ---
g.add((fiunju.CalSoftTest, RDF.type, fiunju.Obligatoria))
g.add((fiunju.CalSoftTest, RDFS.label, Literal("Calidad de Software y Testing", lang="es")))
g.add((fiunju.CalSoftTest, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.CalSoftTest, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.CalSoftTest, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.CalSoftTest, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Modelado Orientado a Objetos ---
g.add((fiunju.ModOrientObjetos, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ModOrientObjetos, RDFS.label, Literal("Modelado Orientado a Objetos", lang="es")))
g.add((fiunju.ModOrientObjetos, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.ModOrientObjetos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ModOrientObjetos, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.ModOrientObjetos, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.ModOrientObjetos, fiunju.tieneDificultadCursada, fiunju.Nivel_3))

# --- Teoria de Automatas, lenguajes y Computación ---
g.add((fiunju.TeoAutoLengComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.TeoAutoLengComp, RDFS.label, Literal("Teoria de Automatas, lenguajes y Computación", lang="es")))
g.add((fiunju.TeoAutoLengComp, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneRequisito, fiunju.LogComp))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Electricidad y Magnetismo ---
g.add((fiunju.ElecMag, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ElecMag, RDFS.label, Literal("Electricidad y Magnetismo", lang="es")))
g.add((fiunju.ElecMag, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ElecMag, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ElecMag, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.ElecMag, fiunju.tieneRequisito, fiunju.FisicaMec))
g.add((fiunju.ElecMag, fiunju.tieneDificultadCursada, fiunju.Nivel_3))

# --- Fisica Mecanica ---
g.add((fiunju.FisicaMec, RDF.type, fiunju.Obligatoria))
g.add((fiunju.FisicaMec, RDFS.label, Literal("Fisica Mecanica", lang="es")))
g.add((fiunju.FisicaMec, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.FisicaMec, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.FisicaMec, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.FisicaMec, fiunju.tieneRequisito, fiunju.AnalMatemI))
g.add((fiunju.FisicaMec, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.FisicaMec, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Análisis Matemático I ---
g.add((fiunju.AnalMatemI, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AnalMatemI, RDFS.label, Literal("Análisis Matemático I", lang="es")))
g.add((fiunju.AnalMatemI, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AnalMatemI, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.AnalMatemI, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Análisis Matemático II ---
g.add((fiunju.AnalMatemII, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AnalMatemII, RDFS.label, Literal("Análisis Matemático II", lang="es")))
g.add((fiunju.AnalMatemII, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AnalMatemII, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.AnalMatemII, fiunju.tieneRequisito, fiunju.AnalMatemI))
g.add((fiunju.AnalMatemII, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Matemática Discreta ---
g.add((fiunju.MatDisc, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MatDisc, RDFS.label, Literal("Matemática Discreta", lang="es")))
g.add((fiunju.MatDisc, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.MatDisc, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.MatDisc, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.MatDisc, fiunju.tieneDificultadCursada, fiunju.Nivel_2))

# --- Metodos de Simulacion ---
g.add((fiunju.MetSim, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MetSim, RDFS.label, Literal("Metodos de Simulacion", lang="es")))
g.add((fiunju.MetSim, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.MetSim, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.MetSim, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.MetSim, fiunju.tieneRequisito, fiunju.CalcNum))
g.add((fiunju.MetSim, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Cálculo Numérico ---
g.add((fiunju.CalcNum, RDF.type, fiunju.Obligatoria))
g.add((fiunju.CalcNum, RDFS.label, Literal("Cálculo Numérico", lang="es")))
g.add((fiunju.CalcNum, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.CalcNum, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.CalcNum, fiunju.tieneRequisito, fiunju.AnalMatemII))
g.add((fiunju.CalcNum, fiunju.tieneDificultadCursada, fiunju.Nivel_2))

# --- Probabilidad y Estadística ---
g.add((fiunju.ProbEstad, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ProbEstad, RDFS.label, Literal("Probabilidad y Estadística", lang="es")))
g.add((fiunju.ProbEstad, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ProbEstad, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ProbEstad, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.ProbEstad, fiunju.tieneRequisito, fiunju.AnalMatemII))
g.add((fiunju.ProbEstad, fiunju.tieneDificultadCursada, fiunju.Nivel_2))

# --- Ingeniería del Conocimiento ---
g.add((fiunju.IngCon, RDF.type, fiunju.Obligatoria))
g.add((fiunju.IngCon, RDFS.label, Literal("Ingeniería del Conocimiento", lang="es")))
g.add((fiunju.IngCon, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.IngCon, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.IngCon, fiunju.tieneRequisito, fiunju.LogComp))
g.add((fiunju.IngCon, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.IngCon, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.IngCon, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.IngCon, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Formulacion, Evaluacion de Proyectos Informáticos y Emprendedorismo Digital ---
g.add((fiunju.FEPIED, RDF.type, fiunju.Obligatoria))
g.add((fiunju.FEPIED, RDFS.label, Literal("Formulacion, Evaluacion de Proyectos Informáticos y Emprendedorismo Digital", lang="es")))
g.add((fiunju.FEPIED, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.FEPIED, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.FEPIED, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.FEPIED, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.FEPIED, fiunju.tieneDificultadCursada, fiunju.Nivel_2))

# --- Organización Empresarial y Modelos de Negocios ---
g.add((fiunju.OEMN, RDF.type, fiunju.Obligatoria))
g.add((fiunju.OEMN, RDFS.label, Literal("Organización Empresarial y Modelos de Negocios", lang="es")))
g.add((fiunju.OEMN, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.OEMN, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.OEMN, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.OEMN, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.OEMN, fiunju.tieneDificultadCursada, fiunju.Nivel_2))

# --- Teoría de la Información y la Comunicación ---
g.add((fiunju.TIC, RDF.type, fiunju.Obligatoria))
g.add((fiunju.TIC, RDFS.label, Literal("Teoría de la Información y la Comunicación", lang="es")))
g.add((fiunju.TIC, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.TIC, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.TIC, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Seguridad y Auditoria informatica ---
g.add((fiunju.SegAudInf, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SegAudInf, RDFS.label, Literal("Seguridad y Auditoria informatica", lang="es")))
g.add((fiunju.SegAudInf, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.SegAudInf, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SegAudInf, fiunju.tieneRequisito, fiunju.SistOpII))
g.add((fiunju.SegAudInf, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.SegAudInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.SegAudInf, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Sistemas Operativos II ---
g.add((fiunju.SistOpII, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SistOpII, RDFS.label, Literal("Sistemas Operativos II", lang="es")))
g.add((fiunju.SistOpII, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.SistOpII, fiunju.tieneRequisito, fiunju.SistOpI))
g.add((fiunju.SistOpII, fiunju.tieneDificultadCursada, fiunju.Nivel_1))

# --- Sistemas de información ---
g.add((fiunju.SistInf, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SistInf, RDFS.label, Literal("Sistemas de información", lang="es")))
g.add((fiunju.SistInf, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.SistInf, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SistInf, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.SistInf, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.SistInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.SistInf, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Ingeniería de Software I ---
g.add((fiunju.IngSoftI, RDF.type, fiunju.Obligatoria))
g.add((fiunju.IngSoftI, RDFS.label, Literal("Ingeniería de Software I", lang="es")))
g.add((fiunju.IngSoftI, fiunju.perteneceAlAño, Literal(5, datatype=XSD.integer)))
g.add((fiunju.IngSoftI, fiunju.tieneRequisito, fiunju.SistInf))
g.add((fiunju.IngSoftI, fiunju.tieneRequisito, fiunju.NivAptIng))
g.add((fiunju.IngSoftI, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))
g.add((fiunju.IngSoftI, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Sistemas Inteligentes ---
g.add((fiunju.SistInt, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SistInt, RDFS.label, Literal("Sistemas Inteligentes", lang="es")))
g.add((fiunju.SistInt, fiunju.perteneceAlAño, Literal(5, datatype=XSD.integer)))
g.add((fiunju.SistInt, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SistInt, fiunju.tieneRequisito, fiunju.MatDisc))
g.add((fiunju.SistInt, fiunju.tieneRequisito, fiunju.CalcNum))
g.add((fiunju.SistInt, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.SistInt, fiunju.tieneRequisito, fiunju.NivAptIng))
g.add((fiunju.SistInt, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))
g.add((fiunju.SistInt, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Ingeniería de Software II ---
g.add((fiunju.IngSoftII, RDF.type, fiunju.Obligatoria))
g.add((fiunju.IngSoftII, RDFS.label, Literal("Ingeniería de Software II", lang="es")))
g.add((fiunju.IngSoftII, fiunju.perteneceAlAño, Literal(5, datatype=XSD.integer)))
g.add((fiunju.IngSoftII, fiunju.tieneRequisito, fiunju.IngSoftI))
g.add((fiunju.IngSoftII, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Practica Profesional Supervisada ---
g.add((fiunju.PPS, RDF.type, fiunju.Obligatoria))
g.add((fiunju.PPS, RDFS.label, Literal("Practica Profesional Supervisada", lang="es")))
g.add((fiunju.PPS, fiunju.perteneceAlAño, Literal(5, datatype=XSD.integer)))
# Requisitos de la PPS
g.add((fiunju.PPS, fiunju.requiereCreditos, Literal(270, datatype=XSD.integer)))
g.add((fiunju.PPS, fiunju.requiereCuartoAnoAprobado, Literal(True, datatype=XSD.boolean)))

# --- Legislación, Etica y Ejercicio Profesional ---
g.add((fiunju.LegEticaProf, RDF.type, fiunju.Obligatoria))
g.add((fiunju.LegEticaProf, RDFS.label, Literal("Legislación, Etica y Ejercicio Profesional", lang="es")))
g.add((fiunju.LegEticaProf, fiunju.perteneceAlAño, Literal(5, datatype=XSD.integer)))
g.add((fiunju.LegEticaProf, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.LegEticaProf, fiunju.tieneRequisito, fiunju.NivAptIng))
g.add((fiunju.LegEticaProf, fiunju.requiereCreditos, Literal(180, datatype=XSD.integer)))
g.add((fiunju.LegEticaProf, fiunju.tieneDificultadCursada, fiunju.Nivel_4))

# --- Nivel de Suficiencia de Ingles ---
g.add((fiunju.NivSufIng, RDF.type, fiunju.Obligatoria))
g.add((fiunju.NivSufIng, RDFS.label, Literal("Nivel de Suficiencia de Ingles", lang="es")))

# --- Nivel de Aptitud de Ingles ---
g.add((fiunju.NivAptIng, RDF.type, fiunju.Obligatoria))
g.add((fiunju.NivAptIng, RDFS.label, Literal("Nivel de Aptitud de Ingles", lang="es")))
g.add((fiunju.NivAptIng, fiunju.tieneRequisito, fiunju.NivSufIng))

# --- Compiladores ---
g.add((fiunju.Compiladores, RDF.type, fiunju.Optativa))
g.add((fiunju.Compiladores, RDFS.label, Literal("Compiladores", lang="es")))
g.add((fiunju.Compiladores, fiunju.tieneRequisito, fiunju.ProgCon))
g.add((fiunju.Compiladores, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.Compiladores, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Aplicaciones de Base de Datos I ---
g.add((fiunju.ABDI, RDF.type, fiunju.Optativa))
g.add((fiunju.ABDI, RDFS.label, Literal("Aplicaciones de Base de Datos I", lang="es")))
g.add((fiunju.ABDI, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ABDI, fiunju.tieneRequisito, fiunju.BaseDatos))
g.add((fiunju.ABDI, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.ABDI, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Aplicaciones de Base de Datos II ---
g.add((fiunju.ABDII, RDF.type, fiunju.Optativa))
g.add((fiunju.ABDII, RDFS.label, Literal("Aplicaciones de Base de Datos II", lang="es")))
g.add((fiunju.ABDII, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ABDII, fiunju.tieneRequisito, fiunju.BaseDatos))
g.add((fiunju.ABDII, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.ABDII, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Introducción al Procesamiento Digital de Imágenes ---
g.add((fiunju.IPDI, RDF.type, fiunju.Optativa))
g.add((fiunju.IPDI, RDFS.label, Literal("Introducción al Procesamiento Digital de Imágenes", lang="es")))
g.add((fiunju.IPDI, fiunju.tieneRequisito, fiunju.ProgCon))
g.add((fiunju.IPDI, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.IPDI, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Inteligencia Artificial ---
g.add((fiunju.IntArt, RDF.type, fiunju.Optativa))
g.add((fiunju.IntArt, RDFS.label, Literal("Inteligencia Artificial", lang="es")))
g.add((fiunju.IntArt, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.IntArt, fiunju.tieneRequisito, fiunju.TeoAutoLengComp))
g.add((fiunju.IntArt, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.IntArt, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Recuperación Avanzada de la Información ---
g.add((fiunju.RaIn, RDF.type, fiunju.Optativa))
g.add((fiunju.RaIn, RDFS.label, Literal("Recuperación Avanzada de la Información", lang="es")))
g.add((fiunju.RaIn, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.RaIn, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.RaIn, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.RaIn, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Desarrollo y Arquitecturas Avanzadas de Software ---
g.add((fiunju.DesArqAvanSoft, RDF.type, fiunju.Optativa))
g.add((fiunju.DesArqAvanSoft, RDFS.label, Literal("Desarrollo y Arquitecturas Avanzadas de Software", lang="es")))
g.add((fiunju.DesArqAvanSoft, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.DesArqAvanSoft, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.DesArqAvanSoft, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Taller de Formación Profesional ---
g.add((fiunju.TallerFormProf, RDF.type, fiunju.Optativa))
g.add((fiunju.TallerFormProf, RDFS.label, Literal("Taller de Formación Profesional", lang="es")))
g.add((fiunju.TallerFormProf, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.TallerFormProf, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.TallerFormProf, fiunju.otorgaCreditos, Literal(60, datatype=XSD.integer))) # <-- Créditos

# --- Taller de Metodología de la Investigación Científica ---
g.add((fiunju.TallerMetInvCient, RDF.type, fiunju.Optativa))
g.add((fiunju.TallerMetInvCient, RDFS.label, Literal("Taller de Metodología de la Investigación Científica", lang="es")))
g.add((fiunju.TallerMetInvCient, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.TallerMetInvCient, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.TallerMetInvCient, fiunju.otorgaCreditos, Literal(60, datatype=XSD.integer))) # <-- Créditos

# --- Gestión Ambiental ---
g.add((fiunju.GestAmbiental, RDF.type, fiunju.Optativa))
g.add((fiunju.GestAmbiental, RDFS.label, Literal("Gestión Ambiental", lang="es")))
g.add((fiunju.GestAmbiental, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.GestAmbiental, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.GestAmbiental, fiunju.otorgaCreditos, Literal(60, datatype=XSD.integer))) # <-- Créditos

# --- Modelado y Proceso de Negocios ---
g.add((fiunju.ModProNeg, RDF.type, fiunju.Optativa))
g.add((fiunju.ModProNeg, RDFS.label, Literal("Modelado y Proceso de Negocios", lang="es")))
g.add((fiunju.ModProNeg, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ModProNeg, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.ModProNeg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.ModProNeg, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# --- Introducción a la Innovación y Entrepreneurship ---
g.add((fiunju.IntInnEntrep, RDF.type, fiunju.Optativa))
g.add((fiunju.IntInnEntrep, RDFS.label, Literal("Introducción a la Innovación y Entrepreneurship", lang="es")))
g.add((fiunju.IntInnEntrep, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.IntInnEntrep, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

print("ABox (Datos) poblada.")


# --- 4. Ejecución del Razonador ---
print("PASO 4: Ejecutando el razonador OWL (owlrl)...")
owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
print("¡Razonamiento completado!")
print(f"Grafo DESPUÉS del razonador tiene {len(g)} tripletas.")

# --- 5. Serialización del Grafo Final ---
print("PASO 5: Serializando el grafo...")
# Define dónde guardar el archivo
output_dir = Path("ontologies") # Guardar en una carpeta local
output_file = output_dir / "fiunju_ontologia_GENERADA.ttl"

# Crea la carpeta 'ontologies' si no existe
output_dir.mkdir(parents=True, exist_ok=True)

# Guarda el archivo
g.serialize(destination=str(output_file), format="turtle")

print("="*40)
print(f"¡ÉXITO! Ontología generada y guardada en:")
print(f"{output_file.resolve()}")
print("="*40)