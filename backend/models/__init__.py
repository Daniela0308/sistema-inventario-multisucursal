"""
models/__init__.py
===================
Re-exporta TODAS las clases para que el resto del proyecto siga haciendo
"import models" y "models.Producto" exactamente igual que antes, sin
tener que tocar routers/ ni services/.
"""
from .sucursal import Sucursal
from .usuario import Usuario, RolUsuario
from .producto import Producto
from .inventario import Inventario, MovimientoInventario, TipoMovimiento
from .proveedor import Proveedor
from .compra import OrdenCompra, DetalleCompra, EstadoOrdenCompra
from .venta import Venta, DetalleVenta
from .transferencia import Transferencia, EstadoTransferencia, UrgenciaTransferencia

__all__ = [
    "Sucursal",
    "Usuario", "RolUsuario",
    "Producto",
    "Inventario", "MovimientoInventario", "TipoMovimiento",
    "Proveedor",
    "OrdenCompra", "DetalleCompra", "EstadoOrdenCompra",
    "Venta", "DetalleVenta",
    "Transferencia", "EstadoTransferencia", "UrgenciaTransferencia",
]
