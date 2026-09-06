import schemas, models, auth
import enum 

from typing import List
from fastapi import APIRouter, Depends, HTTPException

#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db

router = APIRouter( prefix="/proveedores", tags=["proveedores"])


# Endpoints para obtener todos los proveedores
@router.get("/", response_model=List[schemas.ProveedorOut])
def obtener_proveedores(db: Session = Depends(get_db)):
    """Obtiene todos los proveedores activos."""
    proveedores = db.query(models.Proveedor).filter(models.Proveedor.activo == True).all()
    return proveedores


# Endpoint para obtener un proveedor por su ID  
@router.get("/{proveedor_id}", response_model=schemas.ProveedorOut)
def obtener_proveedor(proveedor_id: int, db: Session = Depends(get_db)):
    """Obtiene un proveedor activo por su ID."""
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id, models.Proveedor.activo == True).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor

# Endpoint para crear un nuevo proveedor
@router.post("/", response_model=schemas.ProveedorOut)
def crear_proveedor(
    datos: schemas.ProveedorCreate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):

    """Crea un nuevo proveedor."""
    existente = db.query(models.Proveedor).filter(models.Proveedor.nombre == datos.nombre, models.Proveedor.activo == True).first()
    if existente:
        raise HTTPException(status_code=400, detail="Proveedor ya existe")
    
    nuevo_proveedor = models.Proveedor(**datos.model_dump())
    db.add(nuevo_proveedor)
    db.commit()
    db.refresh(nuevo_proveedor)
    return nuevo_proveedor


# Endpoint para actualizar un proveedor existente
@router.put("/{proveedor_id}", response_model=schemas.ProveedorOut)
def actualizar_proveedor(
    proveedor_id: int,
    datos: schemas.ProveedorUpdate,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Actualiza un proveedor activo por su ID."""
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id, models.Proveedor.activo == True).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    if not proveedor.activo:
        raise HTTPException(status_code=400, detail="Proveedor está desactivado")

    proveedor_actualizado = datos.model_dump(exclude_unset=True)
    for campo, valor in proveedor_actualizado.items():
        setattr(proveedor, campo, valor)
    
    db.commit()
    db.refresh(proveedor)
    return proveedor

# Endpoint para activar un proveedor (borrado lógico inverso)
@router.put("/{proveedor_id}/activar", response_model=schemas.ProveedorOut)
def activar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Activa un proveedor previamente desactivado (borrado lógico inverso)."""

    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    proveedor.activo = True
    db.commit()
    db.refresh(proveedor)
    return proveedor


# Endpoint para eliminar un proveedor (borrado lógico)  
@router.delete("/{proveedor_id}", status_code=204)
def eliminar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Elimina un proveedor del sistema (borrado lógico)."""

    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    proveedor.activo = False
    db.commit()
    return proveedor
