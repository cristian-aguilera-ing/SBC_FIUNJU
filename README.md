# SBC_FIUNJU - Sistema de Recomendación Académica Inteligente

**SBC_FIUNJU** es un sistema de recomendación académica basado en conocimiento (Knowledge-Based System) diseñado para asistir a estudiantes de la **Facultad de Ingeniería de la Universidad Nacional de Jujuy (FIUNJU)** en la planificación de su carrera universitaria.

El sistema utiliza una **ontología OWL/RDF** que modela el plan de estudios, factores personales del estudiante (trabajo, residencia, situación familiar) y reglas de recomendación académica. A través de consultas SPARQL y razonamiento lógico, el sistema:

- 🎯 **Clasifica** a cada estudiante en uno de **7 arquetipos** según su disponibilidad y contexto personal
- 📚 **Recomienda** planes de cursada personalizados con estrategias específicas (Plan A, B, C, D, E)
- 📝 **Sugiere** estrategias de estudio para exámenes finales adaptadas a cada perfil
- ⚠️ **Detecta** factores de riesgo académico y ofrece consejos preventivos
- 💡 **Proporciona** tips específicos por materia para cursada y examen final

## Arquitectura General

El sistema está orquestado mediante **Docker Compose** y consta de tres servicios principales:

1.  **Backend (API & Lógica SBC)**
2.  **Frontend (Interfaz de Usuario)**
3.  **Base de Datos (Persistencia)**

---

## 1. Backend (`/backend`)

El backend está construido con **Python** y **FastAPI**. Su función principal es exponer una API RESTful y gestionar una **Ontología** (Grafo de Conocimiento) que modela el plan de estudios y las reglas de recomendación.

### Tecnologías Clave

*   **FastAPI** - Framework web asíncrono moderno para construir APIs de alto rendimiento
*   **RDFLib & OWLRL** - Librerías para trabajar con Web Semántica (RDF, OWL) y razonamiento lógico
*   **PostgreSQL & SQLAlchemy** - Base de datos relacional y ORM para persistencia de datos de usuarios
*   **Alembic** - Sistema de migraciones de base de datos
*   **Python-Jose** - Autenticación JWT (JSON Web Tokens)
*   **Passlib & Bcrypt** - Hashing seguro de contraseñas
*   **Pydantic** - Validación de datos y serialización

### Archivo Clave: `generar_ontologia.py`

Este script de **1270 líneas** es el "cerebro" del sistema de conocimiento. Define una ontología OWL completa que modela:

#### Conceptos Principales

*   **Materias**: Obligatorias y Optativas con créditos, años, requisitos y correlatividades
*   **Niveles de Dificultad**:
    *   **Cursada**: Fácil, Normal, Difícil, Muy Difícil (4 niveles)
    *   **Examen**: Normal, Difícil, Muy Difícil (3 niveles)
*   **Modalidades de Examen**: Multiple Choice, Oral, Escrito
*   **Arquetipos de Estudiante**: 7 perfiles basados en disponibilidad y factores personales
*   **Estrategias de Recomendación**: Planes de cursada (A, B, C, D, E) con requisitos específicos
*   **Estrategias de Examen**: Planes para rendir finales según perfil
*   **Tópicos de Consejo**: Tips específicos por materia (cursada y examen)

El script puebla el grafo con datos reales de la carrera de Licenciatura en Sistemas de Información, ejecuta el razonador OWLRL para inferir conocimiento implícito, y exporta el resultado a `fiunju_ontologia.ttl`.

## 2. Frontend (`/frontend`)

El frontend es una aplicación web moderna construida con **Next.js 16** (App Router) y **TypeScript**.

### Tecnologías Clave

*   **Next.js 16.0.1** - Framework de React con App Router, Server Components y optimizaciones automáticas
*   **React 19.2.0** - Biblioteca para construir interfaces de usuario con React Compiler habilitado
*   **TypeScript 5** - JavaScript tipado para mayor robustez y autocompletado
*   **Tailwind CSS 4** - Framework de utilidades CSS con sintaxis moderna
*   **Shadcn/ui** - Colección de componentes UI reutilizables construidos con Radix UI
*   **Radix UI** - Primitivos UI accesibles y sin estilos:
    *   `@radix-ui/react-label`
    *   `@radix-ui/react-radio-group`
    *   `@radix-ui/react-select`
    *   `@radix-ui/react-switch`
    *   `@radix-ui/react-scroll-area`
*   **Framer Motion 12.23** - Biblioteca de animaciones fluidas y gestos
*   **Lucide React** - Iconos SVG modernos y personalizables
*   **Axios 1.13** - Cliente HTTP para comunicación con el backend
*   **Next Themes** - Soporte para modo oscuro/claro
*   **Sonner** - Notificaciones toast elegantes y accesibles

## 3. Infraestructura

*   **Docker Compose:** Define y corre los contenedores para que todo el entorno de desarrollo se levante con un solo comando.
*   **Base de Datos:** Imagen oficial de `postgres:15-alpine`.

---

## 🎯 Características Principales

### 1. 👥 **Clasificación de Perfil de Estudiante**

El sistema clasifica automáticamente a cada estudiante en uno de **7 arquetipos** basándose en:
- 💼 **Situación laboral** (No trabaja / Medio tiempo / Tiempo completo)
- 🏠 **Residencia** (Capital / Interior de Jujuy)
- 👨‍👩‍👧 **Situación familiar** (Vive solo / Con familia / Tiene hijos)

### 2. 📚 **Recomendaciones de Cursada Inteligentes**

Para cada arquetipo, el sistema ofrece **múltiples planes de cursada** (Plan A, B, C, D, E) que consideran:
- Número de materias recomendadas
- Niveles de dificultad adecuados al perfil
- Distribución de carga académica balanceada
- Advertencias específicas por plan

**Ejemplo**:
- **Perfil Crítico** → Plan A: 2 Fáciles | Plan B: 1 Normal | Plan C: 1 Difícil
- **Perfil Super Alto** → Plan A: 3 Muy Difíciles + 1 Difícil | Plan B: ≤ 5 Materias

### 3. 📝 **Estrategias de Exámenes Finales**

Recomendaciones personalizadas para rendir finales según:
- Dificultad de los exámenes (Normal, Difícil, Muy Difícil)
- Cantidad óptima de finales simultáneos
- Consideraciones de tiempo de preparación

### 4. 💡 **Tips Específicos por Materia**

Consejos contextuales para cada materia clasificados en:
- **Cursada**: Gestión del tiempo, TI, dinámica social, hardware, conocimiento previo, fuentes de información, errores comunes, aplicación profesional
- **Examen**: Oral, Escrito, Multiple Choice, Estrategia de final, Criterio de corrección

### 5. ⚠️ **Alertas de Riesgo Académico**

Detección de:
- Sobrecarga de materias difíciles
- Conflictos de horarios potenciales
- Falta de correlatividades
- Riesgo de pérdida de promoción

### 6. 🔍 **Seguimiento de Progreso Académico**

El estudiante puede marcar materias como:
- ✅ **Aprobada** (aprobada con final)
- 🟡 **Regular** (cursada aprobada, falta final)
- 📝 **Preparando Final** (estudiando para rendir)

### 7. 🧮 **Simulador de Cursada**

Simula diferentes combinaciones de materias para ver:
- Qué estrategia se aplicaría
- Advertencias del sistema
- Recomendaciones específicas

### 8. 🔗 **Consultas SPARQL en Tiempo Real**

Todas las recomendaciones se generan dinámicamente consultando la ontología OWL/RDF mediante SPARQL, garantizando:
- Consistencia lógica
- Razonamiento automático
- Extensibilidad sin cambios de código

---

## 🎭 Los 7 Arquetipos de Estudiante

El sistema define **7 perfiles** que representan diferentes contextos de disponibilidad y recursos:

### 1. 🔴 **Perfil Crítico** (Riesgo Alto)
**Características**: Trabaja tiempo completo + Vive lejos + Vive solo + Tiene hijos  
**Disponibilidad**: Mínima. Muy poco tiempo para estudiar.  
**Estrategia**: Cursar **muy pocas materias** priorizando las más fáciles.  
**Plan A**: 2 Fáciles  

### 2. 🟠 **Perfil Bajo**
**Características**: Trabaja tiempo completo + Vive en Capital + No vive solo + Tiene hijos  
**Disponibilidad**: Baja, pero mejor que Crítico gracias al apoyo familiar y cercanía.  
**Estrategia**: Balancear prioridades, elegir materias con menor carga horaria.  
**Plan A**: 2 Fáciles  

### 3. 🟡 **Perfil Medio-Bajo**
**Características**: Trabaja medio tiempo + Vive en Interior + Vive solo + No tiene hijos  
**Disponibilidad**: Media-baja. Viajes largos y tareas domésticas quitan energía.  
**Estrategia**: Priorizar materias troncales, organizarse bien.  
**Plan A**: 1 Difícil + 2 Normales  

### 4. 🟢 **Perfil Equilibrado** (Balance Perfecto)
**Características**: Trabaja medio tiempo + Vive en Capital + No vive solo + No tiene hijos  
**Disponibilidad**: Buena. Balance entre trabajo y estudio.  
**Estrategia Puede asumir carga moderada-alta sin problemas.  
**Plan A**: 2 Fáciles + 1 Muy Difícil  

### 5. 🔵 **Perfil Medio-Alto**
**Características**: No trabaja + Vive en Interior + Vive solo + No tiene hijos  
**Disponibilidad**: Alta, pero tareas domésticas y viajes consumen tiempo.  
**Estrategia**: Aprovechar tiempo libre, estudiar en viajes.  
**Plan A**: 2 Muy Difíciles + 2 Fáciles  

### 6. 🟣 **Perfil Super Alto**
**Características**: No trabaja + Vive en Capital + No vive solo + No tiene hijos  
**Disponibilidad**: Máxima. Solo limitado por capacidad de concentración.  
**Estrategia**: Puede cursar hasta 5 materias sin problemas.  
**Plan A**: 3 Muy Difíciles + 1 Difícil  

### 7. 🟤 **Perfil Atípico**
**Características**: No trabaja + Vive en Capital + No vive solo + Tiene hijos  
**Disponibilidad**: Alta, pero los hijos interrumpen el flujo de estudio.  
**Estrategia**: Cuidar tiempos, mantener constancia, priorizar troncales.  
**Plan A**: 1 Muy Difícil + 1 Difícil + 1 Normal  

---

## 🛣️ API Endpoints Principales

### Autenticación
- `POST /register` - Registro de nuevo usuario
- `POST /login` - Inicio de sesión (retorna JWT)
- `GET /perfil/me` - Obtener perfil del usuario autenticado

### Gestión de Perfil
- `PUT /perfil` - Actualizar datos personales (trabajo, residencia, familia)
- `GET /materias` - Obtener materias del usuario (Aprobadas, Regulares, etc.)
- `POST /materias` - Agregar materia al historial académico
- `DELETE /materias/{id}` - Eliminar materia del historial

### Ontología y Materias
- `GET /materias_ontologia` - Obtener todas las materias desde la ontología con dificultades y requisitos
- `GET /topicos/{materia_uri}?tipo=cursada|examen` - Obtener tips específicos para una materia

### Recomendaciones
- `GET /plan_cursada` - Obtener plan de cursada recomendado según arquetipo detectado
- `GET /finales_prioritarios` - Estrategias de exámenes finales personalizadas
- `POST /simular_cursada` - Simular cómo sería cursar X materias
- `GET /alertas_riesgo` - Obtener alertas de riesgo académico

### Consejos Específicos
- `POST /consejo/cursada` - Consejos para cursar una materia específica
- `POST /consejo/examen` - Consejos para rendir el final de una materia

---

## 📁 Estructura del Proyecto

```
SBC_FIUNJU/
├── backend/
│   ├── app/
│   │   ├── core/               # Configuración de BD y knowledge base
│   │   │   ├── database.py
│   │   │   └── knowledge_base.py    # Carga de ontología
│   │   ├── models/             # Modelos SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── enums.py           # WorkStatus, ResidenceLocation, etc.
│   │   │   └── user_materia.py
│   │   ├── schemas/            # Schemas Pydantic para validación
│   │   │   ├── user_schemas.py
│   │   │   └── recomendacion_schemas.py
│   │   ├── services/           # Lógica de negocio
│   │   │   ├── auth_service.py
│   │   │   ├── ontologia_service.py    # Consultas SPARQL
│   │   │   ├── recomendacion_service.py # Motor de recomendaciones
│   │   │   └── user_service.py
│   │   └── main.py             # FastAPI app y rutas
│   ├── alembic/                # Migraciones de BD
│   ├── generar_ontologia.py    # ⭐ Script de generación de ontología (1270 líneas)
│   ├── ontologies/             # Almacén de archivos .ttl
│   │   └── fiunju_ontologia.ttl
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── (auth)/          # Rutas de autenticación
│       │   │   ├── login/page.tsx
│       │   │   └── register/page.tsx
│       │   ├── dashboard/       # Dashboard principal
│       │   │   └── page.tsx
│       │   ├── perfil/          # Página de perfil y materias
│       │   │   └── page.tsx
│       │   ├── layout.tsx       # Layout principal con ThemeProvider
│       │   └── page.tsx         # Landing page
│       ├── components/          # Componentes React reutilizables
│       │   ├── PlanResults.tsx        # Resultados de recomendación
│       │   ├── ExamenStrategy.tsx     # Estrategias de examen
│       │   ├── ui/                    # Componentes Shadcn/ui
│       │   └── ...
│       └── types/               # Tipos TypeScript
├── .devcontainer/           # Configuración de DevContainer
│   └── devcontainer.json
├── docker-compose.yml       # Orquestación de servicios
└── README.md
```

---

## 🚀 Guía de Uso Rápido

### Primera Vez en el Sistema

1. **Registrarse**: Crear cuenta con email y contraseña
2. **Completar Perfil**: Ingresar información personal:
   - Situación laboral (No trabaja / Medio tiempo / Tiempo completo)
   - Lugar de residencia (Capital / Interior)
   - Situación familiar (Vive solo, tiene hijos, etc.)
3. **Marcar Materias**: Indicar qué materias ya tienes:
   - ✅ Aprobadas
   - 🟡 Regulares
   - 📝 Preparando Final
4. **Ver tu Arquetipo**: El sistema detectará automáticamente tu perfil
5. **Obtener Recomendaciones**: 
   - Ir a Dashboard
   - Ver planes de cursada sugeridos
   - Revisar estrategias de exámenes

### Simular un Cuatrimestre

1. Ir a la sección de **Simulador**
2. Seleccionar las materias que quieres cursar
3. Ver qué plan se aplicaría y las advertencias del sistema

### Consultar Consejos por Materia

1. Seleccionar una materia específica
2. Elegir tipo de consejo: **Cursada** o **Examen**
3. Leer los tips personalizados

---

# Manual de Usuario / Guía de Instalación

A continuación se detallan los pasos para instalar y ejecutar el sistema. Se recomienda utilizar **Docker** para una instalación rápida y sin conflictos de dependencias.

## Requisitos Previos

*   **Opción Recomendada (Docker):**
    *   [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y ejecutándose.
    *   Git.

*   **Opción Manual (Desarrollo Local):**
    *   Python 3.10 o superior.
    *   Node.js 18 o superior.
    *   PostgreSQL (instancia local).

---

## Opción 1: Instalación con DevContainers (Recomendado)

Esta opción utiliza **Visual Studio Code** con **DevContainers** para levantar automáticamente un entorno de desarrollo completo con la base de datos, el backend y el frontend configurados para trabajar juntos. Todo se ejecuta dentro de contenedores Docker, garantizando consistencia entre diferentes máquinas.

### Requisitos Previos para DevContainers

Antes de comenzar, asegúrate de tener instalado:

*   **[Visual Studio Code](https://code.visualstudio.com/)** - Editor de código
*   **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** - Motor de contenedores (debe estar **ejecutándose**)
*   **Extensiones de VS Code** (se instalarán en el paso siguiente):
    *   `Dev Containers` (ms-vscode-remote.remote-containers)
    *   `Docker` (ms-azuretools.vscode-docker)

### Pasos de Instalación

#### 1. **Clonar el Repositorio**

Abre una terminal y ejecuta:

```bash
git clone <URL_DEL_REPOSITORIO>
cd SBC_FIUNJU
```

#### 2. **Abrir el Proyecto en VS Code**

Abre Visual Studio Code y carga la carpeta del proyecto:

```bash
code .
```

O desde VS Code: `File > Open Folder...` y selecciona la carpeta `SBC_FIUNJU`.

#### 3. **Instalar las Extensiones Requeridas**

Si aún no tienes las extensiones instaladas, VS Code te sugerirá instalarlas automáticamente. También puedes instalarlas manualmente:

1.  Abre la paleta de comandos: **`Ctrl + Shift + P`** (Windows/Linux) o **`Cmd + Shift + P`** (Mac)
2.  Escribe: `Extensions: Install Extensions`
3.  Busca e instala:
    *   **Dev Containers**
    *   **Docker**

#### 4. **Abrir el Proyecto en el DevContainer**

Este paso construye e inicia todos los contenedores necesarios (base de datos, backend, frontend).

1.  Presiona **`Ctrl + Shift + P`** (o **`Cmd + Shift + P`** en Mac)
2.  Escribe y selecciona: **`Dev Containers: Reopen in Container`**
3.  Espera a que se construyan las imágenes y se instalen las dependencias

> **⏱️ Nota:** La primera vez, este proceso puede tardar **5-10 minutos** mientras se descargan las imágenes base de Docker y se instalan todas las dependencias de Python y Node.js.

VS Code se recargará automáticamente dentro del contenedor. Verás un indicador en la esquina inferior izquierda que dice **"Dev Container: SBC_FIUNJU"**.

#### 5. **Generar la Ontología**

La ontología es el "cerebro" del sistema basado en conocimiento. Debes generarla antes de usar la aplicación.

1.  En VS Code, abre el archivo: `backend/generar_ontologia.py`
2.  Haz clic en el botón **▶️ Run Python File** en la esquina superior derecha
3.  Alternativamente, abre una terminal integrada y ejecuta:
    ```bash
    cd backend
    python generar_ontologia.py
    ```

Esto generará el archivo `fiunju_ontologia.ttl` que contiene el grafo de conocimiento del plan de estudios.

#### 6. **Inicializar la Base de Datos**

Ahora debes crear las tablas necesarias en la base de datos PostgreSQL.

Abre una terminal integrada en VS Code (`Terminal > New Terminal`) y ejecuta:

```bash
cd backend
alembic upgrade head
```

Este comando aplicará todas las migraciones de la base de datos.

#### 7. **Reiniciar el DevContainer**

Para asegurar que todos los servicios estén sincronizados y funcionando correctamente:

1.  Presiona **`Ctrl + Shift + P`** (o **`Cmd + Shift + P`** en Mac)
2.  Escribe y selecciona: **`Dev Containers: Rebuild Container`**
3.  Espera a que el contenedor se reconstruya y se reinicie

> **💡 Tip:** Este paso reinicia todos los servicios con la configuración actualizada. Es útil hacerlo después de cambios importantes en la configuración.

#### 8. **Verificar que el Sistema Está Funcionando**

Una vez completados todos los pasos, verifica que todo funcione correctamente:

*   **Frontend (Interfaz Web):** Abre tu navegador en [http://localhost:3000](http://localhost:3000)
*   **Backend (API y Documentación):** [http://localhost:8000/docs](http://localhost:8000/docs)
*   **Base de Datos:** Accesible mediante herramientas como pgAdmin en `localhost:5432`
    *   Usuario: `postgres`
    *   Contraseña: `miPasswordSecreta`
    *   Base de datos: `sbc_db`

---

### Comandos Útiles para Desarrollo

Una vez dentro del DevContainer, puedes usar estos comandos:

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload  # Reiniciar el servidor FastAPI
alembic revision --autogenerate -m "descripción"  # Crear migración
alembic upgrade head  # Aplicar migraciones
python generar_ontologia.py  # Regenerar ontología
```

**Frontend:**
```bash
cd frontend
npm run dev  # Iniciar servidor de desarrollo Next.js
npm run build  # Construir para producción
npm run lint  # Verificar código
```

### Reiniciar/Detener el Sistema

*   **Reabrir en Container:** `Ctrl+Shift+P` > `Dev Containers: Reopen in Container`
*   **Cerrar Container y volver local:** `Ctrl+Shift+P` > `Dev Containers: Reopen Folder Locally`
*   **Reconstruir Container:** `Ctrl+Shift+P` > `Dev Containers: Rebuild Container`

---

## Opción 2: Instalación Manual (Paso a Paso)

Si prefieres ejecutar los servicios individualmente en tu máquina local para desarrollo.

### 1. Base de Datos (PostgreSQL)
Asegúrate de tener un servidor PostgreSQL corriendo.
*   Crea una base de datos llamada `sbc_db`.
*   Ten a mano la URL de conexión (ej. `postgresql://usuario:password@localhost:5432/sbc_db`).

### 2. Backend (Python/FastAPI)

1.  Navega al directorio del backend:
    ```bash
    cd backend
    ```
2.  Crea y activa un entorno virtual:
    *   **Mac/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configura la conexión a la base de datos:
    *   Establece la variable de entorno `DATABASE_URL` o modifícala directamente en `app/core/database.py` (no recomendado para producción).
    *   Ejemplo (Linux/Mac): `export DATABASE_URL="postgresql://postgres:password@localhost:5432/sbc_db"`
5.  Ejecuta las migraciones de base de datos:
    ```bash
    alembic upgrade head
    ```
6.  Inicia el servidor:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    *El backend estará corriendo en `http://localhost:8000`.*

### 3. Frontend (Next.js)

1.  Navega al directorio del frontend:
    ```bash
    cd frontend
    ```
2.  Instala las dependencias de Node.js:
    ```bash
    npm install
    ```
3.  Configura la conexión con el backend:
    *   Crea un archivo `.env.local` en la carpeta `frontend` y agrega la siguiente línea para que el proxy de Next.js apunte a tu backend local:
    ```env
    BACKEND_URL="http://127.0.0.1:8000/:path*"
    ```
4.  Inicia el servidor de desarrollo:
    ```bash
    npm run dev
    ```
5.  Accede a la aplicación en [http://localhost:3000](http://localhost:3000).

---

## 📝 Licencia

Este proyecto fue desarrollado como parte de un Sistema Basado en Conocimiento para la Facultad de Ingeniería de la UNJU.

## 👥 Contribuciones

Si deseas contribuir al proyecto, por favor contacta con los mantenedores del repositorio.

---

**¡Buena suerte con tu carrera! 🎓**