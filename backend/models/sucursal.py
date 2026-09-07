"""models/sucursal.py - Tabla `sucursales`."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


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
    ordenes_compra = relationship("OrdenCompra", back_populates="sucursal") # uno a muchos: una sucursal puede tener muchas ordenes de compra
    ventas = relationship("Venta", back_populates="sucursal") # uno a muchos: una sucursal puede tener muchas ventas
    transferencias_enviadas = relationship("Transferencia", foreign_keys="Transferencia.sucursal_origen_id", back_populates="sucursal_origen") # uno a muchos: una sucursal puede enviar muchas transferencias
    transferencias_recibidas = relationship("Transferencia", foreign_keys="Transferencia.sucursal_destino_id", back_populates="sucursal_destino") # uno a muchos: una sucursal puede recibir muchas transferencias
