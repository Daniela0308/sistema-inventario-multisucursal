"""models/inventario.py - Tablas `inventarios` y `movimientos_inventario`."""
import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


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

    producto = relationship("Producto", back_populates="movimientos") # uno a muchos: un producto puede tener muchos movimientos de inventario
    sucursal = relationship("Sucursal", back_populates="movimientos") # uno a muchos: una sucursal puede tener muchos movimientos de inventario
    usuario = relationship("Usuario", back_populates="movimientos")
