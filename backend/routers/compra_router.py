import schemas
import models
import auth

from services import compra_service as compra

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db

router = APIRouter(prefix="/compras", tags=["compras"])


# Endpoint para crear una orden de compra
@router.post("", response_model=schemas.OrdenCompraOut, status_code=201)
def crear(
    datos: schemas.OrdenCompraCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
):
    """Crea una nueva orden de compra en estado BORRADOR."""
    # Igual que en ventas: si NO es admin_general, se ignora datos.sucursal_id
    # y se fuerza la sucursal del usuario autenticado.
    if usuario_actual.rol == models.RolUsuario.ADMIN_GENERAL:
        if not datos.sucursal_id:
            raise HTTPException(400, "El administrador debe especificar la sucursal")
        sucursal_id = datos.sucursal_id
    else:
        if not usuario_actual.sucursal_id:
            raise HTTPException(400, "Tu usuario no tiene una sucursal asignada")
        sucursal_id = usuario_actual.sucursal_id  # se ignora datos.sucursal_id por completo

    datos.sucursal_id = sucursal_id
    orden = compra.crear_orden_compra(db, datos, usuario_actual.id)
    db.commit()
    db.refresh(orden)
    return orden


# Endpoint para confirmar una orden de compra
@router.post("/{orden_id}/confirmar", response_model=schemas.OrdenCompraOut)
def confirmar(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL, models.RolUsuario.GERENTE_SUCURSAL)),
):
    """Confirma una orden de compra que está en estado BORRADOR."""
    # El gerente de sucursal solo supervisa SU sucursal (no puede confirmar
    # ordenes de otras). El admin_general no tiene esta restriccion.
    if usuario_actual.rol == models.RolUsuario.GERENTE_SUCURSAL:
        orden_existente = db.query(models.OrdenCompra).filter(models.OrdenCompra.id == orden_id).first()
        if not orden_existente:
            raise HTTPException(404, "Orden de compra no encontrada")
        if orden_existente.sucursal_id != usuario_actual.sucursal_id:
            raise HTTPException(403, "No puedes confirmar órdenes de otra sucursal")

    orden = compra.confirmar_orden_compra(db, orden_id)
    db.commit()
    db.refresh(orden)
    return orden


# Endpoint para recibir una orden de compra
@router.post("/{orden_id}/recibir", response_model=schemas.OrdenCompraOut)
def recibir(
    orden_id: int,
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL, models.RolUsuario.GERENTE_SUCURSAL)),
):
    """Registra la recepción de una orden de compra que está en estado CONFIRMADA."""
    # Misma regla que en confirmar: el gerente solo recibe ordenes de SU sucursal.
    if usuario_actual.rol == models.RolUsuario.GERENTE_SUCURSAL:
        orden_existente = db.query(models.OrdenCompra).filter(models.OrdenCompra.id == orden_id).first()
        if not orden_existente:
            raise HTTPException(404, "Orden de compra no encontrada")
        if orden_existente.sucursal_id != usuario_actual.sucursal_id:
            raise HTTPException(403, "No puedes recibir órdenes de otra sucursal")

    orden = compra.recibir_compra(db, orden_id, usuario_actual.id)
    db.commit()
    db.refresh(orden)
    return orden


# Endpoint para listar todas las órdenes de compra
@router.get("", response_model=List[schemas.OrdenCompraOut])
def listar(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(auth.get_current_user)):
    """Lista las órdenes de compra. Admin ve todas; gerente/operador solo las de su sucursal."""
    query = db.query(models.OrdenCompra)
    if usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL:
        query = query.filter(models.OrdenCompra.sucursal_id == usuario_actual.sucursal_id)
    return query.order_by(models.OrdenCompra.fecha_registro.desc()).all()


# Endpoint para obtener una orden de compra por su ID
@router.get("/{orden_id}", response_model=schemas.OrdenCompraOut)
def obtener(orden_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(auth.get_current_user)):
    """Obtiene una orden de compra por su ID."""
    orden = db.query(models.OrdenCompra).filter(models.OrdenCompra.id == orden_id).first()
    if not orden:
        raise HTTPException(404, "Orden de compra no encontrada")
    if usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL and orden.sucursal_id != usuario_actual.sucursal_id:
        raise HTTPException(403, "No puedes consultar órdenes de otra sucursal")
    return orden