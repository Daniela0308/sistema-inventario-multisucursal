"""models/producto.py - Tabla `productos`."""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Modelo de producto.
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
    detalles_compra = relationship("DetalleCompra", back_populates="producto") # uno a muchos: un producto puede tener muchos detalles de compra
    detalles_venta = relationship("DetalleVenta", back_populates="producto") # uno a muchos: un producto puede tener muchos detalles de venta
    transferencias = relationship("Transferencia", back_populates="producto") # uno a muchos: un producto puede tener muchas transferencias entre sucursales
    alertas = relationship("Alerta", back_populates="producto") # uno a muchos: un producto puede tener muchas alertas
