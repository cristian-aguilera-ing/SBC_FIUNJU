# Análisis del Proyecto SBC_FIUNJU

Este proyecto es una aplicación web completa (Full Stack) diseñada, para brindar asistencia académica a estudiantes de la Facultad de Ingeniería de la UNJU (FIUNJU), utilizando tecnologías de **Sistemas Basados en Conocimiento (SBC)**.

## Arquitectura General

El sistema está orquestado mediante **Docker Compose** y consta de tres servicios principales:

1.  **Backend (API & Lógica SBC)**
2.  **Frontend (Interfaz de Usuario)**
3.  **Base de Datos (Persistencia)**

---

## 1. Backend (`/backend`)

El backend está construido con **Python** y **FastAPI**. Su función principal es exponer una API y gestionar una **Ontología** (Grafo de Conocimiento) que modela el plan de estudios.

*   **Tecnologías Clave:**
    *   **FastAPI:** Framework web moderno y rápido para construir APIs.
    *   **RDFLib & OWLRL:** Librerías para trabajar con Web Semántica (RDF, OWL) y razonamiento lógico.
    *   **PostgreSQL & SQLAlchemy:** Base de datos relacional y ORM.
    *   **Alembic:** Para migraciones de base de datos.

*   **Archivo Clave: `generar_ontologia.py`**
    *   Este script es el "cerebro" del conocimiento. Define una ontología OWL que modela:
        *   **Materias:** (Obligatorias, Optativas) con sus créditos, años y requisitos.
        *   **Dificultades:** Niveles de dificultad para cursada y exámenes.
        *   **Modalidades de Examen:** (Oral, Escrito, Multiple Choice).
        *   **Factores Personales y Académicos:** (Trabajo, hábitos de estudio, situación familiar).
    *   Puebla el grafo con datos reales de la carrera (ej. *Sistemas Operativos I*, *Estructura de Datos*).
    *   Ejecuta un razonador (`owlrl`) para inferir nuevo conocimiento y exporta el resultado a un archivo `.ttl` (Turtle).

## 2. Frontend (`/frontend`)

El frontend es una aplicación moderna construida con **Next.js 16** y **TypeScript**.

*   **Tecnologías Clave:**
    *   **Next.js 16:** Framework de React para producción.
    *   **TypeScript:** JavaScript tipado para mayor robustez.
    *   **Tailwind CSS:** Framework de utilidades para estilos.
    *   **Shadcn/ui:** (Inferido por dependencias como `@radix-ui` y `class-variance-authority`) Una colección de componentes de UI reutilizables y accesibles.
    *   **Axios:** Para realizar peticiones HTTP al backend.

## 3. Infraestructura

*   **Docker Compose:** Define y corre los contenedores para que todo el entorno de desarrollo se levante con un solo comando.
*   **Base de Datos:** Imagen oficial de `postgres:15-alpine`.

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

## Opción 1: Ejecución Rápida con Docker (Recomendado)

Esta opción levanta automáticamente la base de datos, el backend y el frontend configurados para trabajar juntos.

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd SBC_FIUNJU
    ```

2.  **Iniciar el sistema:**
    Ejecuta el siguiente comando en la raíz del proyecto (donde está el archivo `docker-compose.yml`):
    ```bash
    docker-compose up --build
    ```
    *Este proceso puede tardar unos minutos la primera vez mientras se descargan las imágenes y se instalan las dependencias.*

3.  **Acceder al Sistema:**
    *   **Frontend (Aplicación Web):** Abre tu navegador en [http://localhost:3000](http://localhost:3000).
    *   **Backend (Documentación API):** [http://localhost:8000/docs](http://localhost:8000/docs).
    *   **Base de Datos:** Accesible en `localhost:5432` (Usuario: `postgres`, Password: `miPasswordSecreta`, DB: `sbc_db`).

4.  **Detener el sistema:**
    Presiona `Ctrl + C` en la terminal o ejecuta:
    ```bash
    docker-compose down
    ```

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