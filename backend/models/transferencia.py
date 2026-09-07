"""models/transferencia.py - Tabla `transferencias` (maquina de estados)."""
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class EstadoTransferencia(str, enum.Enum):
    SOLICITADA = "solicitada"
    EN_PREPARACION = "en_preparacion"
    EN_TRANSITO = "en_transito"
    RECIBIDA = "recibida"
    RECIBIDA_PARCIAL = "recibida_parcial"
    RECHAZADA = "rechazada"


class UrgenciaTransferencia(str, enum.Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"


class Transferencia(Base):
    __tablename__ = 'transferencias'

    id = Column(Integer, primary_key=True)
    producto_id = Column(Integer, ForeignKey('productos.id'), nullable=False)
    sucursal_origen_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    sucursal_destino_id = Column(Integer, ForeignKey('sucursales.id'), nullable=False)
    cantidad_solicitada = Column(Integer, nullable=False)
    cantidad_enviada = Column(Integer)
    cantidad_recibida = Column(Integer)
    estado = Column(
        Enum(
            EstadoTransferencia,
            name="estado_transferencia",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=EstadoTransferencia.SOLICITADA,
    )
    urgencia = Column(
        Enum(
            UrgenciaTransferencia,
            name="urgencia_transferencia",
            create_type=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=UrgenciaTransferencia.MEDIA,
    )
    transportista = Column(String(100))
    fecha_solicitud = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_estimada_llegada = Column(DateTime(timezone=True))
    fecha_envio = Column(DateTime(timezone=True))
    fecha_recepcion = Column(DateTime(timezone=True))
    usuario_solicita_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False)
    observaciones = Column(String(500))

    producto = relationship("Producto", back_populates="transferencias")
    # dos FKs a la misma tabla sucursales -> hay que indicar foreign_keys explicitamente
    sucursal_origen = relationship("Sucursal", foreign_keys=[sucursal_origen_id], back_populates="transferencias_enviadas")
    sucursal_destino = relationship("Sucursal", foreign_keys=[sucursal_destino_id], back_populates="transferencias_recibidas")
    usuario_solicita = relationship("Usuario", back_populates="transferencias_solicitadas")
