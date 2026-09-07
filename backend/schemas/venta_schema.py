from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DetalleVentaIn(BaseModel):
    """Esquema para la entrada de detalles de venta (POST)."""
    producto_id: int
    cantidad: int
    # precio_unitario es OPCIONAL: si el cliente no lo manda, el
    # servicio usa el precio_venta que ya tiene el producto en catálogo
    # (requisito 3.3: "aplicar descuentos y gestionar diferentes listas
    # de precios" -- permitir override es lo que hace posible eso).
    precio_unitario: Optional[Decimal] = None
    descuento_pct: Decimal = Decimal("0")


class DetalleVentaOut(BaseModel):
    """Esquema para la representación de un detalle de venta que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: Decimal
    descuento_pct: Decimal

    class Config:
        from_attributes = True


class VentaCreate(BaseModel):
    """Esquema para la creación de una venta (POST)."""
    sucursal_id: int
    detalles: List[DetalleVentaIn]


class VentaOut(BaseModel):
    """Esquema para la representación de una venta que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    sucursal_id: int
    usuario_id: int
    fecha_registro: datetime
    total: Decimal
    # el modelo ORM expone la relación como "detalles_venta"
    detalles: List[DetalleVentaOut] = Field(validation_alias="detalles_venta", serialization_alias="detalles")

    class Config:
        from_attributes = True
        populate_by_name = True