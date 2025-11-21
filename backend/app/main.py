from fastapi import FastAPI, Depends, HTTPException
from rdflib import Graph
from sqlalchemy.orm import Session
from enum import Enum

# Importaciones del Backend
from app.core.knowledge_base import load_knowledge_base
from app.core.database import get_db
from app.schemas.user import UserCreate, UserOut, Token, UserPerfilUpdate
from app.schemas.ontologia import MateriaOntology, TopicoOntology
from app.schemas.consejo import ConsejoRequest
from app.services import user_service, perfil_service, evaluacion_service
from app.models.user import User
from app.core.security import create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from app.schemas.perfil import UserMateriaCreate, UserMateriaOut
from app.schemas import recomendacion as recomendacion_schemas
from app.services import recomendacion_service
from app.schemas import alertas as alertas_schemas
from app.services import alertas_service
from app.models.enums import CondicionLaboral


app = FastAPI(
    title="SBC FIUNJU API",
    description="API para el Sistema Basado en Conocimiento de la FI-UNJU"
)

# --- Middleware de CORS ---
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.knowledge_graph = Graph() 

@app.on_event("startup")
def on_startup():
    print("Iniciando API... Cargando Base de Conocimiento...")
    app.state.knowledge_graph = load_knowledge_base()
    print(f"Base de Conocimiento lista. Total de tripletas: {len(app.state.knowledge_graph)}")

@app.get("/")
def read_root():
    return {"message": "¡Hola Mundo! El servidor backend SÍ funciona."}

# --- Endpoints de Ontología ---

@app.get("/ontologia/materias", response_model=list[MateriaOntology])
def get_all_materias_from_ontology(current_user: User = Depends(get_current_user)):
    kg = app.state.knowledge_graph
    
    # --- QUERY ACTUALIZADA: Ahora trae ?creditos y ?requisito ---
    query_str = """
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        
        SELECT ?materia ?label ?año ?creditos ?requisito
            WHERE { 
                ?materia a fiunju:Materia ; rdfs:label ?label . 
                OPTIONAL { ?materia fiunju:perteneceAlAño ?año . }
                OPTIONAL { ?materia fiunju:otorgaCreditos ?creditos . }
                OPTIONAL { ?materia fiunju:tieneRequisito ?requisito . }
            }
            ORDER BY ?año ?label"""
    
    results = kg.query(query_str)
    
    materias_dict = {}

    for row in results:
        uri = str(row.materia)
        if uri not in materias_dict:
            anio_val = int(row.año) if row.año else None
            creditos_val = int(row.creditos) if row.creditos else 0

            materias_dict[uri] = MateriaOntology(
                uri=uri,
                label=str(row.label),
                año=anio_val,
                creditos=creditos_val,
                requisitos=[]
            )
        
        if row.requisito:
            materias_dict[uri].requisitos.append(str(row.requisito))

    return list(materias_dict.values())

class TipoConsejo(str, Enum):
    CURSADA = "cursada"
    EXAMEN = "examen"

@app.get("/ontologia/materias/topicos", response_model=list[TopicoOntology])
def get_topicos_for_materia(
    materia_uri: str, 
    tipo: TipoConsejo, 
    current_user: User = Depends(get_current_user)
):
    kg = app.state.knowledge_graph
    print(f"Buscando tópicos para {materia_uri} (Tipo: {tipo})")
    
    filtro_sparql = ""
    # Queries en una sola línea para evitar errores de indentación
    if tipo == TipoConsejo.EXAMEN:
        filtro_sparql = """FILTER(REGEX(STR(?topico), "ExamenOral$") || REGEX(STR(?topico), "ExamenEscrito$") || REGEX(STR(?topico), "ExamenMultipleChoice$"))"""
    else: # 'cursada'
        filtro_sparql = """FILTER(!REGEX(STR(?topico), "ExamenOral$") && !REGEX(STR(?topico), "ExamenEscrito$") && !REGEX(STR(?topico), "ExamenMultipleChoice$"))"""

    query_str = f"""
        PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?topico ?label
            WHERE {{
                BIND(<{materia_uri}> AS ?materia) .
                ?materia fiunju:tieneTopicoRelevante ?topico .
                ?topico rdfs:label ?label .
                {filtro_sparql} 
            }}
            ORDER BY ?label"""

    results = kg.query(query_str)
    return [TopicoOntology(uri=str(row.topico), label=str(row.label)) for row in results]

# --- Endpoints de Perfil y Usuarios ---

@app.post("/users/register", response_model=UserOut, status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return user_service.create_user(db=db, user=user)

@app.post("/users/login", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/me/perfil", response_model=UserOut)
def update_user_personal_perfil(
    perfil_data: UserPerfilUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return user_service.update_user_perfil(db, user=current_user, perfil_data=perfil_data)

@app.get("/users/me/materias", response_model=list[UserMateriaOut])
def get_user_materias(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return perfil_service.get_materias_for_user(db, user_id=current_user.id)

@app.post("/users/me/materias", response_model=UserMateriaOut, status_code=201)
def add_user_materia(
    materia: UserMateriaCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return perfil_service.add_materia_to_user(db, user_id=current_user.id, materia=materia)

@app.delete("/users/me/materias/{user_materia_id}", status_code=204)
def remove_user_materia(
    user_materia_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success = perfil_service.delete_materia_from_user(db, user_id=current_user.id, user_materia_id=user_materia_id)
    if not success:
        raise HTTPException(status_code=404, detail="Materia no encontrada en el perfil")
    return

# --- Endpoints de Consejos ---

@app.get("/consejos/cursada/general") 
def get_general_cursada_advice(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    print(f"Generando consejo GENERAL de CURSADA para {current_user.email}...")
    kg = app.state.knowledge_graph
    consejos = evaluacion_service.evaluar_plan_cursada_actual(current_user, kg)
    return {"consejos": consejos}

@app.get("/consejos/examen/general")
def get_general_examen_advice(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    print(f"Generando consejo GENERAL de EXAMEN para {current_user.email}...")
    kg = app.state.knowledge_graph
    consejos = evaluacion_service.evaluar_plan_examen_actual(current_user, kg)
    return {"consejos": consejos}

@app.get("/recomendacion/plan-cursada-optimo", response_model=recomendacion_schemas.PlanCursadaRecomendado)
def get_plan_cursada_optimo(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    print(f"Generando plan de cursada ÓPTIMO para {current_user.email}...")
    kg = app.state.knowledge_graph
    plan = recomendacion_service.generar_plan_cursada_optimo(current_user, kg)
    return plan

@app.get("/recomendacion/finales-prioritarios", response_model=recomendacion_schemas.PlanExamenRecomendado)
def get_finales_prioritarios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Generando estrategia de EXÁMENES para {current_user.email}...")
    kg = app.state.knowledge_graph
    plan_examenes = recomendacion_service.generar_estrategia_examenes(current_user, kg)
    return plan_examenes

@app.get("/recomendacion/alerta-riesgos", response_model=list[alertas_schemas.Alerta])
def get_alertas_de_riesgo(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Generando ALERTAS proactivas para {current_user.email}...")
    kg = app.state.knowledge_graph
    alertas = alertas_service.generar_alertas_proactivas(current_user, kg)
    return alertas

@app.post("/recomendacion/simular-cursada", response_model=recomendacion_schemas.PlanCursadaRecomendado)
def post_simular_cursada(
    simulacion_data: recomendacion_schemas.PlanCursadaSimuladoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"Recibida solicitud de SIMULACIÓN para {current_user.email}...")
    kg = app.state.knowledge_graph
    plan_simulado = recomendacion_service.generar_plan_cursada_simulado(current_user, simulacion_data, kg)
    return plan_simulado

@app.post("/consejos/cursada/especifico")
def get_specific_cursada_advice(
    body: ConsejoRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    materia_uri = body.materia_uris_request[0]
    topico_uri = body.topico_uri
    
    kg = app.state.knowledge_graph
    consejos = []
    
    # CORRECCIÓN: Query sin indentación
    query_dificultad_str = f"""PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?labelMateria ?valorDificultad
WHERE {{
    BIND(<{materia_uri}> AS ?materia) . 
    ?materia rdfs:label ?labelMateria .
    ?materia fiunju:tieneDificultadCursada ?nivel .
    ?nivel fiunju:tieneValor ?valorDificultad .
}}"""
    results = kg.query(query_dificultad_str)
    
    materia_label = ""
    dificultad_valor = 0
    try:
        row = next(iter(results))
        materia_label = str(row.labelMateria)
        dificultad_valor = int(row.valorDificultad)
    except StopIteration:
        return {"consejos": ["Error: No se encontraron datos de dificultad."]}

    condicion_laboral = current_user.condicion_laboral
    
    if topico_uri == "http://fi.unju.edu.ar/ontologia/informatica#TopicoGestionTiempo":
        consejo = f"Consejo de 'Gestión del Tiempo' para '{materia_label}': "
        if dificultad_valor >= 3: 
            if condicion_laboral == "tiempo_completo":
                consejo += "¡Atención! Esta es una materia difícil y trabajas a tiempo completo..."
            else:
                consejo += "Esta materia es difícil. Aunque tengas tiempo, no te confíes..."
        else:
            consejo += "Esta materia tiene una dificultad moderada..."
        consejos.append(consejo)
            
    elif topico_uri == "http://fi.unju.edu.ar/ontologia/informatica#TopicoAprobacionTP":
        consejo = f"Consejo de 'Aprobación de TPs' para '{materia_label}': "
        consejos.append(consejo)
    else:
        consejos.append(f"No se encontró un consejo específico para '{topico_uri.split('#')[-1]}'.")

    return {"consejos": consejos}


@app.post("/consejos/examen/especifico")
def get_specific_examen_advice(
    body: ConsejoRequest, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    materia_uri = body.materia_uris_request[0]
    topico_uri = body.topico_uri
    kg = app.state.knowledge_graph
    consejos = []
    
    # CORRECCIÓN: Query sin indentación
    query_str = f"""PREFIX fiunju: <http://fi.unju.edu.ar/ontologia/informatica#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?labelMateria ?labelModalidad ?labelDificultad ?valorNumerico
WHERE {{
    BIND(<{materia_uri}> AS ?materia) .
    ?materia rdfs:label ?labelMateria .
    ?materia fiunju:tieneModalidadExamen ?modalidad .
    ?modalidad rdfs:label ?labelModalidad .
    
    ?modalidad fiunju:tieneDificultadExamen ?dificultadObj .
    ?dificultadObj fiunju:tieneValor ?valorNumerico .
    ?dificultadObj rdfs:label ?labelDificultad .
}} GROUP BY ?labelMateria ?labelModalidad ?labelDificultad ?valorNumerico"""
    
    results = kg.query(query_str)
    
    condicion_laboral = current_user.condicion_laboral
    
    for row in results:
        materia_label = str(row.labelMateria)
        modalidad_label = str(row.labelModalidad)
        
        dificultad_label = str(row.labelDificultad)
        dificultad_num = int(row.valorNumerico)

        if topico_uri == "http://fi.unju.edu.ar/ontologia/informatica#TopicoExamenOral" and "Oral" in modalidad_label:
            consejo = f"Consejo de 'Examen Oral' para '{materia_label}' (Dificultad: {dificultad_label}): "
            if dificultad_num == 4: # Muy Difícil
                consejo += "Este es un final oral de dificultad MÁXIMA..."
                if condicion_laboral == CondicionLaboral.TIEMPO_COMPLETO:
                    consejo += " Dado que trabajas a tiempo completo, es vital que practiques y organices bien tus tiempos..."
                else:
                    consejo += " Aunque tengas tiempo, ¡úsalas bien!"
            else:
                consejo += "En este final oral se evalúa la claridad conceptual..."
            consejos.append(consejo)
        
    if not consejos:
        consejos.append(f"No se encontró un consejo de examen específico para ese tópico.")

    return {"consejos": consejos}
