import sys
with open("debug_ontology.log", "w") as f:
    f.write("DEBUG: Script started\n")
    f.write("DEBUG: Script started\n")
from rdflib import Graph, Literal, RDF, RDFS, OWL, Namespace
from rdflib.namespace import XSD
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
g.add((fiunju.Materia, RDF.type, RDFS.Class))
g.add((fiunju.ModalidadExamenFinal, RDF.type, RDFS.Class))
g.add((fiunju.NivelDificultadCursada, RDF.type, RDFS.Class))
g.add((fiunju.NivelDificultadExamen, RDF.type, RDFS.Class))
g.add((fiunju.TopicoDeConsejo, RDF.type, RDFS.Class))

g.add((fiunju.FactorPersonal, RDF.type, RDFS.Class))
g.add((fiunju.FactorAcademico, RDF.type, RDFS.Class))
g.add((fiunju.FactorPlanificacion, RDF.type, RDFS.Class))
g.add((fiunju.FactorMentalidad, RDF.type, RDFS.Class))

# --- NUEVA CLASE: Arquetipo de Estudiante ---
g.add((fiunju.ArquetipoEstudiante, RDF.type, RDFS.Class))

# --- 2.2. Jerarquías de Clases (Subclases) ---
g.add((fiunju.Optativa, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.Obligatoria, RDFS.subClassOf, fiunju.Materia))
g.add((fiunju.MateriaDeAltoEsfuerzo, RDFS.subClassOf, fiunju.Materia))

# --- 2.3. Definición de Categorías de Consejos (JERARQUÍA ESTRUCTURADA) ---

# 1. Definimos las Clases "Padres" Intermedias
g.add((fiunju.TopicoDeCursada, RDF.type, RDFS.Class))
g.add((fiunju.TopicoDeCursada, RDFS.subClassOf, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoDeCursada, RDFS.label, Literal("Tópicos de Cursada", lang="es")))

g.add((fiunju.TopicoDeFinal, RDF.type, RDFS.Class))
g.add((fiunju.TopicoDeFinal, RDFS.subClassOf, fiunju.TopicoDeConsejo))
g.add((fiunju.TopicoDeFinal, RDFS.label, Literal("Tópicos de Examen Final", lang="es")))

# 2. Lista de Tópicos que pertenecen a la CURSADA
topicos_cursada = [
    (fiunju.TopicoGestionTiempo, "Gestión del Tiempo"),
    (fiunju.TopicoAprobacionTI, "Trabajo Integrador"),
    (fiunju.TopicoDinamicaSocial, "Dinámica de Grupo"),
    (fiunju.TopicoRequisitoHardware, "Requisito de Hardware"),
    (fiunju.TopicoMochilaTecnica, "Conocimiento Previo"),
    (fiunju.TopicoFuentesInfo, "Bibliografía vs Apuntes"),
    (fiunju.TopicoErroresComunes, "Errores Clásicos"),
    (fiunju.TopicoAplicacionProf, "Aplicación Profesional"),
    (fiunju.TopicoFrustracion, "Resistencia y Mentalidad"),
    (fiunju.TopicoValorClase, "Valor de la Clase")
]

# 3. Lista de Tópicos que pertenecen al FINAL
topicos_final = [
    (fiunju.TopicoExamenOral, "Examen Oral"),
    (fiunju.TopicoExamenEscrito, "Examen Escrito"),
    (fiunju.TopicoMultipleChoice, "Multiple Choice"),
    (fiunju.TopicoEstrategiaFinal, "Estrategia de Final"), # El nuevo que creamos
    (fiunju.TopicoCriterioCorreccion, "Criterio de Corrección"),
    (fiunju.TopicoImpactoEstrategico, "Impacto Estratégico")
]

# 4. Bucle para crear las clases de CURSADA (Hijos de TopicoDeCursada)
for uri, label in topicos_cursada:
    g.add((uri, RDF.type, RDFS.Class))
    g.add((uri, RDFS.subClassOf, fiunju.TopicoDeCursada)) # <--- HERENCIA CLAVE
    g.add((uri, RDFS.label, Literal(label, lang="es")))

# 5. Bucle para crear las clases de FINAL (Hijos de TopicoDeFinal)
for uri, label in topicos_final:
    g.add((uri, RDF.type, RDFS.Class))
    g.add((uri, RDFS.subClassOf, fiunju.TopicoDeFinal))   # <--- HERENCIA CLAVE
    g.add((uri, RDFS.label, Literal(label, lang="es")))

# --- 2.3. Propiedades de Objeto (ObjectProperty) ---
g.add((fiunju.esRequisitoPara, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneRequisito, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneModalidadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadCursada, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneDificultadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.esMasDificilQue, RDF.type, OWL.ObjectProperty))

# Relación Materia -> Instancia de Consejo (que a su vez tiene un tipo Tópico)
g.add((fiunju.tieneTopicoRelevante, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneTopicoRelevante, RDFS.domain, fiunju.Materia))
g.add((fiunju.tieneTopicoRelevante, RDFS.range, fiunju.TopicoDeConsejo))

# --- 2.4. Propiedades de Dato (DatatypeProperty) ---
g.add((fiunju.perteneceAlAño, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.comentarioExperto, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneValor, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tienePrioridad, RDF.type, OWL.DatatypeProperty))

# --- NUEVA PROPIEDAD: DESCRIPCIÓN DEL CONSEJO ---
g.add((fiunju.descripcion, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.descripcion, RDFS.range, XSD.string))

# --- NUEVAS PROPIEDADES DE ARQUETIPO ---
g.add((fiunju.tieneNombreArquetipo, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneNombreArquetipo, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneNombreArquetipo, RDFS.range, XSD.string))

g.add((fiunju.tieneColorIdentificativo, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneColorIdentificativo, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneColorIdentificativo, RDFS.range, XSD.string))

g.add((fiunju.tieneConsejoBase, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.tieneConsejoBase, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneConsejoBase, RDFS.range, XSD.string))

g.add((fiunju.tieneConsejoClave, RDF.type, OWL.DatatypeProperty))     # Corrección nombre vs script original
g.add((fiunju.tieneTarjetaDiagnostico, RDF.type, OWL.DatatypeProperty)) # Corrección nombre vs script original



# --- NUEVA CLASE: Estrategia de Recomendación ---
g.add((fiunju.EstrategiaRecomendacion, RDF.type, RDFS.Class))

# Propiedades de Estrategia
g.add((fiunju.ordenPrioridad, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.ordenPrioridad, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.ordenPrioridad, RDFS.range, XSD.integer))

g.add((fiunju.descripcionPlan, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.descripcionPlan, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.descripcionPlan, RDFS.range, XSD.string))

g.add((fiunju.cantidadMaterias, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.cantidadMaterias, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.cantidadMaterias, RDFS.range, XSD.integer))

g.add((fiunju.cantidadMinimaRequerida, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.cantidadMinimaRequerida, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.cantidadMinimaRequerida, RDFS.range, XSD.integer))

g.add((fiunju.requiereDisponibilidadDe, RDF.type, OWL.ObjectProperty))
g.add((fiunju.requiereDisponibilidadDe, RDFS.domain, fiunju.EstrategiaRecomendacion))
g.add((fiunju.requiereDisponibilidadDe, RDFS.range, fiunju.NivelDificultadCursada))

# Relación Arquetipo -> Estrategia
g.add((fiunju.tieneEstrategiaPosible, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneEstrategiaPosible, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneEstrategiaPosible, RDFS.range, fiunju.EstrategiaRecomendacion))

# --- NUEVA CLASE: Estrategia de Examen ---
g.add((fiunju.EstrategiaExamen, RDF.type, RDFS.Class))

# Propiedades de Estrategia Examen
g.add((fiunju.tieneEstrategiaExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.tieneEstrategiaExamen, RDFS.domain, fiunju.ArquetipoEstudiante))
g.add((fiunju.tieneEstrategiaExamen, RDFS.range, fiunju.EstrategiaExamen))

g.add((fiunju.requiereDificultadExamen, RDF.type, OWL.ObjectProperty))
g.add((fiunju.requiereDificultadExamen, RDFS.domain, fiunju.EstrategiaExamen))
g.add((fiunju.requiereDificultadExamen, RDFS.range, fiunju.NivelDificultadExamen))

# Reutilizamos propiedades: ordenPrioridad, descripcionPlan, cantidadMaterias, cantidadMinimaRequerida
# ---------------------------------------

# --- 2.5. Axiomas y Reglas Avanzadas ---
g.add((fiunju.Obligatoria, OWL.disjointWith, fiunju.Optativa))
g.add((fiunju.esRequisitoPara, RDF.type, OWL.TransitiveProperty))
g.add((fiunju.esMasDificilQue, RDF.type, OWL.TransitiveProperty))
g.add((fiunju.tieneRequisito, OWL.inverseOf, fiunju.esRequisitoPara))
g.add((fiunju.perteneceAlAño, RDF.type, OWL.FunctionalProperty))
g.add((fiunju.tieneDificultadCursada, RDF.type, OWL.FunctionalProperty))

g.add((fiunju.perteneceAlAño, RDFS.domain, fiunju.Obligatoria))
g.add((fiunju.tieneTopicoRelevante, RDFS.domain, fiunju.Materia))
g.add((fiunju.tieneTopicoRelevante, RDFS.range, fiunju.TopicoDeConsejo))

# --- PROPIEDADES PARA CRÉDITOS ---
g.add((fiunju.otorgaCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.otorgaCreditos, RDFS.domain, fiunju.Materia))
g.add((fiunju.otorgaCreditos, RDFS.range, XSD.integer))

g.add((fiunju.requiereCreditos, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCreditos, RDFS.domain, fiunju.Materia))
g.add((fiunju.requiereCreditos, RDFS.range, XSD.integer))

g.add((fiunju.requiereCuartoAnoAprobado, RDF.type, OWL.DatatypeProperty))
g.add((fiunju.requiereCuartoAnoAprobado, RDFS.domain, fiunju.Materia))
g.add((fiunju.requiereCuartoAnoAprobado, RDFS.range, XSD.boolean))

# --- 2.6. Definición de Subclases de Modalidad ---
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

all_modalities_uris = [fiunju[m] for m in modalidades_data.keys()]
for i in range(len(all_modalities_uris)):
    for j in range(i + 1, len(all_modalities_uris)):
        g.add((all_modalities_uris[i], OWL.disjointWith, all_modalities_uris[j]))

print("TBox (Esquema) definido.")

# --- 3. Población del Grafo (ABox) - Los "Hechos" ---
print("PASO 3: Poblando el grafo (ABox)...")

# --- 3.1. INSTANCIAS MAESTRAS (Consejos Generales) ---
# Generico: Aprobación TI
inst_gen_ti = fiunju.InstanciaGeneral_TI
g.add((inst_gen_ti, RDF.type, fiunju.TopicoAprobacionTI))
g.add((inst_gen_ti, RDFS.label, Literal("Estrategia para Trabajo Integrador", lang="es")))
g.add((inst_gen_ti, fiunju.descripcion, Literal("Esta materia requiere la aprobación de un Trabajo Integrador obligatorio. No dejes la codificación para el final; la defensa es individual y debes explicar la lógica de tu código.", lang="es")))

# Generico: Gestión del Tiempo
inst_gen_tiempo = fiunju.InstanciaGeneral_Tiempo
g.add((inst_gen_tiempo, RDF.type, fiunju.TopicoGestionTiempo))
g.add((inst_gen_tiempo, RDFS.label, Literal("Administración Inteligente", lang="es")))
g.add((inst_gen_tiempo, fiunju.descripcion, Literal("Asignatura de alta carga horaria. Prioriza la práctica sobre la teoría pura si estás corto de tiempo. Intenta bloques de estudio de 40min con descansos.", lang="es")))

# Generico: Examen Oral
inst_gen_oral = fiunju.InstanciaGeneral_Oral
g.add((inst_gen_oral, RDF.type, fiunju.TopicoExamenOral))
g.add((inst_gen_oral, RDFS.label, Literal("Claves para el Final Oral", lang="es")))
g.add((inst_gen_oral, fiunju.descripcion, Literal("Prepara un 'tema de capilla' sólido para iniciar con confianza. Practica oratoria frente al espejo; evalúan tanto lo técnico como tu expresión.", lang="es")))

# Generico: Examen Escrito
inst_gen_escrito = fiunju.InstanciaGeneral_Escrito
g.add((inst_gen_escrito, RDF.type, fiunju.TopicoExamenEscrito))
g.add((inst_gen_escrito, RDFS.label, Literal("Estrategia Final Escrito", lang="es")))
g.add((inst_gen_escrito, fiunju.descripcion, Literal("Dedica 5 minutos a leer todo antes de empezar. Sé prolijo y justifica siempre tus respuestas teóricas.", lang="es")))

# Generico: Multiple Choice
inst_gen_choice = fiunju.InstanciaGeneral_Choice
g.add((inst_gen_choice, RDF.type, fiunju.TopicoMultipleChoice))
g.add((inst_gen_choice, RDFS.label, Literal("Tips Multiple Choice", lang="es")))
g.add((inst_gen_choice, fiunju.descripcion, Literal("Estudia definiciones exactas, no 'guitarrees'. Ante la duda, usa la técnica de descarte para aumentar tus probabilidades.", lang="es")))

# --- 3.0. NUEVO: Definición de Arquetipos (Individuos) ---
# 1. Perfil Crítico
g.add((fiunju.ArquetipoCritico, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoCritico, fiunju.tieneNombreArquetipo, Literal("Perfil Crítico", lang="es")))
g.add((fiunju.ArquetipoCritico, fiunju.tieneColorIdentificativo, Literal("red", datatype=XSD.string)))
g.add((fiunju.ArquetipoCritico, fiunju.tieneConsejoClave, Literal("Necesitas cursar muy pocas materias y priorizar las más fáciles. La perseverancia es clave.", lang="es")))
g.add((fiunju.ArquetipoCritico, fiunju.tieneTarjetaDiagnostico, Literal("Tu perfil tiene 'muy poco tiempo para estudiar'. No se permiten errores.\n* trabajas tiempo completo\n* Vivis lejos\n* vivis solo\n* tenes hijo/s", lang="es")))

# 2. Perfil Bajo
g.add((fiunju.ArquetipoBajo, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoBajo, fiunju.tieneNombreArquetipo, Literal("Perfil Bajo", lang="es")))
g.add((fiunju.ArquetipoBajo, fiunju.tieneColorIdentificativo, Literal("orange", datatype=XSD.string)))
g.add((fiunju.ArquetipoBajo, fiunju.tieneConsejoClave, Literal("Balancea tus prioridades a las materias que querés cursar, procura que sea una materia con menor carga horaria y con parciales accesibles. Aprovecha tus tiempos libres, para estudiar en lugares tranquilos como la facultad.", lang="es")))
g.add((fiunju.ArquetipoBajo, fiunju.tieneTarjetaDiagnostico, Literal("Tiene un poco más de tiempo gracias al apoyo familiar y vivir cerca.\n* trabajas tiempo completo\n* Vivis en Capital\n* No vives solo\n* tenes hijo/s", lang="es")))

# 3. Perfil Medio-Bajo
g.add((fiunju.ArquetipoMedioBajo, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneNombreArquetipo, Literal("Perfil Medio-Bajo", lang="es")))
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneColorIdentificativo, Literal("yellow", datatype=XSD.string)))
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneConsejoClave, Literal("Prioriza las materias troncales, y organízate bien para no perder la promoción. Usá parciales de años anteriores y apuntes de compañeros.", lang="es")))
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneTarjetaDiagnostico, Literal("Tiene tiempo, pero viajar largas distancias más las tareas domésticas te quitan energía.\n* trabajas medio tiempo\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s", lang="es")))

# 4. Perfil Equilibrado
g.add((fiunju.ArquetipoEquilibrado, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneNombreArquetipo, Literal("Perfil Equilibrado", lang="es")))
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneColorIdentificativo, Literal("green", datatype=XSD.string)))
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneConsejoClave, Literal("Prioriza las materias troncales, y organízate bien para no perder la promoción. Si no entiendes un tema, asiste a consultas. Estudiar en la facultad te ayuda a concentrarte más. Resuelve parciales de años anteriores.", lang="es")))
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneTarjetaDiagnostico, Literal("Es el balance perfecto. Puede asumir carga, pero no extrema.\n* trabajas medio tiempo\n* Vivis en Capital\n* No vivis solo\n* No tenes hijo/s", lang="es")))

# 5. Perfil Medio-Alto
g.add((fiunju.ArquetipoMedioAlto, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneNombreArquetipo, Literal("Perfil Medio-Alto", lang="es")))
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneColorIdentificativo, Literal("blue", datatype=XSD.string)))
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneConsejoClave, Literal("Prioriza todas las materias, y organízate bien para no perder la promoción. No descuides tus tiempos libres, aprovéchalos para estudiar. Tenés mucho tiempo de estudio, pero vivir solo y lejos igual consume horas. Organízate, práctica parciales y usá apuntes de compañeros.", lang="es")))
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneTarjetaDiagnostico, Literal("Tiempo completo, pero vivir solo viene con tareas domésticas y viajar limita la \"energía mental\".\n* No trabajas\n* Vivis en el Interior\n* Vivis solo\n* No tenes hijo/s", lang="es")))

# 6. Perfil Super Alto
g.add((fiunju.ArquetipoSuperAlto, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneNombreArquetipo, Literal("Perfil Super Alto", lang="es")))
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneColorIdentificativo, Literal("violet", datatype=XSD.string)))
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneConsejoClave, Literal("Tenés el perfil con más disponibilidad. Prioriza todas las materias, y organízate bien para no perder la promoción. No te quedes libre. No descuides tus tiempos libres, aprovechalos para estudiar hace apuntes de cada tema, para estar al día.", lang="es")))
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneTarjetaDiagnostico, Literal("Disponibilidad total. Su única restricción es su propia capacidad de concentración.\n* No trabajas\n* Vivis en Capital\n* No vivis solo\n* No tenes hijo/s", lang="es")))

# 7. Perfil Atípico
g.add((fiunju.ArquetipoAtipico, RDF.type, fiunju.ArquetipoEstudiante))
g.add((fiunju.ArquetipoAtipico, fiunju.tieneNombreArquetipo, Literal("Perfil Atípico", lang="es")))
g.add((fiunju.ArquetipoAtipico, fiunju.tieneColorIdentificativo, Literal("brown", datatype=XSD.string)))
g.add((fiunju.ArquetipoAtipico, fiunju.tieneConsejoClave, Literal("Cuidá tus tiempos, tomá buenas notas y mantente constante para no perder promoción. Practica con materiales de otros años. Prioriza materias troncales.", lang="es")))
g.add((fiunju.ArquetipoAtipico, fiunju.tieneTarjetaDiagnostico, Literal("Tiempo libre de trabajo, pero los hijos interrumpen el \"flujo\" de estudio constante.\n* No trabajas\n* Vivis en Capital\n* No vivis solo\n* Tenes hijo/s", lang="es")))

# ---------------------------------------------------------

# --- 3.0.1. Población de Estrategias por Arquetipo ---

def crear_estrategia(id_estrategia, orden, descripcion, cant_materias, dificultad_req_uri, min_req):
    est_uri = fiunju[id_estrategia]
    g.add((est_uri, RDF.type, fiunju.EstrategiaRecomendacion))
    g.add((est_uri, fiunju.ordenPrioridad, Literal(orden, datatype=XSD.integer)))
    g.add((est_uri, fiunju.descripcionPlan, Literal(descripcion, lang="es")))
    g.add((est_uri, fiunju.cantidadMaterias, Literal(cant_materias, datatype=XSD.integer)))
    if dificultad_req_uri:
        g.add((est_uri, fiunju.requiereDisponibilidadDe, dificultad_req_uri))
    g.add((est_uri, fiunju.cantidadMinimaRequerida, Literal(min_req, datatype=XSD.integer)))
    return est_uri

# --- 1. Perfil Crítico ---
# Plan A: 2 Fáciles
e_crit_a = crear_estrategia("Estrategia_Critico_A", 1, "Plan A: 2 Fáciles. (Es el límite real de tu energía diaria; no te sobreexijas). ", 2, fiunju.Nivel_1, 2)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaPosible, e_crit_a))

# Plan B: 1 Normal
e_crit_b = crear_estrategia("Estrategia_Critico_B", 2, "Plan B: 1 Normal. (No se recomienda cursar 2 normales, el riesgo de abandono es altísimo). ", 1, fiunju.Nivel_2, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaPosible, e_crit_b))

# Plan C: 1 Difícil
e_crit_c = crear_estrategia("Estrategia_Critico_C", 3, "Plan C: 1 Difícil. (Advertencia: Solo si es la única actividad académica). ", 1, fiunju.Nivel_3, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaPosible, e_crit_c))

# Plan D: 1 Muy Difícil
e_crit_d = crear_estrategia("Estrategia_Critico_D", 4, "Plan D: 1 Muy Difícil. No cursar este cuatrimestre o cursar 1 Muy Difícil sabiendo que requerirá sacrificar fines de semana. ", 1, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaPosible, e_crit_d))


# --- 2. Perfil Bajo ---
# Plan A: 2 Fáciles
e_bajo_a = crear_estrategia("Estrategia_Bajo_A", 1, "Plan A: 2 Fáciles. (Combinación segura gracias a que tenés buen soporte en casa).", 2, fiunju.Nivel_1, 2)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaPosible, e_bajo_a))

# Plan B: 2 Normales
e_bajo_b = crear_estrategia("Estrategia_Bajo_B", 2, "Plan B: 2 Normales. (Riesgoso: Solo recomendable si las fechas de parciales no caen en la misma semana).", 2, fiunju.Nivel_2, 2)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaPosible, e_bajo_b))

# Plan C: 1 Difícil
e_bajo_c = crear_estrategia("Estrategia_Bajo_C", 3, "Plan C: 1 Difícil. (Advertencia: Estudiar en lugares tranquilos como la facultad, para evitar las distracciones del entorno).", 1, fiunju.Nivel_3, 1)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaPosible, e_bajo_c))

# Plan D: 1 Muy Difícil
e_bajo_d = crear_estrategia("Estrategia_Bajo_D", 4, "Plan D: 1 Muy Difícil. (Solo si no hay otra opción y podes concentrar toda tu atención durante toda la cursada).", 1, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaPosible, e_bajo_d))


# --- 3. Perfil Medio-Bajo ---
# Plan A: 1 Difícil + 2 Normales (Total 3) - REVISAR LOGICA ORIGINAL: "1 Dificil y 2 Normales"
# La logica original dice: if len(dificiles) >= 1 and len(normales) >= 2: ...
# Aquí modelamos el requisito PRINCIPAL. Como OWL no es un lenguaje de programación imperativo, 
# definiremos el requisito más fuerte o una combinación. 
# Para simplificar en esta iteración: Requerimos 1 Difícil. El motor luego intentará llenar con Normales.
e_mb_a = crear_estrategia("Estrategia_MedioBajo_A", 1, "Plan A: 1 Difícil + 2 Normales. (Tenés horas libres, pero el viaje largo consume mucha energía mental).", 3, fiunju.Nivel_3, 1) 
# NOTA: El motor deberá ser inteligente para completar. O podemos hacer estrategias compuestas en el futuro.
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaPosible, e_mb_a))

# Plan B: 3 Normales
e_mb_b = crear_estrategia("Estrategia_MedioBajo_B", 2, "Plan B: 3 Normales. (Debes dedicarle más tiempo al estudio sin perder el ritmo).", 3, fiunju.Nivel_2, 3)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaPosible, e_mb_b))

# Plan C: 2 Difíciles
e_mb_c = crear_estrategia("Estrategia_MedioBajo_C", 3, "Plan C: 2 Difíciles. (Riesgoso, requiere mucha disciplina y usar tus horas de viaje para leer).", 2, fiunju.Nivel_3, 2)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaPosible, e_mb_c))

# Plan D: 1 Muy Difícil + 1 Fácil
e_mb_d = crear_estrategia("Estrategia_MedioBajo_D", 4, "Plan D: 1 Muy Difícil + 1 Fácil. (Es el tope máximo de carga cognitiva para tu rutina).", 2, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaPosible, e_mb_d))


# --- 4. Perfil Equilibrado ---
# Plan A: 1 Muy Difícil + 1 Difícil + 1 Normal
e_eq_a = crear_estrategia("Estrategia_Equilibrado_A", 1, "Plan A: 1 Muy Difícil + 1 Difícil + 1 Normal. (Carga balanceada para no atrasarse y mantener buen ritmo).", 3, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaPosible, e_eq_a))

# Plan B: 1 Muy Difícil + 1 Difícil
e_eq_b = crear_estrategia("Estrategia_Equilibrado_B", 2, "Plan B: 1 Muy Difícil + 1 Difícil. (Se prioriza calidad sobre cantidad para asegurar la promoción de ambas).", 2, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaPosible, e_eq_b))

# Plan C: 3 Normales
e_eq_c = crear_estrategia("Estrategia_Equilibrado_C", 3, "Plan C: 3 Normales. (Ideal para limpiar materias pendientes, pero cuidado con subestimarlas y relajarte).", 3, fiunju.Nivel_2, 3)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaPosible, e_eq_c))

# Plan D: 2 Muy Difíciles
e_eq_d = crear_estrategia("Estrategia_Equilibrado_D", 4, "Plan D: 2 Muy Difíciles. (Advertencia: Solo si no tenés otras actividades extra curriculares previstas).", 2, fiunju.Nivel_4, 2)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaPosible, e_eq_d))


# --- 5. Perfil Medio-Alto ---
# Plan A: 2 Muy Difíciles + 2 Fáciles
e_ma_a = crear_estrategia("Estrategia_MedioAlto_A", 1, "Plan A: 2 Muy Difíciles + 2 Fáciles. (Tu prioridad absoluta es estudiar, tenes tiempo, pero también lee durante tu viajes).", 4, fiunju.Nivel_4, 2)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaPosible, e_ma_a))

# Plan B: 1 Muy Difícil + 2 Difíciles
e_ma_b = crear_estrategia("Estrategia_MedioAlto_B", 2, "Plan B: 1 Muy Difícil + 2 Difíciles. (Advertencia: Alto riesgo de saturación, aprovecha todos tus tiempos libres para estudiar).", 3, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaPosible, e_ma_b))

# Plan C: 2 Normales + 2 Fáciles
e_ma_c = crear_estrategia("Estrategia_MedioAlto_C", 3, "Plan C: 2 Normales + 2 Fáciles. (Aprovechá para adelantar, pero ojo con coordinar grupos viviendo lejos).", 4, fiunju.Nivel_2, 2)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaPosible, e_ma_c))

# Plan D: 3 Difíciles
e_ma_d = crear_estrategia("Estrategia_MedioAlto_D", 4, "Plan D: 3 Difíciles. (Límite extremo: requiere una disciplina estricta de estudio diario).", 3, fiunju.Nivel_3, 3)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaPosible, e_ma_d))


# --- 6. Perfil Super Alto ---
# Plan A: 3 Muy Difíciles + 1 Difícil
e_sa_a = crear_estrategia("Estrategia_SuperAlto_A", 1, "Plan A: 3 Muy Difíciles + 1 Difícil. (Tenés capacidad total, el único límite son los horarios de cursada).", 4, fiunju.Nivel_4, 3)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaPosible, e_sa_a))

# Plan B: 5 Variadas (Mix) - Sin requisito fuerte específico, solo cantidad
e_sa_b = crear_estrategia("Estrategia_SuperAlto_B", 2, "Plan B: 5 Variadas. (Priorizá correlativas; no curses por cursar si no te traban la carrera).", 5, None, 0)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaPosible, e_sa_b))

# Plan C: Solo Fáciles (Max permitido, ej 5)
e_sa_c = crear_estrategia("Estrategia_SuperAlto_C", 3, "Plan C: Solo Fáciles: Máximo permitido. (Usalo para subir promedio, pero no pierdas el hábito de estudio fuerte).", 5, fiunju.Nivel_1, 1)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaPosible, e_sa_c))

# Plan D: 3 Muy Difíciles
e_sa_d = crear_estrategia("Estrategia_SuperAlto_D", 4, "Plan D: 3 Muy Difíciles. (Advertencia: Si procrastinas, perdés el cuatrimestre entero; requiere constancia).", 3, fiunju.Nivel_4, 3)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaPosible, e_sa_d))


# --- 7. Perfil Atípico ---
# Plan A: 1 Muy Difícil + 1 Difícil + 1 Normal
e_at_a = crear_estrategia("Estrategia_Atipico_A", 1, "Plan A: 1 Muy Difícil + 1 Difícil + 1 Normal. (Tus tiempos libres úsalos correctamente para estudiar al 100%).", 3, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaPosible, e_at_a))

# Plan B: 1 Muy Difícil + 1 Difícil + 1 Fácil
e_at_b = crear_estrategia("Estrategia_Atipico_B", 2, "Plan B: 1 Muy Difícil + 1 Difícil + 1 Fácil. (Tus tiempos libres úsalos correctamente para estudiar al 100%).", 3, fiunju.Nivel_4, 1)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaPosible, e_at_b))

# Plan C: 2 Difíciles
e_at_c = crear_estrategia("Estrategia_Atipico_C", 3, "Plan C: 2 Difíciles. (Solo es viable si tenés soporte externo o grupo de estudio virtual para no viajar tanto).", 2, fiunju.Nivel_3, 2)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaPosible, e_at_c))

# Plan D: 2 Muy Difíciles
e_at_d = crear_estrategia("Estrategia_Atipico_D", 4, "Plan D: 2 Muy Difíciles. (Advertencia: Concentra todo el esfuerzo acá para asegurar el éxito sin riesgos).", 2, fiunju.Nivel_4, 2)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaPosible, e_at_d))

# ---------------------------------------------------------
# --- 3.0.2. Población de Estrategias de EXAMEN por Arquetipo ---

def crear_estrategia_examen(id_estrategia, orden, descripcion, cant_materias, dificultad_req_uri, min_req):
    est_uri = fiunju[id_estrategia]
    g.add((est_uri, RDF.type, fiunju.EstrategiaExamen))
    g.add((est_uri, fiunju.ordenPrioridad, Literal(orden, datatype=XSD.integer)))
    g.add((est_uri, fiunju.descripcionPlan, Literal(descripcion, lang="es")))
    g.add((est_uri, fiunju.cantidadMaterias, Literal(cant_materias, datatype=XSD.integer)))
    if dificultad_req_uri:
        g.add((est_uri, fiunju.requiereDificultadExamen, dificultad_req_uri))
    g.add((est_uri, fiunju.cantidadMinimaRequerida, Literal(min_req, datatype=XSD.integer)))
    return est_uri

# 1. Perfil Crítico
# Plan A: 1 Final Normal
ex_crit_a = crear_estrategia_examen("EstrategiaExamen_Critico_A", 1, "Plan A: 1 Final Normal. (Ideal para mantener la constancia sin saturarte).", 1, fiunju.ExamenNormal, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaExamen, ex_crit_a))

# Plan B: 1 Final Difícil
ex_crit_b = crear_estrategia_examen("EstrategiaExamen_Critico_B", 2, "Plan B: 1 Final Difícil. (Advertencia: Preparalo con tiempo, tus bloques de estudio son cortos y fragmentados).", 1, fiunju.ExamenDificil, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaExamen, ex_crit_b))

# Plan C: 1 Final Muy Difícil (No recomendado)
ex_crit_c = crear_estrategia_examen("EstrategiaExamen_Critico_C", 3, "Plan C: 1 Final Muy Difícil. No rendir finales complejos mientras se cursa. Postergar para fechas sin cursada.", 1, fiunju.ExamenMuyDificil, 1)
g.add((fiunju.ArquetipoCritico, fiunju.tieneEstrategiaExamen, ex_crit_c))


# 2. Perfil Bajo
# Plan A: 1 Normal + 1 Difícil
ex_bajo_a = crear_estrategia_examen("EstrategiaExamen_Bajo_A", 1, "Plan A: 1 Normal + 1 Difícil. (Aprovechá que una es múltiple choice y ve a consulta para ganar tiempo).", 2, fiunju.ExamenNormal, 1) # Req min 1 Normal (y el motor completará)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaExamen, ex_bajo_a))

# Plan B: 2 Difíciles
ex_bajo_b = crear_estrategia_examen("EstrategiaExamen_Bajo_B", 2, "Plan B: 2 Difíciles (Solo si los exámenes están separados por 2 semanas).", 2, fiunju.ExamenDificil, 2)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaExamen, ex_bajo_b))

# Plan C: 1 Muy Difícil
ex_bajo_c = crear_estrategia_examen("EstrategiaExamen_Bajo_C", 3, "Plan C: 1 Muy Difícil. (No se recomiendan 2 muy difíciles; el cansancio diario te va a jugar en contra).", 1, fiunju.ExamenMuyDificil, 1)
g.add((fiunju.ArquetipoBajo, fiunju.tieneEstrategiaExamen, ex_bajo_c))


# 3. Perfil Medio-Bajo
# Plan A: 1 Difícil
ex_mb_a = crear_estrategia_examen("EstrategiaExamen_MedioBajo_A", 1, "Plan A: 1 Final Difícil. (Podés apuntar a nota alta si te organizas bien en tus otras tareas y dedicas tu tiempo a estudiar).", 1, fiunju.ExamenDificil, 1)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaExamen, ex_mb_a))

# Plan B: 2 Normales
ex_mb_b = crear_estrategia_examen("EstrategiaExamen_MedioBajo_B", 2, "Plan B: 2 Finales Normales. (Averigua si las fechas de ambas están en la primera y segunda semana de la mesa de examen para tener margen de estudio).", 2, fiunju.ExamenNormal, 2)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaExamen, ex_mb_b))

# Plan C: 1 Muy Difícil
ex_mb_c = crear_estrategia_examen("EstrategiaExamen_MedioBajo_C", 3, "Plan C: 1 Muy Difícil (Debes prepararte muy bien y en lo posible con un grupo de estudio).", 1, fiunju.ExamenMuyDificil, 1)
g.add((fiunju.ArquetipoMedioBajo, fiunju.tieneEstrategiaExamen, ex_mb_c))


# 4. Perfil Equilibrado
# Plan A: 1 Normal + 1 Difícil
ex_eq_a = crear_estrategia_examen("EstrategiaExamen_Equilibrado_A", 1, "Plan A: 1 Normal + 1 Difícil. (Tenés las condiciones óptimas para concentrarte en temas complejos y aprovecha que tenes multiple choice en una).", 2, fiunju.ExamenDificil, 1)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaExamen, ex_eq_a))

# Plan B: 2 Difíciles
ex_eq_b = crear_estrategia_examen("EstrategiaExamen_Equilibrado_B", 2, "Plan B: 2 Difíciles. (Solo si hay al menos 10 días de separación entre mesas de examen).", 2, fiunju.ExamenDificil, 2)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaExamen, ex_eq_b))

# Plan C: 1 Difícil
ex_eq_c = crear_estrategia_examen("EstrategiaExamen_Equilibrado_C", 3, "Plan C: 1 Difícil. (Solo tenes esta materia para rendir, tenes tiempo para estudiar.).", 1, fiunju.ExamenDificil, 1)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaExamen, ex_eq_c))

# Plan D: 1 Muy Difícil
ex_eq_d = crear_estrategia_examen("EstrategiaExamen_Equilibrado_D", 4, "Plan D: 1 Muy Difícil. (No se recomiendan 2 muy difíciles; el cansancio diario te va a jugar en contra).", 1, fiunju.ExamenMuyDificil, 1)
g.add((fiunju.ArquetipoEquilibrado, fiunju.tieneEstrategiaExamen, ex_eq_d))


# 5. Perfil Medio-Alto
# Plan A: 2 Finales (Cualquier tipo)
ex_ma_a = crear_estrategia_examen("EstrategiaExamen_MedioAlto_A", 1, "Plan A: 2 Finales (Cualquier tipo). (Al tener disponibilidad total, podés permitirte preparar dos temas en simultáneo).", 2, None, 0)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaExamen, ex_ma_a))

# Plan B: 1 Final (Cualquier tipo)
ex_ma_b = crear_estrategia_examen("EstrategiaExamen_MedioAlto_B", 2, "Plan B: 1 Final (cualquier tipo). (Al tener disponibilidad total, podés permitirte prepararte para sacar buenas notas).", 1, None, 0)
g.add((fiunju.ArquetipoMedioAlto, fiunju.tieneEstrategiaExamen, ex_ma_b))


# 6. Perfil Super Alto
# Plan A: 2 Finales (Cualquier tipo)
ex_sa_a = crear_estrategia_examen("EstrategiaExamen_SuperAlto_A", 1, "Plan A: 2 Finales. (Tenes el tiempo y la capacidad para preparar dos finales de cualquier tipo).", 2, None, 0)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaExamen, ex_sa_a))

# Plan B: 2 Difíciles + 1 Normal
ex_sa_b = crear_estrategia_examen("EstrategiaExamen_SuperAlto_B", 2, "Plan B: 2 Difíciles + 1 Normal. (Podés prepararte para desarrollar temas extensos sin problemas de tiempo ni logística).", 3, fiunju.ExamenDificil, 2)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaExamen, ex_sa_b))

# Plan C: 3 Normales
ex_sa_c = crear_estrategia_examen("EstrategiaExamen_SuperAlto_C", 3, "Plan C: 3 materias Normales. (Busca que las fechas sean en forma escalonada para rendir una por semana y aprobarlas).", 3, fiunju.ExamenNormal, 3)
g.add((fiunju.ArquetipoSuperAlto, fiunju.tieneEstrategiaExamen, ex_sa_c))


# 7. Perfil Atípico
# Plan A: 1 Muy Difícil + 1 Normal
ex_at_a = crear_estrategia_examen("EstrategiaExamen_Atipico_A", 1, "Plan A: 1 Muy Difícil + 1 Normal. (Condición obligatoria: busca un lugar tranquilo para estudiar y dedicate a estudiar todo el tiempo que puedas).", 2, fiunju.ExamenMuyDificil, 1)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaExamen, ex_at_a))

# Plan B: 2 Difíciles
ex_at_b = crear_estrategia_examen("EstrategiaExamen_Atipico_B", 2, "Plan B: 2 Finales Difíciles. (No recomendado salvo que tengas el apoyo total por varios días en casa).", 2, fiunju.ExamenDificil, 2)
g.add((fiunju.ArquetipoAtipico, fiunju.tieneEstrategiaExamen, ex_at_b))

# --- 3.1. Individuos: Niveles de Dificultad (Examen) ---
niveles_examen_data = {
    "ExamenMuyDificil": {"label": "Muy Difícil", "valor": 4},
    "ExamenDificil": {"label": "Difícil", "valor": 3},
    "ExamenNormal": {"label": "Normal", "valor": 2}
    # "ExamenFacil": {"label": "Fácil", "valor": 1}
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
g.add((fiunju.SistOpI, fiunju.esRequisitoPara, fiunju.PPS))

# --- Estructura de Datos ---
g.add((fiunju.EstDatos, RDF.type, fiunju.Obligatoria)) 
g.add((fiunju.EstDatos, RDFS.label, Literal("Estructura de Datos", lang="es")))
g.add((fiunju.EstDatos, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.EstDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.EstDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.EstDatos, fiunju.tieneRequisito, fiunju.IntroProg))
g.add((fiunju.EstDatos, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.EstDatos, fiunju.esRequisitoPara, fiunju.PPS))

# --- Metodología de la Programación ---
g.add((fiunju.MetProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MetProg, RDFS.label, Literal("Metodología de la Programación", lang="es")))
g.add((fiunju.MetProg, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.MetProg, fiunju.tieneRequisito, fiunju.IntroProg))
g.add((fiunju.MetProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.MetProg, fiunju.tieneTopicoRelevante, fiunju.TopicoAprobacionTI))
g.add((fiunju.MetProg, fiunju.esRequisitoPara, fiunju.PPS))

# --- Introducción a la Programación ---
g.add((fiunju.IntroProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.IntroProg, RDFS.label, Literal("Introducción a la Programación", lang="es")))
g.add((fiunju.IntroProg, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.IntroProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.IntroProg, fiunju.tieneTopicoRelevante, fiunju.TopicoAprobacionTI))
g.add((fiunju.IntroProg, fiunju.esRequisitoPara, fiunju.PPS))

# --- Organización de Computadoras ---
g.add((fiunju.OrgComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.OrgComp, RDFS.label, Literal("Organización de Computadoras", lang="es")))
g.add((fiunju.OrgComp, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.OrgComp, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.OrgComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.OrgComp, fiunju.esRequisitoPara, fiunju.PPS))

# --- Bases de Datos ---
g.add((fiunju.BaseDatos, RDF.type, fiunju.Obligatoria)) 
g.add((fiunju.BaseDatos, RDFS.label, Literal("Bases de Datos", lang="es")))
g.add((fiunju.BaseDatos, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.BaseDatos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.BaseDatos, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.BaseDatos, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.BaseDatos, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, fiunju.TopicoMaterialEstudio))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, inst_gen_oral))
g.add((fiunju.BaseDatos, fiunju.esRequisitoPara, fiunju.PPS))

# --- Programación Concurrente---
g.add((fiunju.ProgCon, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ProgCon, RDFS.label, Literal("Programación Concurrente", lang="es")))
g.add((fiunju.ProgCon, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ProgCon, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ProgCon, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.ProgCon, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.ProgCon, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.ProgCon, fiunju.esRequisitoPara, fiunju.PPS))

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
g.add((fiunju.ArqParalelas, fiunju.esRequisitoPara, fiunju.PPS))

# --- Arquitectua de Redes ---
g.add((fiunju.ArqRedes, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ArqRedes, RDF.type, fiunju.MateriaDeAltoEsfuerzo))
g.add((fiunju.ArqRedes, RDFS.label, Literal("Arquitectura de Redes", lang="es")))
g.add((fiunju.ArqRedes, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.ArqRedes, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ArqRedes, fiunju.tieneRequisito, fiunju.SistOpI))
g.add((fiunju.ArqRedes, fiunju.tieneDificultadCursada, fiunju.Nivel_3))
g.add((fiunju.ArqRedes, fiunju.esRequisitoPara, fiunju.PPS))

# --- Desarrollo Sistemático de Programas ---
g.add((fiunju.DesSistProg, RDF.type, fiunju.Obligatoria))
g.add((fiunju.DesSistProg, RDFS.label, Literal("Desarrollo Sistemático de Programas", lang="es")))
g.add((fiunju.DesSistProg, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.DesSistProg, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.DesSistProg, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.DesSistProg, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.DesSistProg, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.DesSistProg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.DesSistProg, fiunju.esRequisitoPara, fiunju.PPS))

# --- Lógica Computacional ---
g.add((fiunju.LogComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.LogComp, RDFS.label, Literal("Lógica Computacional", lang="es")))
g.add((fiunju.LogComp, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.LogComp, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.LogComp, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.LogComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.LogComp, fiunju.esRequisitoPara, fiunju.PPS))

# --- Algebra Lineal ---
g.add((fiunju.AlgebraLineal, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AlgebraLineal, RDFS.label, Literal("Algebra Lineal", lang="es")))
g.add((fiunju.AlgebraLineal, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AlgebraLineal, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.AlgebraLineal, fiunju.tieneDificultadCursada, fiunju.Nivel_3))
g.add((fiunju.AlgebraLineal, fiunju.esRequisitoPara, fiunju.PPS))

# --- Calidad de Software y Testing ---
g.add((fiunju.CalSoftTest, RDF.type, fiunju.Obligatoria))
g.add((fiunju.CalSoftTest, RDFS.label, Literal("Calidad de Software y Testing", lang="es")))
g.add((fiunju.CalSoftTest, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.CalSoftTest, fiunju.tieneModalidadExamen, fiunju.ExamenMultipleChoice))
g.add((fiunju.CalSoftTest, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.CalSoftTest, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.CalSoftTest, fiunju.esRequisitoPara, fiunju.PPS))

# --- Modelado Orientado a Objetos ---
g.add((fiunju.ModOrientObjetos, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ModOrientObjetos, RDFS.label, Literal("Modelado Orientado a Objetos", lang="es")))
g.add((fiunju.ModOrientObjetos, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.ModOrientObjetos, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ModOrientObjetos, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.ModOrientObjetos, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.ModOrientObjetos, fiunju.tieneDificultadCursada, fiunju.Nivel_3))
g.add((fiunju.ModOrientObjetos, fiunju.esRequisitoPara, fiunju.PPS))

# --- Teoria de Automatas, lenguajes y Computación ---
g.add((fiunju.TeoAutoLengComp, RDF.type, fiunju.Obligatoria))
g.add((fiunju.TeoAutoLengComp, RDFS.label, Literal("Teoria de Automatas, lenguajes y Computación", lang="es")))
g.add((fiunju.TeoAutoLengComp, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneRequisito, fiunju.LogComp))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.TeoAutoLengComp, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.TeoAutoLengComp, fiunju.esRequisitoPara, fiunju.PPS))

# --- Electricidad y Magnetismo ---
g.add((fiunju.ElecMag, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ElecMag, RDFS.label, Literal("Electricidad y Magnetismo", lang="es")))
g.add((fiunju.ElecMag, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ElecMag, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ElecMag, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.ElecMag, fiunju.tieneRequisito, fiunju.FisicaMec))
g.add((fiunju.ElecMag, fiunju.tieneDificultadCursada, fiunju.Nivel_3))
g.add((fiunju.ElecMag, fiunju.esRequisitoPara, fiunju.PPS))

# --- Fisica Mecanica ---
g.add((fiunju.FisicaMec, RDF.type, fiunju.Obligatoria))
g.add((fiunju.FisicaMec, RDFS.label, Literal("Fisica Mecanica", lang="es")))
g.add((fiunju.FisicaMec, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.FisicaMec, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.FisicaMec, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.FisicaMec, fiunju.tieneRequisito, fiunju.AnalMatemI))
g.add((fiunju.FisicaMec, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.FisicaMec, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.FisicaMec, fiunju.esRequisitoPara, fiunju.PPS))

# --- Análisis Matemático I ---
g.add((fiunju.AnalMatemI, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AnalMatemI, RDFS.label, Literal("Análisis Matemático I", lang="es")))
g.add((fiunju.AnalMatemI, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AnalMatemI, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.AnalMatemI, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.AnalMatemI, fiunju.esRequisitoPara, fiunju.PPS))

# --- Análisis Matemático II ---
g.add((fiunju.AnalMatemII, RDF.type, fiunju.Obligatoria))
g.add((fiunju.AnalMatemII, RDFS.label, Literal("Análisis Matemático II", lang="es")))
g.add((fiunju.AnalMatemII, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
g.add((fiunju.AnalMatemII, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.AnalMatemII, fiunju.tieneRequisito, fiunju.AnalMatemI))
g.add((fiunju.AnalMatemII, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.AnalMatemII, fiunju.esRequisitoPara, fiunju.PPS))

# --- Matemática Discreta ---
g.add((fiunju.MatDisc, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MatDisc, RDFS.label, Literal("Matemática Discreta", lang="es")))
g.add((fiunju.MatDisc, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.MatDisc, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.MatDisc, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.MatDisc, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.MatDisc, fiunju.esRequisitoPara, fiunju.PPS))

# --- Metodos de Simulacion ---
g.add((fiunju.MetSim, RDF.type, fiunju.Obligatoria))
g.add((fiunju.MetSim, RDFS.label, Literal("Metodos de Simulacion", lang="es")))
g.add((fiunju.MetSim, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.MetSim, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoEscrito))
g.add((fiunju.MetSim, fiunju.tieneRequisito, fiunju.ProbEstad))
g.add((fiunju.MetSim, fiunju.tieneRequisito, fiunju.CalcNum))
g.add((fiunju.MetSim, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.MetSim, fiunju.esRequisitoPara, fiunju.PPS))

# --- Cálculo Numérico ---
g.add((fiunju.CalcNum, RDF.type, fiunju.Obligatoria))
g.add((fiunju.CalcNum, RDFS.label, Literal("Cálculo Numérico", lang="es")))
g.add((fiunju.CalcNum, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.CalcNum, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.CalcNum, fiunju.tieneRequisito, fiunju.AnalMatemII))
g.add((fiunju.CalcNum, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.CalcNum, fiunju.esRequisitoPara, fiunju.PPS))

# --- Probabilidad y Estadística ---
g.add((fiunju.ProbEstad, RDF.type, fiunju.Obligatoria))
g.add((fiunju.ProbEstad, RDFS.label, Literal("Probabilidad y Estadística", lang="es")))
g.add((fiunju.ProbEstad, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.ProbEstad, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.ProbEstad, fiunju.tieneRequisito, fiunju.AlgebraLineal))
g.add((fiunju.ProbEstad, fiunju.tieneRequisito, fiunju.AnalMatemII))
g.add((fiunju.ProbEstad, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.ProbEstad, fiunju.esRequisitoPara, fiunju.PPS))

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
g.add((fiunju.IngCon, fiunju.esRequisitoPara, fiunju.PPS))

# --- Formulacion, Evaluacion de Proyectos Informáticos y Emprendedorismo Digital ---
g.add((fiunju.FEPIED, RDF.type, fiunju.Obligatoria))
g.add((fiunju.FEPIED, RDFS.label, Literal("Formulacion, Evaluacion de Proyectos Informáticos y Emprendedorismo Digital", lang="es")))
g.add((fiunju.FEPIED, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.FEPIED, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.FEPIED, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.FEPIED, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.FEPIED, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.FEPIED, fiunju.esRequisitoPara, fiunju.PPS))

# --- Organización Empresarial y Modelos de Negocios ---
g.add((fiunju.OEMN, RDF.type, fiunju.Obligatoria))
g.add((fiunju.OEMN, RDFS.label, Literal("Organización Empresarial y Modelos de Negocios", lang="es")))
g.add((fiunju.OEMN, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.OEMN, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.OEMN, fiunju.tieneRequisito, fiunju.MetProg))
g.add((fiunju.OEMN, fiunju.tieneRequisito, fiunju.EstDatos))
g.add((fiunju.OEMN, fiunju.tieneDificultadCursada, fiunju.Nivel_2))
g.add((fiunju.OEMN, fiunju.esRequisitoPara, fiunju.PPS))

# --- Teoría de la Información y la Comunicación ---
g.add((fiunju.TIC, RDF.type, fiunju.Obligatoria))
g.add((fiunju.TIC, RDFS.label, Literal("Teoría de la Información y la Comunicación", lang="es")))
g.add((fiunju.TIC, fiunju.perteneceAlAño, Literal(2, datatype=XSD.integer)))
g.add((fiunju.TIC, fiunju.tieneRequisito, fiunju.OrgComp))
g.add((fiunju.TIC, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.TIC, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.TIC, fiunju.esRequisitoPara, fiunju.PPS))

# --- Seguridad y Auditoria informatica ---
g.add((fiunju.SegAudInf, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SegAudInf, RDFS.label, Literal("Seguridad y Auditoria informatica", lang="es")))
g.add((fiunju.SegAudInf, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.SegAudInf, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SegAudInf, fiunju.tieneRequisito, fiunju.SistOpII))
g.add((fiunju.SegAudInf, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.SegAudInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.SegAudInf, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.SegAudInf, fiunju.esRequisitoPara, fiunju.PPS))

# --- Sistemas Operativos II ---
g.add((fiunju.SistOpII, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SistOpII, RDFS.label, Literal("Sistemas Operativos II", lang="es")))
g.add((fiunju.SistOpII, fiunju.perteneceAlAño, Literal(3, datatype=XSD.integer)))
g.add((fiunju.SistOpII, fiunju.tieneRequisito, fiunju.SistOpI))
g.add((fiunju.SistOpII, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.SistOpII, fiunju.esRequisitoPara, fiunju.PPS))

# --- Sistemas de información ---
g.add((fiunju.SistInf, RDF.type, fiunju.Obligatoria))
g.add((fiunju.SistInf, RDFS.label, Literal("Sistemas de información", lang="es")))
g.add((fiunju.SistInf, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
g.add((fiunju.SistInf, fiunju.tieneModalidadExamen, fiunju.ExamenTeoricoOral))
g.add((fiunju.SistInf, fiunju.tieneRequisito, fiunju.ModOrientObjetos))
g.add((fiunju.SistInf, fiunju.tieneRequisito, fiunju.NivSufIng))
g.add((fiunju.SistInf, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))
g.add((fiunju.SistInf, fiunju.tieneDificultadCursada, fiunju.Nivel_4))
g.add((fiunju.SistInf, fiunju.esRequisitoPara, fiunju.PPS))

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
g.add((fiunju.ModProNeg, fiunju.tieneRequisito, fiunju.OEMN))
g.add((fiunju.ModProNeg, fiunju.tieneDificultadCursada, fiunju.Nivel_1))
g.add((fiunju.ModProNeg, fiunju.otorgaCreditos, Literal(90, datatype=XSD.integer))) # <-- Créditos

# 3.6. VINCULACIÓN DE CONSEJOS ESPECÍFICOS (NUEVO BLOQUE)
# =============================================================================
print("PASO 3.6: Vinculando consejos específicos a materias...")

# --- SISTEMAS OPERATIVOS I ---

# 1. Consejo de Cursada: Las 3 Vidas
cons_sistop_vidas = fiunju.Consejo_SistOp_Vidas
g.add((cons_sistop_vidas, RDF.type, fiunju.TopicoValorClase)) # Clase hija de Cursada
g.add((cons_sistop_vidas, RDFS.label, Literal("El Sistema de las '3 Vidas'", lang="es")))
g.add((cons_sistop_vidas, fiunju.descripcion, Literal("Toman cuestionarios con penalización al inicio de cada teórica. Si desapruebas 3, quedas LIBRE.", lang="es")))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, cons_sistop_vidas))

# 2. Consejo de Examen Final: Estrategia Oral (Capilla)
cons_sistop_capilla = fiunju.Consejo_SistOp_Capilla
g.add((cons_sistop_capilla, RDF.type, fiunju.TopicoExamenOral)) # Clase hija de Final
g.add((cons_sistop_capilla, RDFS.label, Literal("Estrategia de Unidad Específica", lang="es")))
g.add((cons_sistop_capilla, fiunju.descripcion, Literal("Si se presentan a la mesa menos de 5 alumnos, el examen es Oral. Prepara un tema 'blindado' para iniciar. Si ven solidez, 'bajan la guardia'.", lang="es")))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, cons_sistop_capilla))
# Le agregamos el genérico de Multiple Choice (ya que es su modalidad)
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, inst_gen_choice))

# 4. Consejo de Cursada: Libros
cons_sistop_libros = fiunju.Consejo_SistOp_Libros
g.add((cons_sistop_libros, RDF.type, fiunju.TopicoFuentesInfo)) # Clase hija de Cursada
g.add((cons_sistop_libros, RDFS.label, Literal("Libros Obligatorios", lang="es")))
g.add((cons_sistop_libros, fiunju.descripcion, Literal("Los apuntes no alcanzan. Apóyate en Stallings o Tanenbaum.", lang="es")))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, cons_sistop_libros))

# 5. Consejo de Cursada: Integral Salvavidas
cons_sistop_integral = fiunju.Consejo_SistOp_Integral
# Nota: Lo asignamos a 'TopicoValorClase' para forzar que aparezca en CURSADA (si usamos CriterioCorreccion saldría en Final)
g.add((cons_sistop_integral, RDF.type, fiunju.TopicoValorClase)) 
g.add((cons_sistop_integral, RDFS.label, Literal("El 'Integral' Salvavidas", lang="es")))
g.add((cons_sistop_integral, fiunju.descripcion, Literal("Existe una última instancia: un Examen Integral Teórico-Práctico al final del cuatrimestre para salvar la cursada.", lang="es")))
g.add((fiunju.SistOpI, fiunju.tieneTopicoRelevante, cons_sistop_integral))


# --- BASE DE DATOS ---
# Consejo: Error Cartesiano
cons_bd_cartesiano = fiunju.Consejo_BD_Cartesiano
g.add((cons_bd_cartesiano, RDF.type, fiunju.TopicoErroresComunes))
g.add((cons_bd_cartesiano, RDFS.label, Literal("Cuidado con el Producto Cartesiano", lang="es")))
g.add((cons_bd_cartesiano, fiunju.descripcion, Literal("Si olvidas el JOIN/WHERE, combinas todas las filas. Error grave que anula el ejercicio.", lang="es")))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, cons_bd_cartesiano))

# Consejo: Valor Profesional
cons_bd_profesional = fiunju.Consejo_BD_Profesional
g.add((cons_bd_profesional, RDF.type, fiunju.TopicoAplicacionProf))
g.add((cons_bd_profesional, RDFS.label, Literal("Valor en el Mercado", lang="es")))
g.add((cons_bd_profesional, fiunju.descripcion, Literal("Normalización y SQL Avanzado son habilidades críticas para tu primer empleo IT.", lang="es")))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, cons_bd_profesional))

# --------------------- CONSEJO ESPECIFICO PARA EXAMEN FINAL DE BD ---------
# Consejo Especifico para examen oral
cons_bd_oral = fiunju.Consejo_BD_Ruleta
g.add((cons_bd_oral, RDF.type, fiunju.TopicoExamenOral))
g.add((cons_bd_oral, fiunju.descripcion, Literal("La Ruleta de Colores", lang="es")))
g.add((cons_bd_profesional, fiunju.descripcion, Literal("El examen no es con tema a elección. Una app sortea 5 colores (unidades temáticas) al azar y debes responder preguntas puntuales sobre cada uno para sumar puntos. Debes estudiar todo el programa, no puedes 'especular' con un solo tema.", lang="es")))
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, cons_bd_oral))

# --- NUEVO: Consejo de Final para Base de Datos ---
cons_bd_final = fiunju.Consejo_BD_Final_Relacional
# Nota importante: Usamos la CLASE que creamos arriba (TopicoEstrategiaFinal)
g.add((cons_bd_final, RDF.type, fiunju.TopicoEstrategiaFinal))
g.add((cons_bd_final, RDFS.label, Literal("Defensa del Modelo en el Final", lang="es")))
g.add((cons_bd_final, fiunju.descripcion, Literal("En el final oral te pedirán justificar tu DER (Diagrama Entidad-Relación). No digas 'lo hice así porque quedaba bien'. Debes justificar usando las Formas Normales (1FN, 2FN, 3FN) y explicar cómo evitaste redundancia.", lang="es")))

# Vinculamos el consejo a la materia Base de Datos
g.add((fiunju.BaseDatos, fiunju.tieneTopicoRelevante, cons_bd_final))

# --- FISICA MECANICA ---
# Consejo: Unidades
cons_fisica_unidades = fiunju.Consejo_Fisica_Unidades
g.add((cons_fisica_unidades, RDF.type, fiunju.TopicoErroresComunes))
g.add((cons_fisica_unidades, RDFS.label, Literal("Trampa de Unidades", lang="es")))
g.add((cons_fisica_unidades, fiunju.descripcion, Literal("El error #1 es mezclar sistemas. Pasa siempre todo al Sistema Internacional.", lang="es")))
g.add((fiunju.FisicaMec, fiunju.tieneTopicoRelevante, cons_fisica_unidades))

# Consejo: Resiliencia
cons_fisica_resiliencia = fiunju.Consejo_Fisica_Resiliencia
g.add((cons_fisica_resiliencia, RDF.type, fiunju.TopicoFrustracion))
g.add((cons_fisica_resiliencia, RDFS.label, Literal("Resistencia al 1er Parcial", lang="es")))
g.add((cons_fisica_resiliencia, fiunju.descripcion, Literal("Es normal desaprobar el primero. La mayoría regulariza en recuperatorio.", lang="es")))
g.add((fiunju.FisicaMec, fiunju.tieneTopicoRelevante, cons_fisica_resiliencia))

 # --------------------- CONSEJO ESPECIFICO PARA EXAMEN FINAL DE FISICA MECANICA ---------
#Consejo para examen escrito
cons_fisica_escrito = fiunju.Consejo_Fisica_Escrito
g.add((cons_fisica_escrito, RDF.type, fiunju.TopicoExamenEscrito))
g.add((cons_fisica_escrito, RDFS.label, Literal("Estructura: 3 Puntos (Teórico-Práctico)", lang="es")))
g.add((cons_fisica_escrito, fiunju.descripcion, Literal("Es un escrito de desarrollo (Tema A o B) con 3 puntos. No es solo definir; buscan un 'mix' donde apliques la teoría exacta en demostraciones y cálculos puntuales.", lang="es")))
g.add((fiunju.FisicaMec, fiunju.tieneTopicoRelevante, cons_fisica_escrito))

# --- PROGRAMACIÓN CONCURRENTE ---
# Consejo: Impacto
cons_progcon_impacto = fiunju.Consejo_ProgCon_Impacto
g.add((cons_progcon_impacto, RDF.type, fiunju.TopicoImpactoEstrategico))
g.add((cons_progcon_impacto, RDFS.label, Literal("Prioridad Absoluta", lang="es")))
g.add((cons_progcon_impacto, fiunju.descripcion, Literal("Es el 'tapón' de la carrera. Bloquea materias de 3ro y 4to.", lang="es")))
g.add((fiunju.ProgCon, fiunju.tieneTopicoRelevante, cons_progcon_impacto))

# Consejo: Java HW
cons_progcon_hw = fiunju.Consejo_ProgCon_HW
g.add((cons_progcon_hw, RDF.type, fiunju.TopicoRequisitoHardware))
g.add((cons_progcon_hw, RDFS.label, Literal("Entorno Java", lang="es")))
g.add((cons_progcon_hw, fiunju.descripcion, Literal("Lleva notebook con Java+IDE a las prácticas para probar hilos en tiempo real.", lang="es")))
g.add((fiunju.ProgCon, fiunju.tieneTopicoRelevante, cons_progcon_hw))

# Consejo: Hilos
cons_progcon_error = fiunju.Consejo_ProgCon_Error
g.add((cons_progcon_error, RDF.type, fiunju.TopicoErroresComunes))
g.add((cons_progcon_error, RDFS.label, Literal("La Trampa de los Hilos", lang="es")))
g.add((cons_progcon_error, fiunju.descripcion, Literal("Que corra bien una vez no significa que esté bien. Prueba múltiples ejecuciones.", lang="es")))
g.add((fiunju.ProgCon, fiunju.tieneTopicoRelevante, cons_progcon_error))


# --- METODOLOGIA DE LA PROGRAMACIÓN ---
# Consejo: Grupo
cons_metprog_grupo = fiunju.Consejo_MetProg_Grupo
g.add((cons_metprog_grupo, RDF.type, fiunju.TopicoDinamicaSocial))
g.add((cons_metprog_grupo, RDFS.label, Literal("El Equipo es Todo", lang="es")))
g.add((cons_metprog_grupo, fiunju.descripcion, Literal("Busca compañeros responsables YA. Cambiar de grupo a mitad de cuatrimestre es fatal.", lang="es")))
g.add((fiunju.MetProg, fiunju.tieneTopicoRelevante, cons_metprog_grupo))

# Link al Genérico de TI
g.add((fiunju.MetProg, fiunju.tieneTopicoRelevante, inst_gen_ti))

# Consejo: Lógica
cons_metprog_logica = fiunju.Consejo_Intro_Logica
g.add((cons_metprog_logica, RDF.type, fiunju.TopicoMochilaTecnica))
g.add((cons_metprog_logica, RDFS.label, Literal("Lógica antes de Código", lang="es")))
g.add((cons_metprog_logica, fiunju.descripcion, Literal("Valoran más el pseudocódigo bien planteado que un programa que 'corre de casualidad'.", lang="es")))
g.add((fiunju.MetProg, fiunju.tieneTopicoRelevante, cons_metprog_logica))


# --- ORGANIZACIÓN DE COMPUTADORAS ---
# Link al Genérico de MC
g.add((fiunju.OrgComp, fiunju.tieneTopicoRelevante, inst_gen_choice))


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
