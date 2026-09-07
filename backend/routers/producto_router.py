import schemas, models, auth

from typing import List
from fastapi import APIRouter, Depends, HTTPException
#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db

router = APIRouter(prefix="/productos", tags=["productos"])


# Endpoint para obtener todos los productos
@router.get("", response_model=List[schemas.ProductoOut])
def obtener_productos(db: Session = Depends(get_db)):
    """Retorna la lista de todos los productos activos en el sistema."""

    productos = db.query(models.Producto).filter(models.Producto.activo == True).all()  # Solo productos activos
    return productos


# Endpoint para obtener un producto por su ID
@router.get("/{producto_id}", response_model=schemas.ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """Retorna los detalles de un producto específico por su ID."""

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return producto


# Endpoint para crear un nuevo producto
@router.post("", response_model=schemas.ProductoOut, status_code=201)
def crear_producto(
    datos: schemas.ProductoCreate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Crea un nuevo producto en el sistema."""

    existente = db.query(models.Producto).filter(models.Producto.sku == datos.sku).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese SKU")

    nuevo_producto = models.Producto(**datos.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)  # trae de vuelta el id y creado_en que Postgres genero
    return nuevo_producto


# Endpoint para actualizar un producto existente
@router.put("/{producto_id}", response_model=schemas.ProductoOut)
def actualizar_producto(
    producto_id: int, 
    datos: schemas.ProductoUpdate, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Actualiza los detalles de un producto existente."""

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if not producto.activo:
        raise HTTPException(status_code=400, detail="Producto está desactivado")
    
    # Deja un diccionario con solo los campos que el cliente mando, para no sobreescribir los demas
    producto_actualizado = datos.model_dump(exclude_unset=True)
    # Actualizar los campos del producto
    for campo, valor in producto_actualizado.items():
        setattr(producto, campo, valor)
    
    db.commit()
    db.refresh(producto)
    return producto


# Endpoint para activar un producto (borrado lógico inverso)
@router.put("/{producto_id}/activar", response_model=schemas.ProductoOut)
def activar_producto(
    producto_id: int, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Activa un producto previamente desactivado (borrado lógico inverso)."""

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.activo = True  # Marcamos el producto como activo
    db.commit()
    db.refresh(producto)
    return producto


# Endpoint para eliminar un producto (borrado lógico)
@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(
    producto_id: int, 
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL))
    ):
    """Elimina un producto del sistema (borrado lógico)."""

    producto = db.query(models.Producto).filter(models.Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.activo = False  # Marcamos el producto como inactivo en lugar de eliminarlo físicamente
    db.commit()
    return producto
