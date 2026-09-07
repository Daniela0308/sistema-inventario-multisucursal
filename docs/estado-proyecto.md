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

## 2. Funcionalidades pendientes

| Funcionalidad                     | Estado       |
| --------------------------------- | ------------ |
| Transferencias entre sucursales (modelo de datos ya existe, falta router/servicio/pantalla) | 🟡 Parcial |
| Gestión logística                 | 🔴 Pendiente |
| Dashboard de indicadores          | 🔴 Pendiente |
| Costo promedio ponderado en todos los flujos | 🟡 Parcial |
| Unidades de medida y conversiones | 🔴 Pendiente |
| Reportes avanzados                | 🔴 Pendiente |
| Auditoría completa                | 🟡 Parcial   |

## 3. Observación

Las funcionalidades se consideran implementadas cuando existe integración funcional entre **Frontend, Backend y Base de Datos**.

Las tablas o estructuras existentes en `db/init.sql` no se consideran funcionalidades terminadas si todavía no cuentan con su flujo completo.

## 4. Próximos desarrollos

Se priorizará la implementación de:

1. Transferencias entre sucursales (router + servicio + pantalla, sobre el modelo `Transferencia` ya existente).
2. Dashboard de indicadores.
3. Reportes y mejoras de seguridad adicionales.
4. Unidades de medida y conversiones.
