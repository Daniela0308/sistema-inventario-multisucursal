"""models/usuario.py - Tabla `usuarios` y el enum de roles."""
import enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


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
    ordenes_compra = relationship("OrdenCompra", back_populates="usuario") # uno a muchos: un usuario puede registrar muchas ordenes de compra
    ventas = relationship("Venta", back_populates="usuario") # uno a muchos: un usuario puede registrar muchas ventas
    transferencias_solicitadas = relationship("Transferencia", back_populates="usuario_solicita") # uno a muchos: un usuario puede solicitar muchas transferencias
