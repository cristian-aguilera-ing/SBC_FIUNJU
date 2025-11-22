import pytest
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL
import owlrl
from app.services.recomendacion_service import _get_materias_habilitadas
from app.models.user import User
from app.models.perfil import UserMateria
from app.models.enums import CondicionLaboral

# --- Fixtures ---

@pytest.fixture
def mock_kg():
    g = Graph()
    fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    g.bind("fiunju", fiunju)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)

    # Definir clases
    g.add((fiunju.Materia, RDF.type, RDFS.Class))
    g.add((fiunju.Obligatoria, RDFS.subClassOf, fiunju.Materia))

    # Materia 1: Intro (año 1, 0 creditos requeridos)
    g.add((fiunju.Intro, RDF.type, fiunju.Obligatoria))
    g.add((fiunju.Intro, RDFS.label, Literal("Intro a la Prog")))
    g.add((fiunju.Intro, fiunju.perteneceAlAño, Literal(1, datatype=XSD.integer)))
    g.add((fiunju.Intro, fiunju.otorgaCreditos, Literal(50, datatype=XSD.integer)))
    # g.add((fiunju.Intro, fiunju.requiereCreditos, Literal(0, datatype=XSD.integer)))

    # Materia 2: Avanzada (año 4, requiere 90 creditos)
    g.add((fiunju.Avanzada, RDF.type, fiunju.Obligatoria))
    g.add((fiunju.Avanzada, RDFS.label, Literal("Materia Avanzada")))
    g.add((fiunju.Avanzada, fiunju.perteneceAlAño, Literal(4, datatype=XSD.integer)))
    g.add((fiunju.Avanzada, fiunju.requiereCreditos, Literal(90, datatype=XSD.integer)))

    # Ejecutar razonador para que Intro se vea como Materia
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)

    return g

@pytest.fixture
def mock_user():
    return User(
        id=1,
        email="test@test.com",
        condicion_laboral=CondicionLaboral.NO_TRABAJA,
        materias_cursadas=[]
    )

# --- Tests ---

def test_materia_bloqueada_por_creditos(mock_kg, mock_user):
    # Caso 1: Usuario sin materias aprobadas (0 créditos)
    # Debería ver Intro, pero NO Avanzada
    habilitadas = _get_materias_habilitadas(mock_user, mock_kg)
    uris = [m["uri"] for m in habilitadas]

    assert "http://fi.unju.edu.ar/ontologia/informatica#Intro" in uris
    assert "http://fi.unju.edu.ar/ontologia/informatica#Avanzada" not in uris

def test_materia_habilitada_con_creditos_suficientes(mock_kg, mock_user):
    # Caso 2: Usuario aprobó Intro (50 créditos).
    # Aún no alcanza los 90 para Avanzada.
    m1 = UserMateria(materia_uri="http://fi.unju.edu.ar/ontologia/informatica#Intro", estado="Aprobada")
    mock_user.materias_cursadas.append(m1)

    habilitadas = _get_materias_habilitadas(mock_user, mock_kg)
    uris = [m["uri"] for m in habilitadas]

    assert "http://fi.unju.edu.ar/ontologia/informatica#Avanzada" not in uris # 50 < 90

    # Caso 3: Usuario tiene más créditos (simulamos otra materia aprobada extra)
    # Agregamos Materia Extra al Grafo y re-corremos el razonador (o la agregamos explícitamente como Materia)
    fiunju = Namespace("http://fi.unju.edu.ar/ontologia/informatica#")
    mock_kg.add((fiunju.Extra, RDF.type, fiunju.Obligatoria))
    mock_kg.add((fiunju.Extra, RDF.type, fiunju.Materia)) # Truco para evitar correr owlrl de nuevo (es lento)
    mock_kg.add((fiunju.Extra, RDFS.label, Literal("Extra")))
    mock_kg.add((fiunju.Extra, fiunju.otorgaCreditos, Literal(50, datatype=XSD.integer)))

    m2 = UserMateria(materia_uri="http://fi.unju.edu.ar/ontologia/informatica#Extra", estado="Aprobada")
    mock_user.materias_cursadas.append(m2)

    # Total créditos: 50 (Intro) + 50 (Extra) = 100. > 90.
    habilitadas_final = _get_materias_habilitadas(mock_user, mock_kg)
    uris_final = [m["uri"] for m in habilitadas_final]

    assert "http://fi.unju.edu.ar/ontologia/informatica#Avanzada" in uris_final
