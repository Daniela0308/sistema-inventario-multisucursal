# Estado del Proyecto

## 1. Funcionalidades implementadas

| Funcionalidad                        | Estado         |
| ------------------------------------ | -------------- |
| Arquitectura Frontend / Backend / BD | ✅ Implementado |
| Docker Compose                       | ✅ Implementado |
| PostgreSQL                           | ✅ Implementado |
| Autenticación JWT                    | ✅ Implementado |
| Roles y permisos (con validación de sucursal en backend) | ✅ Implementado |
| CRUD de productos                    | ✅ Implementado |
| CRUD de sucursales                   | ✅ Implementado |
| Gestión de usuarios                  | ✅ Implementado |
| Gestión de proveedores               | 🟡 Parcial     |
| Consulta de inventario (stock, cualquier sucursal) | ✅ Implementado |
| Entradas y salidas de inventario     | ✅ Implementado |
| Ajustes de inventario                | 🟡 Parcial     |
| Historial de movimientos (solo admin_general) | ✅ Implementado |
| Alertas de stock bajo                | 🟡 Parcial     |
| Módulo de compras (borrador → confirmar → recibir) | ✅ Implementado |
| Módulo de ventas (descuento inmediato de stock)     | ✅ Implementado |
| Modelos de transferencias y alertas (Paso 1)       | ✅ Implementado |
| Esquemas API de transferencias (Paso 2)             | ✅ Implementado |
| Servicio de transferencias (Paso 3)                 | ✅ Implementado |

## 2. Funcionalidades pendientes

| Funcionalidad                     | Estado       |
| --------------------------------- | ------------ |
| Transferencias entre sucursales (modelos, esquemas y servicio; falta router/pantalla) | 🟡 Parcial |
| Gestión logística                 | 🔴 Pendiente |
| Dashboard de indicadores          | 🔴 Pendiente |
| Costo promedio ponderado en todos los flujos | 🟡 Parcial |
| Unidades de medida y conversiones | 🔴 Pendiente |
| Reportes avanzados                | 🔴 Pendiente |
| Auditoría completa                | 🟡 Parcial   |

## 3. Observación

Las funcionalidades se consideran implementadas cuando existe integración funcional entre **Frontend, Backend y Base de Datos**.

Las tablas o estructuras existentes en `db/init.sql` no se consideran funcionalidades terminadas si todavía no cuentan con su flujo completo.

### Trazabilidad del módulo de transferencias

**Paso 1 completado:** se alinearon los modelos SQLAlchemy con las tablas `transferencias` y `alertas`. La transferencia ahora contempla la cantidad faltante, el tratamiento aplicado (`reenvio`, `ajuste` o `reclamacion`) y las observaciones de recepción parcial. También se agregó el modelo `Alerta` para poder persistir alertas asociadas a transferencias.

**Paso 2 completado:** se agregaron los esquemas Pydantic para crear solicitudes, preparar cantidades, registrar despachos, confirmar recepciones y devolver alertas relacionadas. Las validaciones que dependen del estado almacenado, como comparar la cantidad recibida con la enviada, se implementaron en el servicio durante el Paso 3.

**Paso 3 completado:** se agregó el servicio de transferencias. El flujo valida estados, disponibilidad en origen, cantidades enviadas y recibidas, actualiza el inventario mediante `registrar_movimiento` y crea una alerta persistente cuando la recepción es parcial.

Todavía no se han implementado los endpoints ni la pantalla frontend. Por ese motivo, el módulo continúa marcado como parcial.

## 4. Próximos desarrollos

Se priorizará la implementación de:

1. Transferencias entre sucursales (router, registro en `main.py` y pantalla, sobre los modelos, esquemas y servicio existentes).
2. Dashboard de indicadores.
3. Reportes y mejoras de seguridad adicionales.
4. Unidades de medida y conversiones.
