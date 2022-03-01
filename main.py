from fastapi import FastAPI, Path, Body, Query
from pydantic import BaseModel, Field
from typing import Optional
from uuid import uuid4, UUID
from db import Productos
from enum import Enum

# Instanciasmos FastAPI
app = FastAPI()
productos = Productos()

# Modelos

class Categorias(Enum):
    electronicos = 'Electronicos'
    ropa = 'Ropa'
    herramientas = 'Cocina'
    general = 'General' 
    
class Tienda(BaseModel):
    nombre_plat: str = Field(
        ...,
        min_length=1,
        max_length=45
    )
    pais: Optional[str] = 'Online'
    envios: str
    
class Producto(BaseModel):
    nombre: str = Field(
        ...,
        max_length=45,
        min_length=1
        # example = Ejemplo de Producto
    )
    categoria: Optional[Categorias] = Field(default='General')
    uid: str = str(uuid4())
    color: Optional[str] = None
    precio: int = Field(
        ...,
        gt=0
        )
    contraseña: str = Field(
        ...,
        min_length=8
    )

    class Config:
        schema_extra = {
            'example': {
                'nombre': 'SmartWatch',
                'categoria': 'Electronicos',
                'uid': uuid4(),
                'color': 'Negro',
                'precio': 1223,
                'contraseña': 'stringst'

            }
        }
    
# Path operations
@app.get('/')
def home():
    return {'Hola': 'Mundo'}

# Request body y Response Body
@app.post('/producto/nuevo',
          response_model=Producto,
          response_model_exclude={'contraseña'})
def crear_producto(producto: Producto = Body(...)):
    
    #productos.iniciar_conexion()
    #productos.crear(producto.nombre, producto.categoria, producto.uid, producto.color, producto.precio)
    return producto

# Query parameters
@app.get('/producto/detalle')
def mostrar_producto(
    nombre: Optional[str] = Query(
        None, 
        min_length=1, 
        max_length=45,
        title='Nombre del producto',
        description='Este es el nombre del producto, con un número de caracteres entre 1 y 45',
        example='Lenovo PC'
        ),
    uid: Optional[str] = Query(
        ...,
        title='Unique ID del producto',
        description='Este es el Unique ID del producto que queremos buscar',
        example='a76d6ad9-96e0-4a79-a6b8-75d30e85665f'
        )
):
    return {'nombre': nombre, 'uid': uid}

# Path parameters
@app.get('/producto/detalle/{uid_producto}')
def mostrar_producto(
    uid_producto: str = Path(
        ...,
        max_length=36,
        title='Unique ID del producto',
        description='Unique ID del producto a mostrar, es requerido',
        example='a76d6ad9-96e0-4a79-a6b8-75d30e85665f'
    )
):
    return {'uid_producto': f'{uid_producto} encontrado!'}

# Validaciones: Request Body
@app.put('/producto/{uid_producto}')
def actualizar_producto(
    uid_producto: str = Path(
        ...,
        title='Unique ID del producto',
        description='Unique ID del producto, es requerida',
        max_length=36,
        example='a76d6ad9-96e0-4a79-a6b8-75d30e85665f'
    ),
    producto: Producto = Body(...),
    tienda: Tienda = Body(...)
):
    resultados = producto.dict()
    resultados.update(tienda.dict())
    return producto