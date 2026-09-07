import schemas, models, auth

from typing import List
from fastapi import APIRouter, Depends, HTTPException

#la variable db va a ser un objeto de tipo Session y sirve para hacer consultas a la base de datos
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db

router = APIRouter(prefix="/sucursales", tags=["sucursales"])


# Endpoint para obtener todas las sucursales
@router.get("", response_model=List[schemas.SucursalOut])
def obtener_sucursales(db: Session = Depends(get_db)):
    """Retorna la lista de todas las sucursales en el sistema."""

    sucursales = db.query(models.Sucursal).all()
    return sucursales


# Endpoint para obtener una sucursal por su ID
@router.get("/{sucursal_id}", response_model=schemas.SucursalOut)
def obtener_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    """Retorna los detalles de una sucursal específica por su ID."""

    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()
    if sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")
    return sucursal


# Endpoint para crear una nueva sucursal
@router.post("", response_model=schemas.SucursalOut, status_code=201)
def crear_sucursal(
    datos: schemas.SucursalCreate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
):
    """Crea una nueva sucursal en el sistema."""

    existente = db.query(models.Sucursal).filter(models.Sucursal.nombre == datos.nombre).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una sucursal con ese nombre")

    nueva_sucursal = models.Sucursal(**datos.model_dump())
    db.add(nueva_sucursal)
    db.commit()
    db.refresh(nueva_sucursal)  # trae de vuelta el id y creado_en que Postgres genero
    return nueva_sucursal


# Endpoint para actualizar una sucursal existente
@router.put("/{sucursal_id}", response_model=schemas.SucursalOut)
def actualizar_sucursal(
    sucursal_id: int, 
    datos: schemas.SucursalUpdate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Actualiza los detalles de una sucursal existente."""

    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()
    if sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    # Dejar un diccionario con solo los campos que el cliente mando, para no sobreescribir los demas
    sucursal_actualizado = datos.model_dump(exclude_unset=True)
    # Actualizar los campos
    for campo, valor in sucursal_actualizado.items():
        setattr(sucursal, campo, valor)

    db.commit()
    db.refresh(sucursal)
    return sucursal


# Endpoint para activar una sucursal
@router.put("/{sucursal_id}/activar", response_model=schemas.SucursalOut)
def activar_sucursal(
    sucursal_id: int, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Activa una sucursal en el sistema."""

    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()
    if sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    sucursal.activo = True
    db.commit()
    db.refresh(sucursal)
    return sucursal


# Endpoint para eliminar una sucursal
@router.delete("/{sucursal_id}", status_code=204)
def eliminar_sucursal(
    sucursal_id: int, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))):
    """Elimina una sucursal del sistema (borrado lógico)."""
    
    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == sucursal_id).first()
    if sucursal is None:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    sucursal.activo = False  # Marcamos la sucursal como inactiva en lugar de eliminarla físicamente
    db.commit()
    db.refresh(sucursal)
  