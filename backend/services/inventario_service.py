""" inventario.py - Logica de negocio relacionada con el inventario."""

from fastapi import HTTPException
from sqlalchemy.orm import Session

from decimal import Decimal
import models


# Tipos de movimiento que representan ingreso o retiro de stock. Se usan
# para validar que el movimiento sea correcto y para sumar/restar stock.
TIPOS_INGRESO = {
    models.TipoMovimiento.INGRESO_COMPRA,
    models.TipoMovimiento.INGRESO_DEVOLUCION,
    models.TipoMovimiento.INGRESO_AJUSTE,
    models.TipoMovimiento.INGRESO_TRANSFERENCIA,
}
TIPOS_RETIRO = {
    models.TipoMovimiento.RETIRO_VENTA,
    models.TipoMovimiento.RETIRO_MERMA,
    models.TipoMovimiento.RETIRO_AJUSTE,
    models.TipoMovimiento.RETIRO_TRANSFERENCIA,
}

# Unico punto de entrada para registrar un movimiento de inventario y
# actualizar el stock del inventario. Se llama desde varios routers:
def registrar_movimiento(
    db: Session,
    *,
    producto_id: int,
    sucursal_id: int,
    tipo: models.TipoMovimiento,
    cantidad: int,
    usuario_id: int,
    motivo: str | None = None,
    referencia: str | None = None,
    costo_unitario: Decimal | None = None,
) -> models.MovimientoInventario: #Es una indicación de qué tipo de objeto debería devolver la función.
    """
    UNICO punto de entrada para cambiar stock en todo el sistema.
    Quien la llama: Inventario (ajustes manuales), Compras (al confirmar
    recepcion), Ventas (al confirmar la venta), Transferencias (al
    despachar y al recibir).
    """
    # Validaciones de negocio
    if cantidad <= 0:
        raise HTTPException(400, "La cantidad debe ser mayor a cero")

    inventario = (
        db.query(models.Inventario)
        .filter(
            models.Inventario.producto_id == producto_id,
            models.Inventario.sucursal_id == sucursal_id,
        )
        .first() # Obtiene el primer registro que cumpla con los filtros, o None si no existe.
    )
    if inventario is None:
        # Si no existe un registro de inventario para este producto y sucursal, lo creamos con cantidad 0.
        inventario = models.Inventario(producto_id=producto_id, sucursal_id=sucursal_id, cantidad=0)
        db.add(inventario)
        db.flush()

    # Actualizamos el stock del inventario según el tipo de movimiento
    if tipo in TIPOS_INGRESO:
        # Solo recalculamos el costo promedio si quien llama a esta
        # función SI conoce el precio de esta entrada (típicamente,
        # una compra). En una devolución/ajuste/transferencia, se manda
        # costo_unitario=None y el costo_promedio no se toca.
        if costo_unitario is not None:
            valor_actual = inventario.cantidad * inventario.costo_promedio
            valor_entrante = cantidad * costo_unitario
            nueva_cantidad_total = inventario.cantidad + cantidad
            inventario.costo_promedio = (valor_actual + valor_entrante) / nueva_cantidad_total

        inventario.cantidad += cantidad

    elif tipo in TIPOS_RETIRO:
        if inventario.cantidad < cantidad:
            raise HTTPException(
                400, f"Stock insuficiente: disponible {inventario.cantidad}, solicitado {cantidad}"
            )
        inventario.cantidad -= cantidad
    else:
        raise HTTPException(400, "Tipo de movimiento inválido")

    movimiento = models.MovimientoInventario(
        producto_id=producto_id,
        sucursal_id=sucursal_id,
        tipo=tipo,
        cantidad=cantidad,  # Calcula el valor total del movimiento
        motivo=motivo,
        referencia=referencia,
        usuario_id=usuario_id,
    )
    db.add(movimiento)
    db.flush() # permite que SQLAlchemy sincronice ese objeto con PostgreSQL dentro de la transacción actual.
    return movimiento


# Función para ajustar el inventario de un producto en una sucursal específica.
def ajustar_inventario_sucursal(
        db: Session, 
        sucursal_id: int, 
        usuario_id: int, 
        producto_id: int, 
        cantidad_real: int, 
        motivo: str
    ):
        """ Ajusta el inventario de un producto en una sucursal específica. """
        # 1. Obtener item de inventario
        item_inventario = db.query(models.Inventario).filter(
            models.Inventario.sucursal_id == sucursal_id,
            models.Inventario.producto_id == producto_id
        ).first()

        if not item_inventario:
            raise HTTPException(
                400, f"El producto no existe en el inventario de esta sucursal."
            )

        # 2. Calcular la diferencia
        cantidad_actual = item_inventario.cantidad
        diferencia = cantidad_real - cantidad_actual

        if diferencia == 0:
            raise HTTPException(
                400,
                f"La cantidad ingresada es igual a la cantidad actual en stock."
            )

        # 3. Determinar tipo de movimiento
        tipo_movimiento = "ingreso_ajuste" if diferencia > 0 else "retiro_ajuste"

        # 4. Actualizar stock
        item_inventario.cantidad = cantidad_real

        # 5. Registrar trazabilidad
        nuevo_movimiento = models.MovimientoInventario(
            sucursal_id=sucursal_id,
            producto_id=producto_id,
            usuario_id=usuario_id,
            tipo=tipo_movimiento,
            cantidad=abs(diferencia),
            motivo=f"[AJUSTE MANUAL] {motivo} (Anterior: {cantidad_actual} -> Nuevo: {cantidad_real})"
        )

        db.add(nuevo_movimiento)
        db.flush() # permite que SQLAlchemy sincronice ese objeto con PostgreSQL dentro de la transacción actual.
        db.refresh(item_inventario)

        return {
            "mensaje": "Stock ajustado correctamente.",
            "cantidad_anterior": cantidad_actual,
            "cantidad_nueva": item_inventario.cantidad,
            "diferencia_aplicada": diferencia
        }


# Función alerta de stock bajo
def alerta_stock_bajo(
        db: Session,
        sucursal_id: int,   
    ):
    """
    Retorna una lista de productos cuyo stock en la sucursal especificada
    está por debajo del umbral indicado.
    """
    # Consulta los registros de inventario cruzados con el modelo Producto
    query = (
        db.query(models.Inventario)
        .join(models.Producto, models.Inventario.producto_id == models.Producto.id)
        # Filtra donde la cantidad en stock sea menor o igual al stock_minimo del producto
        .filter(models.Inventario.cantidad <= models.Producto.stock_minimo)
    )

    # Si se pasa un sucursal_id, se filtra por esa sucursal
    if sucursal_id:
        query = query.filter(models.Inventario.sucursal_id == sucursal_id)

    return query.all()