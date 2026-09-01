"""
test.py
=======
Archivo de PRUEBAS, no de produccion. Sirve para experimentar con la BD
sin tener que escribir todo de nuevo cada vez en la consola interactiva
(que borra el historial al cerrarla).

Como correrlo (con los contenedores ya levantados):

    docker exec -it optiplant_backend python test.py

Cada vez que quieras probar algo nuevo, edita este archivo, guarda, y
vuelve a correr el comando de arriba. Si es la PRIMERA vez que agregas
este archivo, necesitas reconstruir la imagen primero para que exista
dentro del contenedor:

    docker compose up --build -d
    docker exec -it optiplant_backend python test.py
"""

from database import SessionLocal
from models import Producto

# Abrimos una sesion manual (fuera de FastAPI, por eso no usamos get_db()
# con su Depends() -- eso es exclusivo del mundo de los endpoints).
db = SessionLocal()

# ---------------------------------------------------------------------
# PRUEBA 1: crear un producto desde Python
# ---------------------------------------------------------------------
nuevo = Producto(sku="TEST-003", nombre="Otro producto de prueba", precio_venta=1500)
db.add(nuevo)
db.commit()
print(f"Producto creado con id={nuevo.id}")

""" # ---------------------------------------------------------------------
# PRUEBA 2: leer TODOS los productos (los que creaste desde Python Y
# los que crees manualmente desde pgAdmin apareceran aqui tambien)
# ---------------------------------------------------------------------
print("\n--- Todos los productos en la BD ---")
productos = db.query(Producto).all()
for p in productos:
    print(f"id={p.id}  sku={p.sku}  nombre={p.nombre}  precio={p.precio_venta}")

# ---------------------------------------------------------------------
# PRUEBA 3: buscar UN producto por su id (ejemplo de filtro)
# ---------------------------------------------------------------------
primero = db.query(Producto).filter(Producto.id == 1).first()
if primero:
    print(f"\nEl producto con id=1 es: {primero.nombre}")
else:
    print("\nNo hay producto con id=1")

# Siempre cerrar la sesion al terminar (aqui lo hacemos manual porque no
# estamos dentro de un endpoint de FastAPI con su try/finally automatico).
db.close() """