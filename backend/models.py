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
    creado_en = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

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





