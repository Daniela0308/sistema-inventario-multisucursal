from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import producto, sucursal, usuario , auth, inventario, proveedor

#Creamos la instancia de FastAPI
app = FastAPI(title="Sistema de Inventario Multi-Sucursal")

# CORS: permite que el frontend (en otro puerto/origen) pueda llamar a
# esta API desde el navegador. Sin esto, el navegador bloquea la
# peticion por seguridad, aunque el backend funcione perfectamente.
# allow_origins=["*"] es permisivo (cualquier origen puede llamar) --
# aceptable para esta prueba tecnica; en produccion real se restringiria
# a la URL exacta del frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"mensaje": "¡API de Inventario OptiPlant funcionando correctamente!"}

# Registramos el router de productos
app.include_router(producto.router)
app.include_router(sucursal.router)
app.include_router(usuario.router)
app.include_router(auth.router)
app.include_router(inventario.router)
app.include_router(proveedor.router)