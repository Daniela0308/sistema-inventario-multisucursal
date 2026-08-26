from fastapi import FastAPI

app = FastAPI(title="Sistema de Inventario Multi-Sucursal")

@app.get("/")
def home():
    return {"mensaje": "¡API de Inventario OptiPlant funcionando correctamente!"}