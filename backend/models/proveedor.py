"""models/proveedor.py - Tabla `proveedores`."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Modelo de proveedor.
class Proveedor(Base):
    __tablename__ = 'proveedores'

    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    direccion = Column(String(200))
    telefono = Column(String(20))
    email = Column(String(100))
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ordenes_compra = relationship("OrdenCompra", back_populates="proveedor") # uno a muchos: un proveedor puede tener muchas órdenes de compra
