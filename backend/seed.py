"""
seed.py
=======
Borra la base de datos por completo y crea un set de datos de prueba consistente.
Es seguro correrlo varias veces: reinicia los contadores (IDs arrancan en 1).

Cómo correrlo (con los contenedores levantados):
    docker exec -it optiplant_backend python seed.py
"""
import auth
from database import SessionLocal
from models import Producto, Sucursal, Usuario, RolUsuario, Proveedor

db = SessionLocal()

""" 
# -------------------------------------------------------------------------
# 1. CREACIÓN DE SUCURSALES Y PROVEEDORES
# -------------------------------------------------------------------------
print(" Creando sucursales de prueba...")
central = Sucursal(
    nombre="Sucursal Central", ciudad="Bogotá", direccion="Cra 7 # 45-10"
)
norte = Sucursal(
    nombre="Sucursal Norte", ciudad="Medellín", direccion="Cl 10 # 30-20"
)


db.add_all([central, norte])
db.commit()
# Hacemos refresh para obtener los IDs generados (1 y 2)
db.refresh(central)
db.refresh(norte)

print(" Creando proveedores de prueba...")
proveedores = [
    Proveedor(
        nombre="Proveedor A",
        email="proveedorA@optiplant.com",
        telefono="1234567890",
    ),
    Proveedor(
        nombre="Proveedor B",
        email="proveedorB@optiplant.com",
        telefono="0987654321",
    ),
]
db.add_all(proveedores)
db.commit()
# -------------------------------------------------------------------------
# 2. CREACIÓN DE PRODUCTOS
# -------------------------------------------------------------------------
print("Creando productos de prueba...")
productos = [
    Producto(
        sku="TORN-001",
        nombre="Tornillo hexagonal 1/2 pulg",
        unidad_medida="unidad",
        stock_minimo=50,
        precio_venta=500,
    ),
    Producto(
        sku="PINT-010",
        nombre="Pintura acrílica blanca 1gal",
        unidad_medida="galón",
        stock_minimo=10,
        precio_venta=85000,
    ),
    Producto(
        sku="CABL-020",
        nombre="Cable eléctrico #12 (rollo 100m)",
        unidad_medida="rollo",
        stock_minimo=5,
        precio_venta=210000,
    ),
    Producto(
        sku="GUAN-005",
        nombre="Guantes de seguridad",
        unidad_medida="par",
        stock_minimo=20,
        precio_venta=12000,
    ),
]

db.add_all(productos)
db.commit() """

# -------------------------------------------------------------------------
# 3. CREACIÓN DE USUARIOS
# -------------------------------------------------------------------------
#print("Borrando usuarios existentes...")
#db.query(Usuario).delete()


print("Creando usuarios de prueba...")
usuarios = [
    Usuario(
        nombre="Admin General",
        email="admin@optiplant.com",
        password_hash=auth.hash_password("Admin123!"),
        rol=RolUsuario.ADMIN_GENERAL,
        sucursal_id=None,  # el admin no pertenece a ninguna sucursal especifica
    ),
    Usuario(
        nombre="Gerente Central",
        email="gerente@optiplant.com",
        password_hash=auth.hash_password("Gerente123!"),
        rol=RolUsuario.GERENTE_SUCURSAL,
        sucursal_id= db.query(Sucursal).filter(Sucursal.nombre == "Sucursal Central").first().id,  # reutiliza la variable "central" que ya creaste arriba
    ),
    Usuario(
        nombre="Operador Central",
        email="operador@optiplant.com",
        password_hash=auth.hash_password("Operador123!"),
        rol=RolUsuario.OPERADOR_INVENTARIO,
        sucursal_id= db.query(Sucursal).filter(Sucursal.nombre == "Sucursal Central").first().id,
    ),
]
db.add_all(usuarios)
db.commit()

print("\nUsuarios de prueba creados:")
print("  admin@optiplant.com     / Admin123!     (ADMIN_GENERAL)")
print("  gerente@optiplant.com   / Gerente123!    (GERENTE_SUCURSAL - Central)")
print("  operador@optiplant.com  / Operador123!   (OPERADOR_INVENTARIO - Central)")



db.close()