from typing import Optional
from pydantic import BaseModel

class SucursalOut(BaseModel):
    """Esquema para la representación de una sucursal que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True

class SucursalCreate(BaseModel):
    """Esquema para la creación de una sucursal (POST)."""
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    activo: bool = True

class SucursalUpdate(BaseModel):
    """Esquema para la actualización de una sucursal (PUT/PATCH)."""
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
