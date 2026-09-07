import models 
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

# Esquema para la creación y actualización de usuarios
class UsuarioBase(BaseModel):
    """Esquema base para la creación y actualización de usuarios."""
    nombre: str
    email: EmailStr
    rol: models.RolUsuario = models.RolUsuario.OPERADOR_INVENTARIO
    sucursal_id: Optional[int] = None  # Permitir que sea nulo si el usuario no está asignado a una sucursal
    activo: bool = True  # Por defecto, el usuario está activo

# Esquema para la creación de un usuario (POST)
class UsuarioCreate(UsuarioBase):
    """Esquema para la creación de un usuario (POST)."""
    password: str  # Contraseña en texto plano, que será hasheada antes de almacenar

# Esquema para la salida de datos del usuario, excluyendo la contraseña (GET)
class UsuarioOut(UsuarioBase):  
    """Esquema para la salida de datos del usuario, excluyendo la contraseña (GET)."""
    id: int
    creado_en: datetime

    class Config:
        from_attributes = True  # Permite la conversión desde objetos ORM a Pydantic

# Esquema para actualizar datos generales del perfil (SIN ROL ni PASSWORD) (PUT/PATCH)
class UsuarioUpdatePerfil(BaseModel):
    """Esquema para actualizar datos generales del perfil (SIN ROL ni PASSWORD) (PUT/PATCH)."""
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None

# Esquema exclusivo para cambiar el rol de un usuario
class UsuarioCambiarRol(BaseModel):
    """Esquema exclusivo para cambiar el rol de un usuario."""
    rol: models.RolUsuario

# Esquema exclusivo para cambiar el usuario de sucursal (PUT/PATCH)
class UsuarioCambiarSucursal(BaseModel):
    """Esquema exclusivo para cambiar el usuario de sucursal (PUT/PATCH)."""
    sucursal_id: Optional[int] = None
