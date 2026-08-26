# Sistema de Inventario Multi-Sucursal - OptiPlant

## 1. Descripción del proyecto

Aplicación web para la gestión de inventario de múltiples sucursales de una misma organización.

El sistema busca permitir que cada sucursal gestione sus operaciones de inventario de manera independiente, manteniendo al mismo tiempo visibilidad y coherencia de la información entre las diferentes sucursales.

La solución se desarrolla bajo una arquitectura separada por capas, compuesta por frontend, backend y base de datos, comunicados mediante una API.

## 2. Arquitectura

La solución adopta una arquitectura desacoplada en tres capas principales:

- **Frontend:** responsable de la presentación y de la interacción con el usuario.
- **Backend:** responsable de la lógica de negocio, validaciones y exposición de la API.
- **Base de datos:** responsable del almacenamiento persistente de la información.

La comunicación entre el frontend y el backend se realizará exclusivamente mediante la API, manteniendo la lógica de negocio centralizada en el backend.

Esta separación responde directamente a los requisitos técnicos definidos para la prueba.

### Arquitectura general

┌──────────────────────────────┐
│          FRONTEND            │
│     Interfaz de usuario      │
└──────────────┬───────────────┘
               │
               │ REST API
               ▼
┌──────────────────────────────┐
│           BACKEND            │
│           FastAPI            │
│       Lógica de negocio      │
└──────────────┬───────────────┘
               │
               │ SQL
               ▼
┌──────────────────────────────┐
│          DATABASE            │
│         PostgreSQL           │
└──────────────────────────────┘

## 3. Stack tecnológico
### 3.1 Python

Python fue seleccionado como lenguaje principal del backend debido a la experiencia previa con el lenguaje y al conocimiento adquirido durante el desarrollo de otros proyectos.

Además, su ecosistema permite utilizar diferentes herramientas y frameworks orientados al desarrollo de APIs y aplicaciones backend.

### 3.2 FastAPI

FastAPI fue seleccionado como framework para el desarrollo del backend.

Una de las principales razones de esta elección es la necesidad de mantener una separación clara entre frontend, backend y base de datos. FastAPI permite desarrollar el backend como una API independiente, evitando acoplar la lógica de negocio a la capa de presentación.

Esta decisión también permite que el frontend consuma los servicios del sistema mediante endpoints REST.

Otra razón para utilizar FastAPI es su enfoque orientado al desarrollo de APIs y su buen rendimiento, características que resultan adecuadas para una aplicación que debe manejar operaciones de inventario y comunicación entre diferentes sucursales.

### 3.3 PostgreSQL

PostgreSQL fue seleccionado como motor de base de datos debido a la experiencia previa con esta tecnología y a su afinidad con el stack utilizado para el backend.

El sistema requiere manejar información relacionada entre productos, sucursales, inventarios, movimientos, compras, ventas y transferencias, por lo que se utilizará un modelo de datos relacional.

PostgreSQL permitirá mantener la integridad y consistencia de las relaciones entre las diferentes entidades del sistema.

### 3.4 Docker

Docker se utiliza para contenerizar los diferentes componentes de la aplicación.

La solución se estructura mediante servicios independientes para frontend, backend y base de datos, permitiendo que el proyecto pueda ejecutarse de manera reproducible mediante Docker Compose.

Esto facilita la configuración del entorno de desarrollo y permite mantener aisladas las diferentes capas de la aplicación.