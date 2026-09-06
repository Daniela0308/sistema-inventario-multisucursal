# Sistema de Inventario Multi-Sucursal - OptiPlant

## 1. Descripción

OptiPlant es un sistema web para la gestión de inventario en múltiples sucursales. Permite administrar productos, sucursales, usuarios, proveedores y movimientos de inventario, manteniendo trazabilidad sobre las operaciones realizadas.

Proyecto académico desarrollado como parte de una evaluación técnica de desarrollo de software.

## 2. Objetivo

Desarrollar una solución centralizada para controlar el inventario de diferentes sucursales mediante una arquitectura de tres capas, una API REST, autenticación y una base de datos relacional.

## 3. Funcionalidades implementadas

Actualmente el sistema cuenta con:

* Inicio de sesión mediante autenticación JWT.
* Gestión de usuarios y roles.
* Gestión de productos.
* Gestión de sucursales.
* Gestión básica de proveedores.
* Consulta de inventario por sucursal.
* Registro de entradas y salidas de inventario.
* Ajustes de inventario.
* Historial de movimientos.
* Alertas de stock bajo mediante API.
* Control de permisos según el rol del usuario.

## 4. Roles del sistema

### Administrador general

* Gestionar productos.
* Gestionar sucursales.
* Gestionar usuarios y roles.
* Gestionar proveedores.
* Consultar información general.

### Gerente de sucursal

* Consultar información de su sucursal.
* Supervisar inventario y movimientos según sus permisos.

### Operador de inventario

* Consultar inventario.
* Registrar movimientos de inventario.
* Realizar operaciones autorizadas.

## 5. Arquitectura

El sistema utiliza una arquitectura de tres capas:

```text
┌─────────────────────────────┐
│          FRONTEND           │
│        React + Vite         │
└──────────────┬──────────────┘
               │ HTTP / REST
               ▼
┌─────────────────────────────┐
│          BACKEND            │
│      Python + FastAPI       │
│   SQLAlchemy + Pydantic     │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│       BASE DE DATOS         │
│        PostgreSQL 15        │
└─────────────────────────────┘
```

El frontend se comunica con el backend mediante una API REST. La lógica de negocio y las validaciones se ejecutan principalmente en el backend.

## 6. Tecnologías utilizadas

### Frontend

* React 18
* Vite 5
* JavaScript
* HTML
* CSS
* Node.js 20

### Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT
* Passlib
* bcrypt

### Base de datos

* PostgreSQL 15

### Infraestructura

* Docker
* Docker Compose

## 7. Estructura del proyecto

```text
sistema-inventario-multisucursal/
│
├── backend/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── producto.py
│   │   ├── sucursal.py
│   │   ├── usuario.py
│   │   ├── inventario.py
│   │   └── proveedor.py
│   │
│   ├── schemas/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── security.py
│   ├── services.py
│   └── seed.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── AuthContext.jsx
│   ├── Dockerfile
│   └── package.json
│
├── db/
│   └── init.sql
│
├── docs/
│   └── uso-ia.md
│
├── docker-compose.yml
└── README.md
```

## 8. Base de datos

La base de datos utiliza PostgreSQL y contempla entidades para:

* Sucursales.
* Usuarios.
* Productos.
* Inventarios.
* Movimientos de inventario.
* Proveedores.
* Órdenes de compra.
* Detalles de compra.
* Ventas.
* Detalles de venta.
* Transferencias.
* Alertas.

Las entidades de compras, ventas y transferencias están contempladas en el esquema inicial, pero requieren integración completa con backend y frontend para considerarse funcionalidades terminadas.

## 9. API REST

### Autenticación

```text
POST /auth/login
```

### Productos

```text
GET    /productos
GET    /productos/{producto_id}
POST   /productos
PUT    /productos/{producto_id}
PUT    /productos/{producto_id}/activar
DELETE /productos/{producto_id}
```

### Sucursales

```text
GET    /sucursales
GET    /sucursales/{sucursal_id}
POST   /sucursales
PUT    /sucursales/{sucursal_id}
PUT    /sucursales/{sucursal_id}/activar
DELETE /sucursales/{sucursal_id}
```

### Usuarios

```text
GET    /usuarios
GET    /usuarios/roles
GET    /usuarios/{usuario_id}
POST   /usuarios
PUT    /usuarios/{usuario_id}/perfil
PUT    /usuarios/{usuario_id}/rol
PUT    /usuarios/{usuario_id}/estado
DELETE /usuarios/{usuario_id}
```

### Inventario

```text
POST /inventarios/movimientos
POST /inventarios/movimientos/mi-sucursal
POST /inventarios/movimientos/ajustar-stock

GET /inventarios/mi-sucursal
GET /inventarios/movimientos
GET /inventarios/alerta-stock-bajo
GET /inventarios/{sucursal_id}
```

### Proveedores

```text
GET    /proveedores/
GET    /proveedores/{proveedor_id}
POST   /proveedores/
PUT    /proveedores/{proveedor_id}
PUT    /proveedores/{proveedor_id}/activar
DELETE /proveedores/{proveedor_id}
```

## 10. Seguridad

El sistema implementa:

* Autenticación mediante JWT.
* Contraseñas almacenadas mediante hash.
* Control de acceso basado en roles.
* Protección de operaciones de escritura.
* Validación de datos mediante Pydantic.
* Manejo de errores HTTP.
* Verificación de usuarios activos.
* Tokens Bearer para solicitudes autenticadas.

Como mejora pendiente, los secretos y credenciales sensibles deben gestionarse mediante variables de entorno y no permanecer directamente en el código fuente.

## 11. Docker

El proyecto utiliza Docker Compose para ejecutar tres servicios:

```text
db       → PostgreSQL 15
backend  → FastAPI
frontend → React + Vite
```

PostgreSQL utiliza un volumen para conservar la información de la base de datos.

El frontend utiliza Node.js 20 Alpine y ejecuta Vite en modo desarrollo.

## 12. Ejecución

### Requisitos

* Docker
* Docker Compose

### Iniciar el proyecto

```bash
docker compose up --build
```

### Servicios

```text
Frontend:     http://localhost:5173
Backend:      http://localhost:8000
Base de datos: localhost:5433
```

### Detener el proyecto

```bash
docker compose down
```

## 13. Estado actual del proyecto

### Implementado

* Arquitectura frontend, backend y base de datos.
* Docker Compose.
* Autenticación JWT.
* Autorización por roles.
* CRUD de productos.
* CRUD de sucursales.
* Gestión de usuarios.
* Gestión básica de proveedores.
* Consulta de inventario.
* Movimientos de inventario.
* Ajustes de stock.
* Historial de movimientos.
* API de alertas de stock bajo.

### Pendiente de integración completa

* Módulo de compras.
* Módulo de ventas.
* Transferencias entre sucursales.
* Gestión logística y estados de despacho.
* Dashboard de indicadores.
* Cálculo integrado del costo promedio ponderado.
* Manejo completo de unidades de medida y conversiones.
* Interfaz visual de alertas.
* Reportes avanzados y exportables.

## 14. Documentación técnica

La documentación contempla:

* Levantamiento de requerimientos.
* Requerimientos funcionales y no funcionales.
* Casos de uso.
* Diagramas de procesos.
* Diagrama de arquitectura.
* Modelo entidad-relación.
* Descripción de API.
* Seguridad.
* Uso de inteligencia artificial.
* Estado de implementación de funcionalidades.

Los documentos se encuentran en:

```text
/docs
```

## 15. Uso de inteligencia artificial

Durante el desarrollo se utilizaron GitHub Copilot y ChatGPT como herramientas de apoyo para el análisis de arquitectura, código, API, base de datos, seguridad y documentación.

Las sugerencias generadas fueron revisadas, validadas y ajustadas manualmente antes de incorporarse al proyecto.

La evidencia detallada se encuentra en:

```text
docs/uso-ia.md
```

## 16. Historial de desarrollo

El proyecto cuenta con un historial de commits que permite identificar la evolución de sus principales componentes:

1. Inicialización del proyecto.
2. Configuración de Docker.
3. Configuración de PostgreSQL y esquema inicial.
4. Desarrollo del CRUD de productos con FastAPI, SQLAlchemy y Pydantic.

Los cambios posteriores se registrarán mediante commits descriptivos asociados a cada funcionalidad desarrollada.

## 17. Repositorio

Repositorio público:

https://github.com/Daniela0308/sistema-inventario-multisucursal

## 18. Licencia

Proyecto académico desarrollado con fines educativos y de evaluación técnica.
