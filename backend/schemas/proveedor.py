from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, EmailStr

class ProveedorOut(BaseModel):
    id: int
    nombre: str
    direccion: Optional[str] = None
    telefono: str
    email: EmailStr
    activo: bool = True

    class Config:
        from_attributes = True

class ProveedorCreate(BaseModel):
    nombre: str
    direccion: Optional[str] = None
    telefono: str
    email: EmailStr

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[EmailStr] = None
    activo: Optional[bool] = None