import schemas, models, auth
import enum 

from typing import List
from fastapi import APIRouter, Depends, HTTPException

#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db



router = APIRouter(prefix="/usuarios", tags=["usuarios"])


#   Endpoint para listar todos los usuarios
@router.get("", response_model=List[schemas.UsuarioOut])
def obtener_usuarios(db: Session = Depends(get_db)):
    """Retorna la lista de todos los usuarios en el sistema."""

    usuarios = db.query(models.Usuario).all()
    return usuarios


# Endpoint para obtener los roles disponibles para un usuario
@router.get("/roles", response_model=List[str])
def obtener_roles_disponibles():
    """Retorna la lista de todos los roles válidos definidos en el sistema."""
    return [rol.value for rol in models.RolUsuario]


# Endpoint para obtener un usuario por su ID
@router.get("/{usuario_id}", response_model=schemas.UsuarioOut)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Retorna los detalles de un usuario específico por su ID."""

    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


# Endpoint para crear un nuevo usuario
@router.post("", response_model=schemas.UsuarioOut, status_code=201)
def crear_usuario(
    datos: schemas.UsuarioCreate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Crea un nuevo usuario en el sistema. Los roles permitidos son: admin_general, gerente_sucursal, operador_inventario.
    Si se proporciona un sucursal_id, se valida que la sucursal exista."""

    # Validar que el email no esté ya registrado
    usuario_existente = db.query(models.Usuario).filter(models.Usuario.email == datos.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    # Validar que la surcursal exista si se proporciona un sucursal_id
    if datos.sucursal_id:
        sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == datos.sucursal_id).first()
        if not sucursal:
            raise HTTPException(status_code=400, detail="Sucursal no encontrada")

    # Convertir la contraseña a hash antes de guardarla
    payload = datos.model_dump()
    password_plano = payload.pop("password") #extrae la contraseña del diccionario y la elimina de payload
    # Convertir la contraseña a hash antes de guardarla
    payload["password_hash"] = auth.hash_password(password_plano)

    # Crear el usuario
    usuario_nuevo = models.Usuario(**payload)
    db.add(usuario_nuevo)
    db.commit()
    db.refresh(usuario_nuevo)  # trae de vuelta el id y creado_en que Postgres genero
    return usuario_nuevo


# Endpoint para actualizar los datos del perfil de un usuario existente
@router.put("/{usuario_id}/perfil", response_model=schemas.UsuarioOut)
def actualizar_perfil(
    usuario_id: int,
    datos: schemas.UsuarioUpdatePerfil,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
):
    """Actualiza los datos del perfil de un usuario existente en el sistema."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.activo:
        raise HTTPException(status_code=400, detail="No se puede actualizar el perfil de un usuario inactivo")

    usuario_actualizado = datos.model_dump(exclude_unset=True)
    for campo, valor in usuario_actualizado.items():
        setattr(usuario, campo, valor)

    db.commit()
    db.refresh(usuario)
    return usuario


# Endpoint para cambiar el rol de un usuario existente
@router.put("/{usuario_id}/rol", response_model=schemas.UsuarioOut)
def cambiar_rol(
    usuario_id: int,
    nuevo_rol: schemas.UsuarioCambiarRol,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
):
    """Cambia el rol de un usuario existente en el sistema."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.activo:
        raise HTTPException(status_code=400, detail="No se puede cambiar el rol de un usuario inactivo")

    usuario.rol = nuevo_rol.rol
    db.commit()
    db.refresh(usuario)
    return usuario


# Endpoint para cambiar el estado de un usuario existente
@router.put("/{usuario_id}/estado", response_model=schemas.UsuarioOut)
def cambiar_estado(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
):
    """Cambia el estado (activo/inactivo) de un usuario existente en el sistema."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario.activo:
        raise HTTPException(status_code=400, detail="El usuario ya está activo")

    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario


# Endpoint para desactivar un usuario existente
@router.delete("/{usuario_id}", status_code=204)
def desactivar_usuario(
    usuario_id: int, 
    db: Session = Depends(get_db), 
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))):

    """Desactiva un usuario existente en el sistema. No se elimina físicamente de la base de datos."""
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.activo:
        raise HTTPException(status_code=400, detail="El usuario ya está inactivo")
    
    usuario.activo = False  # Marcamos el usuario como inactivo en lugar de eliminarlo físicamente
    db.commit()
    db.refresh(usuario)
    return usuario
