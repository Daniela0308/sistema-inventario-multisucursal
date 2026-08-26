-- =====================================================================
-- Sistema de Inventario Multi-Sucursal - Esquema de Base de Datos
-- =====================================================================
-- Este archivo es la version "SQL plano" del modelo que SQLAlchemy genera
-- automaticamente desde backend/app/models/*.py (Base.metadata.create_all).
-- No es necesario ejecutarlo a mano: el backend crea las tablas al
-- arrancar. Se incluye para documentacion, para el diagrama E-R, y para
-- quien quiera inspeccionar/crear la BD sin levantar el backend.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. SUCURSALES
-- ---------------------------------------------------------------------
CREATE TABLE sucursales (
    id          SERIAL PRIMARY KEY,  --entero que autoincrementa
    nombre      VARCHAR(100) NOT NULL UNIQUE,
    ciudad      VARCHAR(100) NOT NULL,
    direccion   VARCHAR(200)
);

-- ---------------------------------------------------------------------
-- 2. USUARIOS
-- sucursal_id es NULL solo para ADMIN_GENERAL (visibilidad de toda la red).
-- password_hash: NUNCA se guarda la contrasena en texto plano (bcrypt).
-- ---------------------------------------------------------------------
CREATE TYPE rol_usuario AS ENUM ('admin_general', 'gerente_sucursal', 'operador_inventario'); --tipo de dato enumerado

CREATE TABLE usuarios (
    id              SERIAL PRIMARY KEY,
    nombre          VARCHAR(120) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    rol             rol_usuario NOT NULL DEFAULT 'operador_inventario',
    sucursal_id     INTEGER REFERENCES sucursales(id), --llave foranea
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- 3. PRODUCTOS (catalogo global, compartido por toda la red)
-- ---------------------------------------------------------------------
CREATE TABLE productos (
    id              SERIAL PRIMARY KEY,
    sku             VARCHAR(50) NOT NULL UNIQUE,
    nombre          VARCHAR(150) NOT NULL,
    descripcion     VARCHAR(500),
    unidad_medida   VARCHAR(20) NOT NULL DEFAULT 'unidad',
    stock_minimo    INTEGER NOT NULL DEFAULT 5,
    precio_venta    NUMERIC(12,2) NOT NULL DEFAULT 0,
    activo          BOOLEAN NOT NULL DEFAULT TRUE
);

-- ---------------------------------------------------------------------
-- 4. INVENTARIOS (stock de un producto EN una sucursal)
-- ---------------------------------------------------------------------
CREATE TABLE inventarios (
    id              SERIAL PRIMARY KEY,
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    sucursal_id     INTEGER NOT NULL REFERENCES sucursales(id),
    cantidad        INTEGER NOT NULL DEFAULT 0,
    costo_promedio  NUMERIC(12,4) NOT NULL DEFAULT 0,
    UNIQUE (producto_id, sucursal_id) --impide que haya dos registros para el mismo producto en la misma sucursal
);

-- ---------------------------------------------------------------------
-- 5. MOVIMIENTOS_INVENTARIO (bitacora inmutable, auditoria)
-- ---------------------------------------------------------------------
CREATE TYPE tipo_movimiento AS ENUM (
    'ingreso_compra', 'ingreso_devolucion', 'ingreso_ajuste', 'ingreso_transferencia',
    'retiro_venta', 'retiro_merma', 'retiro_ajuste', 'retiro_transferencia'
);

CREATE TABLE movimientos_inventario (
    id              SERIAL PRIMARY KEY,
    producto_id     INTEGER NOT NULL REFERENCES productos(id),
    sucursal_id     INTEGER NOT NULL REFERENCES sucursales(id),
    tipo            tipo_movimiento NOT NULL,
    cantidad        INTEGER NOT NULL,
    motivo          VARCHAR(300),
    referencia      VARCHAR(100),
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- 6. PROVEEDORES
-- ---------------------------------------------------------------------
CREATE TABLE proveedores (
    id          SERIAL PRIMARY KEY,
    nombre      VARCHAR(150) NOT NULL,
    contacto    VARCHAR(150),
    telefono    VARCHAR(30),
    email       VARCHAR(120)
);

-- ---------------------------------------------------------------------
-- 7. ORDENES_COMPRA y DETALLE_COMPRA
-- ---------------------------------------------------------------------
CREATE TYPE estado_orden_compra AS ENUM ('borrador', 'confirmada', 'cancelada');

CREATE TABLE ordenes_compra (
    id                  SERIAL PRIMARY KEY,
    proveedor_id        INTEGER NOT NULL REFERENCES proveedores(id),
    sucursal_id         INTEGER NOT NULL REFERENCES sucursales(id),
    usuario_id          INTEGER NOT NULL REFERENCES usuarios(id),
    estado              estado_orden_compra NOT NULL DEFAULT 'borrador',
    plazo_pago_dias     INTEGER NOT NULL DEFAULT 0,
    fecha               TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE detalle_compra (
    id                  SERIAL PRIMARY KEY,
    orden_compra_id     INTEGER NOT NULL REFERENCES ordenes_compra(id) ON DELETE CASCADE, --impediría borrar la orden mientras tenga detalles asociados
    producto_id         INTEGER NOT NULL REFERENCES productos(id),
    cantidad            INTEGER NOT NULL,
    precio_unitario     NUMERIC(12,2) NOT NULL,
    descuento_pct       NUMERIC(5,2) NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------
-- 8. VENTAS y DETALLE_VENTA
-- ---------------------------------------------------------------------
CREATE TABLE ventas (
    id              SERIAL PRIMARY KEY,
    sucursal_id     INTEGER NOT NULL REFERENCES sucursales(id),
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    fecha           TIMESTAMP NOT NULL DEFAULT NOW(),
    total           NUMERIC(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE detalle_venta (
    id                  SERIAL PRIMARY KEY,
    venta_id            INTEGER NOT NULL REFERENCES ventas(id) ON DELETE CASCADE,
    producto_id         INTEGER NOT NULL REFERENCES productos(id),
    cantidad            INTEGER NOT NULL,
    precio_unitario     NUMERIC(12,2) NOT NULL,
    descuento_pct       NUMERIC(5,2) NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------
-- 9. TRANSFERENCIAS (maquina de estados)
-- ---------------------------------------------------------------------
CREATE TYPE estado_transferencia AS ENUM (
    'solicitada', 'en_preparacion', 'en_transito', 'recibida', 'recibida_parcial', 'rechazada'
);
CREATE TYPE urgencia_transferencia AS ENUM ('baja', 'media', 'alta');

CREATE TABLE transferencias (
    id                          SERIAL PRIMARY KEY,
    producto_id                 INTEGER NOT NULL REFERENCES productos(id),
    sucursal_origen_id          INTEGER NOT NULL REFERENCES sucursales(id),
    sucursal_destino_id         INTEGER NOT NULL REFERENCES sucursales(id),
    cantidad_solicitada         INTEGER NOT NULL,
    cantidad_enviada            INTEGER,
    cantidad_recibida           INTEGER,
    estado                      estado_transferencia NOT NULL DEFAULT 'solicitada',
    urgencia                    urgencia_transferencia NOT NULL DEFAULT 'media',
    transportista                VARCHAR(100),
    fecha_solicitud              TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_estimada_llegada       TIMESTAMP,
    fecha_envio                  TIMESTAMP,
    fecha_recepcion              TIMESTAMP,
    usuario_solicita_id          INTEGER NOT NULL REFERENCES usuarios(id),
    observaciones                VARCHAR(500)
);

-- ---------------------------------------------------------------------
-- 10. ALERTAS (funcionalidad adicional: alertas inteligentes)
-- ---------------------------------------------------------------------
CREATE TYPE tipo_alerta AS ENUM ('stock_bajo', 'stock_agotado', 'transferencia_faltante');

CREATE TABLE alertas (
    id                  SERIAL PRIMARY KEY,
    tipo                tipo_alerta NOT NULL,
    producto_id         INTEGER REFERENCES productos(id),
    sucursal_id         INTEGER NOT NULL REFERENCES sucursales(id),
    transferencia_id    INTEGER REFERENCES transferencias(id),
    mensaje             VARCHAR(300) NOT NULL,
    resuelta            BOOLEAN NOT NULL DEFAULT FALSE,
    fecha               TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ---------------------------------------------------------------------
-- Indices adicionales (rendimiento en consultas frecuentes)
-- ---------------------------------------------------------------------
-- Estructura de indices para optimizar las consultas más frecuentes en la base de datos
CREATE INDEX idx_movimientos_producto_sucursal ON movimientos_inventario(producto_id, sucursal_id);
CREATE INDEX idx_transferencias_estado ON transferencias(estado);
CREATE INDEX idx_alertas_sucursal_resuelta ON alertas(sucursal_id, resuelta);