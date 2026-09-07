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
* Consulta de inventario por sucursal (cualquier rol puede consultar el stock de cualquier sucursal).
* Registro de entradas y salidas de inventario.
* Ajustes de inventario.
* Historial de movimientos (exclusivo del administrador general).
* Alertas de stock bajo mediante API.
* Módulo de compras: creación de órdenes (borrador), confirmación, recepción con actualización automática de inventario y costo promedio.
* Módulo de ventas: registro de ventas con descuento inmediato de stock y validación de disponibilidad.
* Alta rápida de proveedores y productos desde el propio flujo de compras/ventas (sin salir de la pantalla).
* Control de permisos según el rol del usuario, incluyendo validación de sucursal en el backend (un usuario no-admin no puede operar ni ver movimientos de otra sucursal aunque intente manipular la petición).
* Paso 1 del módulo de transferencias: modelos SQLAlchemy de transferencias y alertas alineados con el esquema de base de datos, incluyendo los datos de recepción parcial.
* Paso 2 del módulo de transferencias: esquemas Pydantic para solicitudes, preparación, despacho, recepción y alertas.
* Paso 3 del módulo de transferencias: servicio de negocio para solicitar, preparar, despachar y recibir transferencias, con actualización de inventario y alertas por faltantes.

## 4. Roles del sistema

### Administrador general

* Gestionar productos, sucursales, usuarios y proveedores.
* Visibilidad total: cualquier sucursal, cualquier movimiento, cualquier compra o venta.
* Único rol que puede consultar el historial de movimientos de inventario.
* Confirmar y recibir órdenes de compra de cualquier sucursal.

### Gerente de sucursal

* Supervisa las operaciones de **su propia sucursal** (compras, ventas, ajustes quedan forzados a su sucursal aunque el cliente intente mandar otra).
* Aprueba (confirma) y recibe órdenes de compra, pero solo las de su propia sucursal.
* Puede **consultar el inventario (stock) de cualquier sucursal** de la red, no solo la suya.
* No tiene acceso al historial de movimientos de inventario (exclusivo del admin).

### Operador de inventario

* Realiza ingresos y retiros de inventario, solicita ajustes y registra ventas/compras, siempre dentro de **su propia sucursal**.
* Puede **consultar el inventario (stock) de cualquier sucursal** de la red, no solo la suya.
* No tiene acceso al historial de movimientos de inventario (exclusivo del admin).
* No puede confirmar ni recibir órdenes de compra (reservado a gerente/admin).

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
│   │   ├── auth_router.py
│   │   ├── producto_router.py
│   │   ├── sucursal_router.py
│   │   ├── usuario_router.py
│   │   ├── inventario_router.py
│   │   ├── proveedor_router.py
│   │   ├── compra_router.py
│   │   └── venta_router.py
│   │
│   ├── schemas/
│   │   ├── auth_schema.py, producto_schema.py, sucursal_schema.py, usuario_schema.py
│   │   └── inventario_schema.py, proveedor_schema.py, compra_schema.py, venta_schema.py, transferencia_schema.py
│   │
│   ├── services/
│   │   ├── inventario_service.py
│   │   ├── compra_service.py
│   │   ├── venta_service.py
│   │   └── transferencia_service.py
│   │
│   ├── models/
│   │   ├── __init__.py  (re-exporta todas las clases)
│   │   ├── sucursal.py, usuario.py, producto.py, inventario.py
│   │   └── proveedor.py, compra.py, venta.py, transferencia.py, alerta.py
│   │
│   ├── auth/
│   │   └── security.py  (hash de contraseñas, JWT, dependencias de autorización)
│   │
│   ├── main.py
│   ├── database.py
│   └── seed.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx, ProductosPage.jsx, SucursalesPage.jsx
│   │   │   ├── UsuariosPage.jsx, InventarioPage.jsx
│   │   │   └── ComprasPage.jsx, VentasPage.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── db/
│   └── init.sql
│
├── docs/
│   ├── uso-ia.md
│   └── estado-proyecto.md
│
├── docker-compose.yml
└── README.md
```

> Nota: `schemas/`, `routers/` y `services/` usan el sufijo de capa (`_schema`, `_router`, `_service`) en el nombre de archivo para poder distinguirlos de un vistazo cuando hay varias pestañas abiertas en el editor con el mismo nombre base (ej. `compra_router.py` vs `compra_service.py`).

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

Las entidades de compras y ventas ya cuentan con integración completa (backend + frontend). El módulo de transferencias se encuentra en implementación por pasos: ya están completados los modelos, esquemas y servicio; todavía faltan el router, su registro en `main.py` y la pantalla frontend.

### Trazabilidad de cambios

* **Paso 1 - Capa de datos:** se agregó el modelo `Alerta`, se incorporó el tratamiento de faltantes al modelo `Transferencia` y se actualizó `db/init.sql` con el tipo enum y las nuevas columnas.
* **Paso 2 - Contratos API:** se agregó `transferencia_schema.py` con esquemas separados para solicitar, preparar, despachar y recibir transferencias, además de las respuestas de transferencias y alertas.
* **Paso 3 - Lógica de negocio:** se agregó `transferencia_service.py`. El despacho descuenta inventario en origen; la recepción ingresa únicamente la cantidad recibida en destino; las recepciones parciales guardan el faltante y generan una alerta.
* Los pasos 1 y 2 no implementaban el flujo operativo ni modificaban inventario; esa responsabilidad se incorporó en el Paso 3 mediante el servicio. Todavía falta exponerlo mediante endpoints.

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
POST /inventarios/movimientos                  (admin: cualquier sucursal / resto: forzado a la propia)
POST /inventarios/movimientos/mi-sucursal
POST /inventarios/movimientos/ajustar-stock

GET /inventarios/mi-sucursal
GET /inventarios/movimientos                    (exclusivo admin_general)
GET /inventarios/alerta-stock-bajo
GET /inventarios/{sucursal_id}                  (cualquier rol, cualquier sucursal)
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

### Compras

```text
POST /compras                        (crea orden en estado BORRADOR; sucursal forzada si no es admin)
POST /compras/{orden_id}/confirmar   (admin o gerente de esa sucursal)
POST /compras/{orden_id}/recibir     (admin o gerente de esa sucursal; actualiza inventario y costo promedio)
GET  /compras                        (admin ve todas; gerente/operador solo las de su sucursal)
GET  /compras/{orden_id}
```

### Ventas

```text
POST /ventas       (descuenta stock de inmediato; sucursal forzada si no es admin)
GET  /ventas       (admin ve todas; gerente/operador solo las de su sucursal)
GET  /ventas/{venta_id}
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
* Validación de sucursal en el backend para operaciones de compras, ventas y movimientos de inventario: un usuario no-admin no puede leer ni escribir datos de una sucursal distinta a la suya manipulando la petición directamente (ej. Postman o la consola del navegador). El `sucursal_id` que manda el cliente se ignora y se reemplaza por la sucursal real del usuario autenticado cuando no es `admin_general`.
* El historial de movimientos de inventario es visible únicamente para `admin_general`.

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
* Autorización por roles, con validación de sucursal en el backend (no solo en el frontend).
* CRUD de productos.
* CRUD de sucursales.
* Gestión de usuarios.
* Gestión básica de proveedores.
* Consulta de inventario (stock) de cualquier sucursal, para cualquier rol.
* Movimientos de inventario (visibles solo para admin_general).
* Ajustes de stock.
* Historial de movimientos.
* API de alertas de stock bajo.
* Módulo de compras completo: alta de orden (borrador) con carrito de líneas, alta rápida de proveedor/producto inline, confirmación y recepción con actualización de inventario y costo promedio.
* Módulo de ventas completo: registro con descuento inmediato de stock, precio de catálogo u override, validación de disponibilidad previa.
* Backend reorganizado: `models.py` dividido en paquete `models/` por dominio, y `schemas/`, `routers/`, `services/` con sufijo de capa para evitar archivos duplicados en el editor.

### Pendiente de integración completa

* Transferencias entre sucursales (modelos, esquemas y servicio implementados; falta router, registro en `main.py` y pantalla).
* Gestión logística y estados de despacho.
* Dashboard de indicadores.
* Cálculo integrado del costo promedio ponderado en todos los flujos (compras ya lo aplica).
* Manejo completo de unidades de medida y conversiones.
* Interfaz visual de alertas (hoy solo expuesta vía API).
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
