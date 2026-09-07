"""Lógica de negocio para transferencias entre sucursales."""

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from services.inventario_service import registrar_movimiento


def crear_transferencia(
    db: Session,
    datos: schemas.TransferenciaCreate,
    usuario_id: int,
):
    """Crea una solicitud sin modificar todavía el inventario."""
    # Validar que la sucursal de origen y destino sean diferentes
    if datos.sucursal_origen_id == datos.sucursal_destino_id:
        raise HTTPException(
            status_code=400,
            detail="La sucursal de origen y destino deben ser diferentes",
        )
    # Validar que el producto exista
    producto = (
        db.query(models.Producto)
        .filter(models.Producto.id == datos.producto_id)
        .first()
    )
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    # Validar que la sucursal de origen exista
    sucursal_origen = (
        db.query(models.Sucursal)
        .filter(models.Sucursal.id == datos.sucursal_origen_id)
        .first()
    )
    if not sucursal_origen:
        raise HTTPException(status_code=404, detail="Sucursal de origen no encontrada")

    sucursal_destino = (
        db.query(models.Sucursal)
        .filter(models.Sucursal.id == datos.sucursal_destino_id)
        .first()
    )
    if not sucursal_destino:
        raise HTTPException(status_code=404, detail="Sucursal de destino no encontrada")
    # crear la transferencia en la base de datos
    transferencia = models.Transferencia(
        producto_id=datos.producto_id,
        sucursal_origen_id=datos.sucursal_origen_id,
        sucursal_destino_id=datos.sucursal_destino_id,
        cantidad_solicitada=datos.cantidad_solicitada,
        urgencia=datos.urgencia,
        usuario_solicita_id=usuario_id,
        observaciones=datos.observaciones,
        estado=models.EstadoTransferencia.SOLICITADA,
    )
    db.add(transferencia)
    db.flush()
    db.refresh(transferencia)
    return transferencia
