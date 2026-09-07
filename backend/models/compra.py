"""models/compra.py - Tablas `ordenes_compra` y `detalle_compra`."""
import enum
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class EstadoOrdenCompra(str, enum.Enum):
    BORRADOR = "borrador"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"


# Se usa en la relación con DetalleCompra a través de la columna orden_compra_id.
class OrdenCompra(Base):
    __tablename__ = 'ordenes_compra'

    id = Column(Integer, primary_key=True)
    proveedor_id = Column(Integer, ForeignKey('proveedores.id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    estado = Column(
        Enum(
            EstadoOrdenCompra,
            name="estado_orden_compra",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],  # el mismo ajuste que usamos en rol y tipo_movimiento
        ),
        nullable=False,
        default=EstadoOrdenCompra.BORRADOR,
    )
    plazo_pago_dias = Column(Integer, nullable=False, default=0)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    proveedor = relationship("Proveedor", back_populates="ordenes_compra")
    sucursal = relationship("Sucursal", back_populates="ordenes_compra")
    usuario = relationship("Usuario", back_populates="ordenes_compra")
    # cascade="all, delete-orphan": si borras la orden desde el ORM,
    # sus detalles se borran con ella automáticamente.
    detalles = relationship("DetalleCompra", back_populates="orden", cascade="all, delete-orphan")


# Se usa en la relación con OrdenCompra a través de la columna orden_compra_id.
class DetalleCompra(Base):
    __tablename__ = 'detalle_compra'

    id = Column(Integer, primary_key=True)
    orden_compra_id = Column(Integer, ForeignKey('ordenes_compra.id', ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    descuento_pct = Column(Numeric(5, 2), nullable=False, default=0)

    orden = relationship("OrdenCompra", back_populates="detalles")
    producto = relationship("Producto", back_populates="detalles_compra")
