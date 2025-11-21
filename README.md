# Análisis del Proyecto SBC_FIUNJU

Este proyecto es una aplicación web completa (Full Stack) diseñada, aparentemente, para brindar asistencia académica a estudiantes de la Facultad de Ingeniería de la UNJU (FIUNJU), utilizando tecnologías de **Sistemas Basados en Conocimiento (SBC)**.

## Arquitectura General

El sistema está orquestado mediante **Docker Compose** y consta de tres servicios principales:

1.  **Backend (API & Lógica SBC)**
2.  **Frontend (Interfaz de Usuario)**
3.  **Base de Datos (Persistencia)**

---

## 1. Backend (`/backend`)

El backend está construido con **Python** y **FastAPI**. Su función principal parece ser exponer una API y gestionar una **Ontología** (Grafo de Conocimiento) que modela el plan de estudios.

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

## Conclusión

Es un sistema sofisticado que combina desarrollo web moderno con Inteligencia Artificial Simbólica (Ontologías). Probablemente su objetivo sea recomendar materias, predecir dificultades o asistir en la planificación de la carrera basándose tanto en las reglas duras del plan de estudios como en el perfil personal del estudiante.