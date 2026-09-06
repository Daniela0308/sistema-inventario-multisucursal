import models
import schemas

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from auth.security import verify_password, crear_token

router = APIRouter(prefix="/auth", tags=["autenticacion"])

# Endpoint para el login de usuarios
@router.post("/login", response_model=schemas.TokenOut)
def login(datos: schemas.LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()

    # Fijate: el mismo mensaje de error tanto si el email no existe como
    # si la contraseña esta mal. Es a proposito -- si dijeras "email no
    # encontrado" vs "contraseña incorrecta", le estarias regalando a un
    # atacante la informacion de que emails SI existen en tu sistema.
    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")

    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = crear_token({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer", "usuario": usuario}