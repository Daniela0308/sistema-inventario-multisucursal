from typing import Optional
from pydantic import BaseModel

class SucursalOut(BaseModel):
    id: int
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    activo: bool

    class Config:
        from_attributes = True

class SucursalCreate(BaseModel):
    nombre: str
    ciudad: str
    direccion: Optional[str] = None
    activo: bool = True

class SucursalUpdate(BaseModel):
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None
