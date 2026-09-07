import schemas
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Esquema para la solicitud de inicio de sesión."""
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    """Esquema para la respuesta de autenticación con token."""
    access_token: str
    token_type: str
    usuario: schemas.UsuarioOut