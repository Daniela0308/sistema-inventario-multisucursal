# Uso de Inteligencia Artificial

## 1. Herramientas utilizadas

Durante el desarrollo del proyecto se utilizaron:

* **GitHub Copilot:** apoyo en análisis, revisión y desarrollo de código.
* **ChatGPT:** apoyo en análisis técnico, documentación y revisión de requerimientos.

## 2. Etapas de utilización

| Etapa         | Herramienta       | Uso                                                          |
| ------------- | ----------------- | ------------------------------------------------------------ |
| Arquitectura  | GitHub Copilot    | Análisis de estructura y separación de capas                 |
| Backend       | GitHub Copilot    | Revisión de routers, servicios y endpoints                   |
| Base de datos | GitHub Copilot    | Análisis de modelos y relaciones                             |
| Seguridad     | GitHub Copilot    | Revisión de autenticación, JWT y permisos                    |
| Procesos      | GitHub Copilot    | Identificación de funcionalidades implementadas y pendientes |
| Documentación | ChatGPT / Copilot | Apoyo en organización y redacción técnica                    |

## 3. Prompts utilizados

### Prompt 1 - Análisis de arquitectura

> Analiza la estructura completa del proyecto e identifica cómo están separadas las capas frontend, backend y base de datos. Indica qué tecnologías utiliza cada una y cómo se comunican entre sí.

**Resultado:** permitió identificar la arquitectura basada en React + Vite, FastAPI y PostgreSQL, además de la comunicación mediante API REST.

### Prompt 2 - Análisis del backend

> Analiza los routers, modelos, schemas y servicios del backend. Identifica los endpoints existentes, qué función cumple cada uno y qué operaciones están realmente implementadas.

**Resultado:** permitió documentar los endpoints disponibles y diferenciar las funcionalidades realmente implementadas de las que solamente estaban contempladas en la estructura de la base de datos.

### Prompt 3 - Revisión de funcionalidades

> Revisa las funcionalidades requeridas para un sistema de inventario multisucursal y compáralas con el código actual. Clasifica cada funcionalidad como implementada, parcial o pendiente, sin asumir que una tabla de base de datos significa que la funcionalidad está terminada.

**Resultado:** permitió identificar como implementados los módulos de autenticación, productos, sucursales, usuarios e inventario, y como pendientes los módulos de compras, ventas, transferencias, logística y dashboard.

## 4. Validación humana

Las respuestas y sugerencias generadas mediante inteligencia artificial no fueron incorporadas automáticamente.

El desarrollador realizó revisión manual del código, estructura del proyecto, endpoints, modelos de base de datos y funcionamiento general antes de documentar cada funcionalidad.

También se verificó que la existencia de una tabla, endpoint o componente no fuera considerada automáticamente como una funcionalidad terminada si no existía el flujo completo entre frontend, backend y base de datos.

## 5. Evaluación crítica

La inteligencia artificial fue utilizada como herramienta de apoyo y no como sustituto de las decisiones técnicas.

Sus principales aportes fueron:

* Reducir el tiempo de análisis del código.
* Facilitar la identificación de relaciones entre componentes.
* Apoyar la revisión de seguridad.
* Facilitar la organización de la documentación.
* Detectar funcionalidades pendientes.

Los resultados requirieron validación porque una herramienta de IA puede interpretar incorrectamente una funcionalidad o asumir que un componente está terminado únicamente por su existencia en el código.

## 6. Porcentaje estimado de participación de IA

La participación de IA debe diferenciar entre código generado, código modificado, análisis y documentación.

**Porcentaje estimado de participación de IA: ______ %.**

Este porcentaje representa una estimación del apoyo de inteligencia artificial y no significa que el proyecto haya sido generado completamente por IA.

## 7. Conclusión

La IA permitió agilizar tareas de análisis, revisión y documentación durante el desarrollo. Sin embargo, las decisiones finales, validaciones y ajustes realizados sobre el proyecto fueron responsabilidad del desarrollador.
