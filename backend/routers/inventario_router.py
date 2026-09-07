import schemas
import models
import auth

from services import inventario_service as inventario

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db

router = APIRouter(prefix="/inventarios", tags=["inventarios"])


# Endpoint para registrar un movimiento de inventario
@router.post("/movimientos", response_model=schemas.MovimientoOut, status_code=201)
def registrar_movimiento_endpoint(
    datos: schemas.MovimientoCreate,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):
    """
    Registra un movimiento de inventario (ingreso o retiro) y actualiza el stock.
    """
    # Igual que en ventas/compras: si NO es admin_general, se ignora
    # datos.sucursal_id y se fuerza la sucursal del usuario autenticado.
    if usuario_actual.rol == models.RolUsuario.ADMIN_GENERAL:
        if not datos.sucursal_id:
            raise HTTPException(400, "El administrador debe especificar la sucursal")
        sucursal_id = datos.sucursal_id
    else:
        # Para usuarios que no son ADMIN_GENERAL, se fuerza la sucursal del usuario autenticado.
        if not usuario_actual.sucursal_id:
            raise HTTPException(400, "Tu usuario no tiene una sucursal asignada")
        sucursal_id = usuario_actual.sucursal_id  # se ignora datos.sucursal_id por completo

    # Llamamos a la función de servicio para registrar el movimiento
    movimiento = inventario.registrar_movimiento(
        db,
        producto_id=datos.producto_id,
        sucursal_id=sucursal_id,
        tipo=datos.tipo,
        cantidad=datos.cantidad,
        usuario_id=usuario_actual.id,
        motivo=datos.motivo,
        referencia=datos.referencia
    )
    db.commit()  # Confirmamos los cambios en la base de datos
    db.refresh(movimiento)  # Refrescamos el objeto para obtener los datos actualizados
    return movimiento


# Endpoint para registrar movimiento directamente en la sucursal del usuario logueado
@router.post("/movimientos/mi-sucursal", response_model=schemas.MovimientoOut, status_code=201)
def registrar_movimiento_mi_sucursal_endpoint(
    datos: schemas.MovimientoCreateSinSucursal,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):
    """ Registra un movimiento de inventario directamente en la sucursal del usuario logueado. 
    Si el usuario no tiene una sucursal asignada y no es ADMIN_GENERAL, se lanza una excepción HTTP 400.
    """

    sucursal_id = usuario_actual.sucursal_id
    if not sucursal_id and usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL:
        raise HTTPException(
            400, f"El usuario no tiene una sucursal asignada."
        )
    movimiento = inventario.registrar_movimiento(
        db,
        producto_id=datos.producto_id,
        sucursal_id=sucursal_id,
        tipo=datos.tipo,
        cantidad=datos.cantidad,
        usuario_id=usuario_actual.id,
        motivo=datos.motivo,
        referencia=datos.referencia
    )
    db.commit()
    db.refresh(movimiento)
    return movimiento


# Endpoint para ajustar el stock de una sucursal
@router.post("/movimientos/ajustar-stock", response_model=schemas.MovimientoOut, status_code=201)
def ajustar_inventario_sucursal_endpoint(
    datos: schemas.AjusteInventarioSchema,
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):
    """
    Realiza un ajuste de inventario por conteo físico real.
    - ADMIN_GENERAL: Puede especificar cualquier sucursal_id.
    - OTROS ROLES: Solo pueden ajustar la sucursal a la que están asignados.
    """
    # Resolver la sucursal del usuario
    if usuario_actual.rol == models.RolUsuario.ADMIN_GENERAL:
        # Si el usuario es ADMIN_GENERAL, se toma la sucursal_id del payload
        if not datos.sucursal_id:
            raise HTTPException(
                400, f"Se debe especificar la sucursal para el ajuste."
            )
        sucursal_id = datos.sucursal_id
    else:
        # Para otros roles, se toma la sucursal del usuario
        sucursal_id = usuario_actual.sucursal_id
        if not sucursal_id:
            raise HTTPException(
                400, f"El usuario no tiene una sucursal asignada."
            )
    if not sucursal_id:
        raise HTTPException(
            400, f"No se pudo determinar la sucursal para el ajuste."
        )

    # Delegar toda la regla de negocio al servicio
    ajuste = inventario.ajustar_inventario_sucursal(
        db=db,
        sucursal_id=sucursal_id,
        usuario_id=usuario_actual.id,
        producto_id=datos.producto_id,
        cantidad_real=datos.cantidad_real,
        motivo=datos.motivo
    )

    db.commit()
    return ajuste


# Endpoint para listar el inventario de la sucursal del usuario actual
@router.get("/mi-sucursal", response_model=List[schemas.InventarioOut])
def obtener_inventario_mi_sucursal(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):
    """ Retorna el inventario de la sucursal del usuario logueado.

    Si el usuario no tiene una sucursal asignada y no es ADMIN_GENERAL, se lanza una excepción HTTP 400.
    """
    # Para usuarios que no son ADMIN_GENERAL, se fuerza la sucursal del usuario autenticado.
    sucursal_id = usuario_actual.sucursal_id
    # Validar que el usuario tenga una sucursal asignada si no es ADMIN_GENERAL
    if not sucursal_id and usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL:
        raise HTTPException(
            400, f"El usuario no tiene una sucursal asignada."
        )
    inventario = (
        db.query(models.Inventario)
        .filter(models.Inventario.sucursal_id == sucursal_id)
        .all()
    )
    return inventario


# Endpoint para listar todos los movimientos de inventario
@router.get("/movimientos", response_model=List[schemas.MovimientoOut])
def listar_movimientos(
    db: Session = Depends(get_db),
    usuario_actual = Depends(auth.requerir_roles(models.RolUsuario.ADMIN_GENERAL)),
):
    """ Retorna los movimientos de inventario. Exclusivo del admin_general: gerentes y operadores NO tienen acceso al historial de movimientos."""
    query = db.query(models.MovimientoInventario)
    return query.order_by(models.MovimientoInventario.fecha_registro.desc()).all()


# Endpoint para alertar sobre stock bajo
@router.get("/alerta-stock-bajo", response_model=List[schemas.InventarioOut])
def alerta_stock_bajo_endpoint(
    db: Session = Depends(get_db),
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):
    """ Retorna los productos cuyo stock en la sucursal del usuario logueado está por debajo del umbral definido. """
    sucursal_id = usuario_actual.sucursal_id
    if not sucursal_id and usuario_actual.rol != models.RolUsuario.ADMIN_GENERAL:
        raise HTTPException(
            400, f"El usuario no tiene una sucursal asignada."
        )

    productos_bajo_stock = inventario.alerta_stock_bajo(db=db, sucursal_id=sucursal_id)
    return productos_bajo_stock


# Endpoint para obtener el inventario de una sucursal específica
@router.get("/{sucursal_id}", response_model=List[schemas.InventarioOut])
def obtener_inventario(
    sucursal_id: int, 
    db: Session = Depends(get_db), 
    usuario_actual: models.Usuario = Depends(auth.get_current_user)
):

    """Retorna el inventario (stock) de una sucursal específica."""
    # Cualquier rol puede consultar el stock de CUALQUIER sucursal; lo
    # restringido a solo admin_general es el historial de movimientos,
    # no el inventario en sí.
    inventario = (
        db.query(models.Inventario)
        .filter(models.Inventario.sucursal_id == sucursal_id)
        .all()
    )
    return inventario


