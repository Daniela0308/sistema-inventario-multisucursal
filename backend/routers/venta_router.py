from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
import auth
from database import get_db
from services import venta_service as venta

router = APIRouter(prefix="/ventas", tags=["ventas"])

# Endpoint para crear una venta
@router.post("", response_model=schemas.VentaOut, status_code=201)
def crear(
    datos: schemas.VentaCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user),
):
    """Crea una nueva venta."""

    # REGLA DE NEGOCIO EN EL BACKEND, no en el frontend: si el usuario
    # NO es admin_general, se IGNORA por completo lo que haya mandado
    # en datos.sucursal_id, y se fuerza a su propia sucursal -- sin
    # importar si el cliente intentó mandar otra cosa.
    if usuario_actual.rol == models.RolUsuario.ADMIN_GENERAL:
        if not datos.sucursal_id:
            raise HTTPException(400, "El administrador debe especificar la sucursal")
        sucursal_id = datos.sucursal_id
    else:
        if not usuario_actual.sucursal_id:
            raise HTTPException(400, "Tu usuario no tiene una sucursal asignada")
        sucursal_id = usuario_actual.sucursal_id  # se ignora datos.sucursal_id por completo

    # Reconstruimos "datos" con la sucursal ya resuelta y validada, antes
    # de pasarlo al servicio -- así crear_venta nunca necesita saber de
    # dónde vino ese id, solo confía en que ya es el correcto.
    datos.sucursal_id = sucursal_id
    # Ahora "datos" tiene la sucursal correcta, y podemos pasar todo al servicio de ventas.
    nueva_venta = venta.crear_venta(db, datos, usuario_actual.id)
    db.commit()
    db.refresh(nueva_venta)
    return nueva_venta


# Endpoint para listar todas las ventas
@router.get("", response_model=List[schemas.VentaOut])
def listar(db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(auth.get_current_user)):
    """Lista las ventas. Admin ve todas; gerente/operador solo las de su sucursal."""
    query = db.query(models.Venta)
    if usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL:
        query = query.filter(models.Venta.sucursal_id == usuario_actual.sucursal_id)
    return query.order_by(models.Venta.fecha_registro.desc()).all()


# Endpoint para obtener una venta por su ID
@router.get("/{venta_id}", response_model=schemas.VentaOut)
def obtener(venta_id: int, db: Session = Depends(get_db), usuario_actual: models.Usuario = Depends(auth.get_current_user)):
    """Obtiene una venta por su ID."""
    venta_obj = db.query(models.Venta).filter(models.Venta.id == venta_id).first()
    if not venta_obj:
        raise HTTPException(404, "Venta no encontrada")
    if usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL and venta_obj.sucursal_id != usuario_actual.sucursal_id:
        raise HTTPException(403, "No puedes consultar ventas de otra sucursal")
    return venta_obj