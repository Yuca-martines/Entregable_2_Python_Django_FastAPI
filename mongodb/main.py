from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional


# =========================================================
# CONFIGURACIÓN DE FASTAPI
# =========================================================

app = FastAPI(
    title="TechGear API",
    description="API REST para gestión de productos y pedidos",
    version="1.0.0"
)


# =========================================================
# CONEXIÓN A MONGODB
# =========================================================

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

db = client["techgear"]

productos_collection = db["productos"]


# =========================================================
# SCHEMA PRODUCTO - PYDANTIC
# =========================================================

class Producto(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    descripcion: Optional[str] = None
    precio: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    categoria: str


class ProductoRespuesta(Producto):
    id: str


# =========================================================
# FUNCIÓN PARA CONVERTIR MONGODB
# =========================================================

def producto_to_dict(producto):
    return {
        "id": str(producto["_id"]),
        "nombre": producto["nombre"],
        "descripcion": producto.get("descripcion"),
        "precio": producto["precio"],
        "stock": producto["stock"],
        "categoria": producto["categoria"]
    }


# =========================================================
# RUTA PRINCIPAL
# =========================================================

@app.get("/")
def inicio():
    return {
        "mensaje": "TechGear API funcionando correctamente"
    }


# =========================================================
# CREATE - CREAR PRODUCTO
# =========================================================

@app.post(
    "/productos",
    response_model=ProductoRespuesta,
    status_code=201,
    tags=["Productos"]
)
def crear_producto(producto: Producto):

    resultado = productos_collection.insert_one(
        producto.model_dump()
    )

    producto_creado = productos_collection.find_one(
        {"_id": resultado.inserted_id}
    )

    return producto_to_dict(producto_creado)


# =========================================================
# READ - OBTENER TODOS LOS PRODUCTOS
# =========================================================

@app.get(
    "/productos",
    response_model=list[ProductoRespuesta],
    tags=["Productos"]
)
def obtener_productos():

    productos = productos_collection.find()

    return [
        producto_to_dict(producto)
        for producto in productos
    ]


# =========================================================
# READ - OBTENER UN PRODUCTO
# =========================================================

@app.get(
    "/productos/{producto_id}",
    response_model=ProductoRespuesta,
    tags=["Productos"]
)
def obtener_producto(producto_id: str):

    try:
        producto = productos_collection.find_one(
            {"_id": ObjectId(producto_id)}
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="ID de producto inválido"
        )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return producto_to_dict(producto)


# =========================================================
# UPDATE - ACTUALIZAR PRODUCTO
# =========================================================

@app.put(
    "/productos/{producto_id}",
    response_model=ProductoRespuesta,
    tags=["Productos"]
)
def actualizar_producto(
    producto_id: str,
    producto: Producto
):

    try:
        object_id = ObjectId(producto_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="ID de producto inválido"
        )

    resultado = productos_collection.update_one(
        {"_id": object_id},
        {
            "$set": producto.model_dump()
        }
    )

    if resultado.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    producto_actualizado = productos_collection.find_one(
        {"_id": object_id}
    )

    return producto_to_dict(producto_actualizado)


# =========================================================
# DELETE - ELIMINAR PRODUCTO
# =========================================================

@app.delete(
    "/productos/{producto_id}",
    tags=["Productos"]
)
def eliminar_producto(producto_id: str):

    try:
        object_id = ObjectId(producto_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="ID de producto inválido"
        )

    resultado = productos_collection.delete_one(
        {"_id": object_id}
    )

    if resultado.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Producto no encontrado"
        )

    return {
        "mensaje": "Producto eliminado correctamente"
    }