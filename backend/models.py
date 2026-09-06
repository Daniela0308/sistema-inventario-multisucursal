"""
models.py
=========
Cada clase = una tabla que YA existe en Postgres (creada por db/init.sql).
Estas clases no crean nada; solo le dicen a SQLAlchemy "así se ve cada
tabla" para poder leer/escribir usando objetos Python en vez de SQL a mano.

Reglas de nombres usadas en todo el archivo:
- __tablename__          -> plural, EXACTO al nombre real en Postgres.
- Nombre de la clase      -> singular
- relationship() plural   -> cuando el atributo es una LISTA ("uno a muchos").
- relationship() singular -> cuando el atributo es UN SOLO objeto ("muchos a uno").
"""

import enum
from sqlalchemy import  (
    Column, Integer, String, Numeric, Boolean, DateTime, 
    Enum, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# =====================================================================
# 1. SUCURSALES
# =====================================================================
class Sucursal(Base):
    __tablename__ = 'sucursales'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(String(200))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuarios = relationship("Usuario", back_populates="sucursal") # muchos a uno: muchos usuarios pueden pertenecer a una sucursal
    inventarios = relationship("Inventario", back_populates="sucursal") # uno a muchos: una sucursal puede tener muchos registros de inventario (uno por producto)
    movimientos = relationship("MovimientoInventario", back_populates="sucursal") # uno a muchos: una sucursal puede tener muchos movimientos de inventario
# =====================================================================
# 2. USUARIOS
# =====================================================================
# Roles de usuario, para controlar permisos de acceso a la API
class RolUsuario(str, enum.Enum):
    ADMIN_GENERAL = "admin_general"
    GERENTE_SUCURSAL = "gerente_sucursal"
    OPERADOR_INVENTARIO = "operador_inventario"

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    rol = Column(
        Enum(
            RolUsuario, 
            name="rol_usuario", 
            create_type=False, 
            values_callable=lambda obj: [e.value for e in obj] 
        ), # Convierte los objetos Enum a sus strings en minúscula (.value)
        nullable=False,
        default=RolUsuario.OPERADOR_INVENTARIO,
    )
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sucursal = relationship("Sucursal", back_populates="usuarios") # muchos a uno: muchos usuarios pueden pertenecer a una sucursal
    movimientos = relationship("MovimientoInventario", back_populates="usuario") # uno a muchos: un usuario puede registrar muchos movimientos de inventario
# =====================================================================
# 3. PRODUCTOS
# =====================================================================
class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True)
    sku = Column(String(50), nullable=False, unique=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(String(500))
    unidad_medida = Column(String(20), nullable=False, default='unidad')
    stock_minimo = Column(Integer, nullable=False, default=5)
    precio_venta = Column(Numeric(12, 2), nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inventarios = relationship("Inventario", back_populates="producto") # uno a muchos: un producto puede tener muchos registros de inventario (uno por sucursal)
    movimientos = relationship("MovimientoInventario", back_populates="producto") # uno a muchos: un producto puede tener muchos movimientos de inventario

# =====================================================================
# 4. INVENTARIO
# =====================================================================

# Tipos de movimiento de inventario
class TipoMovimiento(str, enum.Enum):
    INGRESO_COMPRA = "ingreso_compra"
    INGRESO_DEVOLUCION = "ingreso_devolucion"
    INGRESO_AJUSTE = "ingreso_ajuste"
    INGRESO_TRANSFERENCIA = "ingreso_transferencia"
    RETIRO_VENTA = "retiro_venta"
    RETIRO_MERMA = "retiro_merma"
    RETIRO_AJUSTE = "retiro_ajuste"
    RETIRO_TRANSFERENCIA = "retiro_transferencia"

# Modelos de inventario y movimientos de inventario
class Inventario(Base):
    __tablename__ = 'inventarios'
    __table_args__ = (
        UniqueConstraint('producto_id', 'sucursal_id', name='uq_producto_sucursal'),
    ) # Cada producto puede tener un solo registro de inventario por sucursal

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    cantidad = Column(Integer, nullable=False, default=0)
    costo_promedio = Column(Numeric(12, 4), nullable=False, default=0)

    producto = relationship("Producto", back_populates="inventarios")
    sucursal = relationship("Sucursal", back_populates="inventarios")

class MovimientoInventario(Base):
    __tablename__ = 'movimientos_inventario'

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    tipo = Column(
        Enum(
            TipoMovimiento, 
            name="tipo_movimiento", 
            create_type=False, 
            values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    cantidad = Column(Integer, nullable=False)
    motivo = Column(String(300))
    referencia = Column(String(100))
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    producto = relationship("Producto", back_populates="movimientos")
    sucursal = relationship("Sucursal", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")


# =====================================================================
# 5. PROVEEDORES
# =====================================================================
class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20))
    email = Column(String(100))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)