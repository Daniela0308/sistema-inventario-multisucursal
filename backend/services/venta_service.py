"""venta.py - Lógica de negocio relacionada con las ventas."""

from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from services.inventario_service import registrar_movimiento


def crear_venta(db: Session, datos: schemas.VentaCreate, usuario_id: int):
    """
    Crea una venta y descuenta el stock DE INMEDIATO (a diferencia de
    Compras, aquí no hay paso de "confirmar" separado -- una venta
    implica que el cliente ya se llevó el producto en el momento).
    """

    # Validar que la sucursal exista antes de continuar.
    sucursal = db.query(models.Sucursal).filter(models.Sucursal.id == datos.sucursal_id).first()
    if not sucursal:
        raise HTTPException(status_code=404, detail="Sucursal no encontrada")

    if not datos.detalles:
        raise HTTPException(status_code=400, detail="La venta debe tener al menos un producto")

    # PASO 1: validar que haya stock suficiente para TODAS las líneas
    # ANTES de mover nada (requisito 3.3: "validar disponibilidad de
    # stock antes de confirmar la venta"). Si una línea falla, ninguna
    # se procesa -- evita dejar una venta a medias.
    for detalle in datos.detalles:
        if detalle.cantidad <= 0:
            raise HTTPException(status_code=400, detail="La cantidad debe ser mayor a cero")
        # Validar que la cantidad solicitada sea positiva.
        inventario = db.query(models.Inventario).filter(
            models.Inventario.sucursal_id == datos.sucursal_id,
            models.Inventario.producto_id == detalle.producto_id,
        ).first()
        # Determinar la cantidad disponible en inventario. Si no hay registro, se asume 0.
        disponible = inventario.cantidad if inventario else 0
        # Comparar la cantidad disponible con la solicitada. Si no hay suficiente, se lanza excepción.
        if disponible < detalle.cantidad:
            producto = db.query(models.Producto).filter(models.Producto.id == detalle.producto_id).first()
            nombre = producto.nombre if producto else detalle.producto_id
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{nombre}': disponible {disponible}, solicitado {detalle.cantidad}",
            )

    # PASO 2: crear la venta y calcular el total, resolviendo el precio
    # de cada línea con el del catálogo.
    nueva_venta = models.Venta(sucursal_id=datos.sucursal_id, usuario_id=usuario_id, total=Decimal("0"))
    total = Decimal("0")

    # Iterar sobre cada línea de detalle para calcular subtotales y total de la venta.
    for detalle in datos.detalles:
        producto = db.query(models.Producto).filter(models.Producto.id == detalle.producto_id).first()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto no encontrado")

        # Calcular el subtotal de la línea usando el precio de venta del producto y el descuento.
        subtotal = producto.precio_venta * detalle.cantidad * (1 - detalle.descuento_pct / 100)
        total += subtotal

        nueva_venta.detalles_venta.append(models.DetalleVenta(
            producto_id=detalle.producto_id,
            cantidad=detalle.cantidad,
            precio_unitario=producto.precio_venta,
            descuento_pct=detalle.descuento_pct,
        ))
    # Fin del cálculo de subtotales y total de la venta.
    nueva_venta.total = total
    db.add(nueva_venta)
    db.flush()  # asigna el id de la venta antes de registrar los movimientos

    # PASO 3: descontar el stock de cada línea (esto también dispara,
    # dentro de registrar_movimiento, la validación de stock negativo
    # como segunda barrera de seguridad, y más adelante las alertas).
    for detalle in datos.detalles:
        registrar_movimiento(
            db,
            producto_id=detalle.producto_id,
            sucursal_id=datos.sucursal_id,
            tipo=models.TipoMovimiento.RETIRO_VENTA,
            cantidad=detalle.cantidad,
            usuario_id=usuario_id,
            motivo="Venta",
            referencia=f"venta:{nueva_venta.id}",
        )

    db.flush()
    return nueva_venta