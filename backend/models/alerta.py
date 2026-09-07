"""models/alerta.py - Tabla `alertas`."""
import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base

# Tipos de alerta disponibles.
class TipoAlerta(str, enum.Enum):
    STOCK_BAJO = "stock_bajo"
    STOCK_AGOTADO = "stock_agotado"
    TRANSFERENCIA_FALTANTE = "transferencia_faltante"

# Modelo de alerta.
class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True)
    tipo = Column(
        Enum(
            TipoAlerta,
            name="tipo_alerta",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    producto_id = Column(Integer, ForeignKey("productos.id"))
    sucursal_id = Column(Integer, ForeignKey("sucursales.id"), nullable=False)
    transferencia_id = Column(Integer, ForeignKey("transferencias.id"))
    mensaje = Column(String(300), nullable=False)
    resuelta = Column(Boolean, nullable=False, default=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    transferencia = relationship("Transferencia", back_populates="alertas") # uno a muchos: una transferencia puede tener muchas alertas
    producto = relationship("Producto", back_populates="alertas") # uno a muchos: un producto puede tener muchas alertas
    sucursal = relationship("Sucursal", back_populates="alertas") # uno a muchos: una sucursal puede tener muchas alertas