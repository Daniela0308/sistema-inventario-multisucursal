from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr

class ProveedorOut(BaseModel):
    """Esquema para la representación de un proveedor que la API DEVUELVE (GET, y tambien la respuesta de POST/PUT)."""
    id: int
    nombre: str
    direccion: Optional[str] = None
    telefono: str
    email: EmailStr
    activo: bool = True

    class Config:
        from_attributes = True

class ProveedorCreate(BaseModel):
    """Esquema para la creación de un proveedor (POST)."""
    nombre: str
    direccion: Optional[str] = None
    telefono: str
    email: EmailStr

class ProveedorUpdate(BaseModel):
    """Esquema para la actualización de un proveedor (PUT/PATCH)."""
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None