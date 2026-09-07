"""compra.py - Lógica de negocio relacionada con las compras."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from services.inventario_service import registrar_movimiento  # reutilizamos la función que ya existe


def crear_orden_compra(db: Session, datos: schemas.OrdenCompraCreate, usuario_id: int):
    """
    Crea una orden de compra en estado BORRADOR junto con todos sus
    detalles. Crear la orden NO modifica todavía el inventario.
    """
    # Validaciones iniciales
    proveedor = db.query(models.Proveedor).filter(models.Proveedor.id == datos.proveedor_id).first()
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == datos.sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    if not datos.detalles:
        raise HTTPException(status_code=400, detail="La orden de compra debe tener al menos un detalle")

    # Crear la orden de compra en estado BORRADOR
    nueva_orden = models.OrdenCompra(
        proveedor_id=datos.proveedor_id,
        sucursal_id=datos.sucursal_id,
        usuario_id=usuario_id,
        estado=models.EstadoOrdenCompra.BORRADOR,
        plazo_pago_dias=datos.plazo_pago_dias,
    )

    # Agregar los detalles a la orden de compra
    for detalle in datos.detalles:
        # Validar cada detalle antes de agregarlo a la orden
        if detalle.cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad del producto debe ser mayor a cero")
        if detalle.precio_unitario <= 0:
            raise HTTPException(status_code=400, detail="El precio unitario del producto debe ser mayor a cero")
        if detalle.descuento_pct < 0 or detalle.descuento_pct > 100:
            raise HTTPException(status_code=400, detail="El descuento debe estar entre 0 y 100")

        producto = db.query(models.Producto).filter(models.Producto.id == detalle.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto con ID {detalle.producto_id} no encontrado")
        # Agregar el detalle validado a la orden de compra
        nueva_orden.detalles.append(models.DetalleCompra(
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=detalle.precio_unitario,
            descuento_pct=detalle.descuento_pct,
        ))
    # Guardar la orden de compra en la base de datos
    db.add(nueva_orden)
    db.flush()  # asigna el id de la orden sin cerrar la transacción todavía
    return nueva_orden


def confirmar_orden_compra(db: Session, orden_id: int):
    """Cambia una orden de BORRADOR a CONFIRMADA. Todavía NO toca el inventario."""
    # Buscar la orden de compra por ID
    orden = db.query(models.OrdenCompra).filter(models.OrdenCompra.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    if orden.estado == models.EstadoOrdenCompra.CANCELADA:
        raise HTTPException(status_code=400, detail="No se puede confirmar una orden cancelada")
    if orden.estado == models.EstadoOrdenCompra.CONFIRMADA:
        raise HTTPException(status_code=400, detail="La orden de compra ya está confirmada")
    if not orden.detalles:
        raise HTTPException(status_code=400, detail="La orden de compra no tiene detalles")

    # Cambiar el estado de la orden a CONFIRMADA
    orden.estado = models.EstadoOrdenCompra.CONFIRMADA
    db.flush()
    return orden


def recibir_compra(db: Session, orden_id: int, usuario_id: int):
    """
    Registra la recepción de una orden CONFIRMADA:
    - aumenta el inventario de la sucursal,
    - registra un movimiento INGRESO_COMPRA por cada línea,
    - recalcula el costo promedio (todo esto lo hace registrar_movimiento,
      no lo repetimos aquí).
    """
    # validar que la orden exista y esté en estado CONFIRMADA antes de procesar la recepción
    orden = db.query(models.OrdenCompra).filter(models.OrdenCompra.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")
    if orden.estado != models.EstadoOrdenCompra.CONFIRMADA:
        raise HTTPException(status_code=400, detail="Solo se pueden recibir órdenes confirmadas")
    if not orden.detalles:
        raise HTTPException(status_code=400, detail="La orden de compra no tiene detalles")

    # Procesar cada detalle de la orden de compra
    for detalle in orden.detalles:
        # El costo neto ya considera el descuento de esta línea, para
        # que el costo promedio del inventario refleje lo que REALMENTE
        # se pagó por unidad, no el precio de lista.
        costo_neto = detalle.precio_unitario * (1 - detalle.descuento_pct / 100)

        registrar_movimiento(
            db,
            producto_id=detalle.producto_id,
            sucursal_id=orden.sucursal_id,
            tipo=models.TipoMovimiento.INGRESO_COMPRA,
            cantidad=detalle.cantidad,
            usuario_id=usuario_id,
            motivo="Recepción de compra",
            referencia=f"orden_compra:{orden.id}",
            costo_unitario=costo_neto,
        )

    # Guardar los cambios en la base de datos
    db.flush()
    return orden