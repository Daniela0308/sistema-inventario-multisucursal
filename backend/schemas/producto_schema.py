from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

class ProductoOut(BaseModel):
    """Forma del JSON que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    sku: str
    nombre: str
    descripcion: Optional[str] = None
    unidad_medida: str
    stock_minimo: int
    precio_venta: Decimal
    activo: bool

    class Config:
        from_attributes = True

class ProductoCreate(BaseModel):
    """
    Forma del JSON que la API ESPERA RECIBIR al crear un producto (POST).
    Diferencias clave con ProductoOut:
    - NO tiene "id": el id lo genera Postgres solo (SERIAL), nadie desde
      afuera debe poder decidir el id de un producto nuevo.
    - NO tiene "activo": todo producto nuevo nace activo por default.
    - unidad_medida y stock_minimo son opcionales aqui (con valor por
      defecto), igual que en tu init.sql, para que el cliente no este
      obligado a mandarlos si no le importan.
    """
    sku: str
    nombre: str
    descripcion: Optional[str] = None
    unidad_medida: str = "unidad"
    stock_minimo: int = 5
    precio_venta: Decimal = Decimal("0.00")
    activo: bool = True

class ProductoUpdate(BaseModel):
    """
    Forma del JSON que la API espera recibir al ACTUALIZAR un producto
    (PUT). Todos los campos son Optional a proposito: permite que el
    cliente mande solo los campos que quiere cambiar, sin obligarlo a
    reenviar el producto completo cada vez que edita, por ejemplo, solo
    el precio.
    """
    sku: Optional[str] = None
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    unidad_medida: Optional[str] = None
    stock_minimo: Optional[int] = None
    precio_venta: Optional[Decimal] = None
    activo: Optional[bool] = None
