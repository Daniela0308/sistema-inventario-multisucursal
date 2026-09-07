"""models/venta.py - Tablas `ventas` y `detalle_venta`."""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Venta(Base):
    __tablename__ = 'ventas'

    id = Column(Integer, primary_key=True)
    sucursal_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total = Column(Numeric(12, 2), nullable=False, default=0)

    sucursal = relationship("Sucursal", back_populates="ventas")
    usuario = relationship("Usuario", back_populates="ventas")
    detalles_venta = relationship("DetalleVenta", back_populates="venta", cascade="all, delete-orphan")


class DetalleVenta(Base):
    __tablename__ = 'detalle_venta'

    id = Column(Integer, primary_key=True)
    venta_id = Column(Integer, ForeignKey('ventas.id', ondelete="CASCADE"), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    descuento_pct = Column(Numeric(5, 2), nullable=False, default=0)

    venta = relationship("Venta", back_populates="detalles_venta")
    producto = relationship("Producto", back_populates="detalles_venta")
