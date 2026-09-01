from typing import List
from fastapi import APIRouter, Depends, HTTPException
#la variable db va a ser un objeto de tipo Session
from sqlalchemy.orm import Session

# Importamos la funcion get_db() que nos da una sesion de SQLAlchemy 
# y la clase que mapea la tabla "cualquiera" de la BD
from database import get_db
from models import Producto
from schemas import ProductoOut, ProductoCreate, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["productos"])

# Endpoint para obtener todos los productos
@router.get("/", response_model=List[ProductoOut])
def obtener_productos(db: Session = Depends(get_db)):
    """GET /productos -> lista completa."""
    productos = db.query(Producto).filter(Producto.activo == True).all()  # Solo productos activos 

    return f"Productos encontrados: {len(productos)}"


@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """GET /productos/{id} -> uno solo, o 404 si no existe."""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    return f"Producto encontrado: {producto.nombre}"


@router.post("", response_model=ProductoOut, status_code=201)
def crear_producto(datos: ProductoCreate, db: Session = Depends(get_db)):
    """
    POST /productos -> crea un producto nuevo.
    """
    existente = db.query(Producto).filter(Producto.sku == datos.sku).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese SKU")

    nuevo_producto = Producto(**datos.model_dump())
    db.add(nuevo_producto)
    db.commit()
    db.refresh(nuevo_producto)  # trae de vuelta el id y creado_en que Postgres genero

    return f"Producto creado: {nuevo_producto.nombre}"


@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(producto_id: int, datos: ProductoUpdate, db: Session = Depends(get_db)):
    """
    PUT /productos/{id} -> actualiza SOLO los campos que el cliente mando.
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Deja un diccionario con solo los campos que el cliente mando, para no sobreescribir los demas
    producto_actualizado = datos.model_dump(exclude_unset=True)
    # Actualizar los campos del producto
    for key, value in producto_actualizado.items():
        setattr(producto, key, value)
    
    db.commit()
    db.refresh(producto)
    return f"Producto actualizado: {producto.nombre}"


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    DELETE /productos/{id}.
 
    Decision de diseño: borrado LOGICO, no fisico. En vez de un
    "DELETE FROM productos WHERE id=...", simplemente marcamos
    activo=False. Por que: si el producto ya tiene ventas, compras o
    movimientos de inventario asociados (FK apuntando a el), un borrado
    fisico real fallaria por violar integridad referencial, o peor,
    borraria historial que deberia conservarse para auditoria.
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    producto.activo = False  # Marcamos el producto como inactivo en lugar de eliminarlo físicamente
    db.commit()

    return f"Producto con id {producto_id} marcado como inactivo"
