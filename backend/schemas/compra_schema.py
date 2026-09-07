import models

from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import List

# Esquema para crear las ordenes de compra (ejm: carrito de compras )
class DetalleCompraIn(BaseModel):
    """
    Forma de UNA línea dentro del JSON que el cliente manda al crear
    una orden. Fíjate que NO tiene "id" ni "orden_compra_id" -- esos los
    genera el backend, el cliente solo dice QUÉ quiere comprar.
    """
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    descuento_pct: Decimal = Decimal("0")

# Esquema para la salida de los detalles de compra (con id)
class DetalleCompraOut(DetalleCompraIn):
    """
    Forma de UNA línea en la RESPUESTA. Hereda todos los campos de
    DetalleCompraIn (producto_id, cantidad, precio_unitario,
    descuento_pct) y le agrega el "id" real que sí existe una vez
    guardado en la base de datos.
    """
    id: int

    class Config:
        from_attributes = True

# Esquema para crear una orden de compra (cabecera + detalles)
class OrdenCompraCreate(BaseModel):
    """
    Forma del JSON completo que el cliente manda para crear una orden.
    "detalles" es una LISTA de DetalleCompraIn -- el cliente puede
    mandar varios productos distintos en una sola petición.
    """
    proveedor_id: int
    sucursal_id: int
    plazo_pago_dias: int = 0
    detalles: List[DetalleCompraIn]

# Esquema para la salida de una orden de compra completa (cabecera + detalles)
class OrdenCompraOut(BaseModel):
    """
    Forma de la RESPUESTA completa: la cabecera de la orden, MÁS la
    lista completa de sus líneas ya guardadas (con su id real cada una).
    """
    id: int
    proveedor_id: int
    sucursal_id: int
    usuario_id: int
    estado: models.EstadoOrdenCompra
    plazo_pago_dias: int
    fecha_registro: datetime
    detalles: List[DetalleCompraOut]

    class Config:
        from_attributes = True