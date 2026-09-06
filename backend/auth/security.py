"""
auth/security.py
=================
Todo lo relacionado con seguridad de usuarios vive aqui:
  1) Hash de contraseñas (nunca se guarda texto plano en la BD).
  2) Generar y leer JWT (los "tokens" que representan una sesion).
  3) Dependencias de FastAPI para proteger endpoints: saber quien esta
     logueado (get_current_user) y exigir un rol especifico (requerir_roles).
"""

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from database import get_db
import models


# =====================================================================
# 1) HASH DE CONTRASEÑAS
# =====================================================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a un hash seguro (bcrypt)."""
    return pwd_context.hash(password)


def verify_password(password_plano: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano contra un hash ya guardado."""
    return pwd_context.verify(password_plano, password_hash)


# =====================================================================
# 2) JWT (crear y leer tokens)
# =====================================================================
# En un proyecto real, SECRET_KEY vendria de una variable de entorno
# (nunca hardcodeada en el codigo fuente ni subida a git).
SECRET_KEY = "cambia-esto-por-algo-largo-y-aleatorio-en-produccion"
ALGORITHM = "HS256"
MINUTOS_EXPIRACION = 480  # 8 horas


def crear_token(datos: dict) -> str:
    """
    Recibe un diccionario (ej: {"sub": "5"} = "este token es del usuario
    con id 5") y devuelve un token firmado. "sub" (subject) es el nombre
    estandar en JWT para "de quien trata este token".
    """
    datos_copia = datos.copy()
    expiracion = datetime.now(timezone.utc) + timedelta(minutes=MINUTOS_EXPIRACION)
    datos_copia["exp"] = expiracion  # "exp" es el campo estandar de JWT para expiracion
    return jwt.encode(datos_copia, SECRET_KEY, algorithm=ALGORITHM)


def leer_token(token: str) -> dict | None:
    """Verifica la firma y vigencia del token. Devuelve su contenido o None si es invalido."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# =====================================================================
# 3) DEPENDENCIAS: proteger endpoints
# =====================================================================
# Le dice a FastAPI como leer el header "Authorization: Bearer <token>".
# tokenUrl es solo informativo, para que el boton "Authorize" de /docs
# sepa a que endpoint apunta el login.
oauth2_scheme = HTTPBearer()


def get_current_user(
    credenciales = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    """
    Dependencia reutilizable: cualquier endpoint que la use con
    Depends(get_current_user) EXIGE un token valido. Si falta, esta
    vencido, o no corresponde a un usuario activo, corta con 401 antes
    de que el endpoint se ejecute.
    """
    token = credenciales.credentials  # Extrae el token del header "Authorization: Bearer <token>"
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la sesión",
    )

    payload = leer_token(token)
    if payload is None:
        raise credenciales_invalidas

    usuario_id = payload.get("sub")
    if usuario_id is None:
        raise credenciales_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.id == int(usuario_id)).first()
    if usuario is None or not usuario.activo:
        raise credenciales_invalidas

    return usuario


def requerir_roles(*roles_permitidos):
    """
    Factory de dependencia para restringir por rol, ej:
        Depends(requerir_roles(RolUsuario.ADMIN_GENERAL))
    Si el usuario logueado no tiene uno de los roles permitidos, corta
    con 403 (a diferencia del 401: aqui SI sabemos quien es, solo que
    no tiene permiso para esta accion).
    """
    def verificador(usuario_actual: models.Usuario = Depends(get_current_user)):
        if usuario_actual.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para realizar esta acción",
            )
        return usuario_actual
    return verificador