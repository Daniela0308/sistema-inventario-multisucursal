import models

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field


class InventarioOut(BaseModel):
    """Forma del JSON que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    producto_id: int
    sucursal_id: int
    cantidad: Decimal
    costo_promedio: Decimal

    class Config:
        from_attributes = True

class MovimientoCreate(BaseModel):
    """Forma del JSON que la API RECIBE (POST) para registrar un movimiento de inventario."""
    producto_id: int
    sucursal_id: int
    tipo: models.TipoMovimiento
    cantidad: int
    motivo: Optional[str] = None
    referencia: Optional[str] = None

class MovimientoOut(BaseModel):
    """Forma del JSON que la API DEVUELVE (GET, y tambien la respuesta de POST) para un movimiento de inventario."""
    id: int
    producto_id: int
    sucursal_id: int
    tipo: models.TipoMovimiento
    cantidad: int
    motivo: Optional[str]
    referencia: Optional[str]
    usuario_id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True

# Esquema para el ajuste
class AjusteInventarioSchema(BaseModel):
    producto_id: int
    cantidad_real: int  # La cantidad correcta que realmente HAY en la estantería
    motivo: str         # Ej: "Corrección por error de digitación anterior"
    sucursal_id: Optional[int] = Field(None, description="Requerido si el usuario es ADMIN_GENERAL")

# Esquema para registrar un movimiento de inventario sin especificar la sucursal (se usa la sucursal del usuario logueado)
class MovimientoCreateSinSucursal(BaseModel):
    """Forma del JSON que la API RECIBE (POST) para registrar un movimiento de inventario directamente en la sucursal del usuario logueado."""
    producto_id: int
    tipo: models.TipoMovimiento
    cantidad: int
    motivo: Optional[str] = None
    referencia: Optional[str] = None