from fastapi import FastAPI

from routers import productos

#Creamos la instancia de FastAPI
app = FastAPI(title="Sistema de Inventario Multi-Sucursal")

@app.get("/")
def home():
    return {"mensaje": "¡API de Inventario OptiPlant funcionando correctamente!"}

# Registramos el router de productos
app.include_router(productos.router)
