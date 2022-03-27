from datetime import date, datetime
from fastapi import Body, FastAPI, HTTPException, Path, status
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Optional, List
import string, random, json

app = FastAPI() # 🏁

# Modelos

class UsuarioBase(BaseModel):
    id_usuario: str = Field(title='ID Usuario',
                             default=''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]))
    email: EmailStr = Field(...,
                            title='Email')
    
class Usuario(UsuarioBase):
    nombre: str = Field(...,
                        title='Nombre',
                        min_length=1,
                        max_length=30)
    apellido: str =  Field(...,
                           title='Apellido',
                           min_length=1,
                           max_length=30)
    fecha_nacimiento: Optional[date] = Field(default=None,
                                             title='Fecha Nacimiento')

class UsuarioIngresar(UsuarioBase):
    contrasena: str = Field(...,
                            title='Contrasena',
                            min_length=8)
    
class UsuarioRegistro(Usuario, UsuarioIngresar):
    pass

class UsuarioLoginOut(UsuarioBase):
    mensaje: str = Field(title='Mensaje de salida',
                         default='Ingreso correcto')
    
class Tweet(BaseModel):
    id_tweet: str = Field(default=''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)]))
    contenido: str = Field(...,
                          max_length=256,
                          min_length=1)
    timestamp_pub: datetime = Field(default=datetime.now())
    timestamp_act: Optional[datetime] = Field()
    autor: Usuario = Field(..., exclude={'contrasena', 'fecha_nacimiento'})
    
# Path Operations

@app.get(
    path="/",
    status_code=status.HTTP_200_OK,
    tags=['🔵']
)
def home() -> Dict[str, str]:
    return {'Bienvenido': 'API Twitter Clone 🐦️'}

# Generación de ID para usuarios
@app.get(
    path="/generacion-id",
    status_code=status.HTTP_200_OK,
    tags=['🔵'],
    summary='Genera un ID para usuarios y tweets nuevos'
)
def generacion_id() -> str:
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

##### Usuarios #####

# Registro de usuarios
@app.post(
    path='/registrar',
    response_model=Usuario,
    status_code=status.HTTP_201_CREATED,
    summary='Registrar un usuario',
    tags=['Usuarios']
)
def registrar(usuario: UsuarioRegistro = Body(...)) -> Usuario:
    """
    Registro
    
    Registra un usuario en la app
    
    Parámetros:
        - Request body parameter
            - usuario: UsuarioRegistro
    
    Regresa un JSON con la información básica del usuario:
        - id_usuario: str
        - email: EmailStr
        - nombre: str
        - apellido: str
        - fecha_nacimiento: date
    """
    with open('./usuarios.json', 'r+', encoding='utf-8') as f:
        contenido = json.loads(f.read())
        diccionario_usuarios = usuario.dict()
        diccionario_usuarios['id_usuario'] = str(diccionario_usuarios['id_usuario'])
        diccionario_usuarios['fecha_nacimiento'] = str(diccionario_usuarios['fecha_nacimiento'])
        contenido.append(diccionario_usuarios)
        f.seek(0)
        f.write(json.dumps(contenido))
        return usuario

# Acceso a la app
@app.post(
    path='/ingresar',
    response_model=UsuarioLoginOut,
    status_code=status.HTTP_200_OK,
    summary='Ingresar con un usuario',
    tags=['Usuarios']
)
def ingresar(usuario: UsuarioIngresar) -> UsuarioLoginOut:
    """
    Ingresar
    
    Ingresa con los datos de un usuario a la app
    
    Parámetros:
        - Request body parameter
            - usuario: UsuarioIngresar
    
    Regresa un JSON con la información básica del usuario y un mensaje de ingreso correcto o incorrecto:
        - id_usuario: str
        - email: EmailStr
        - mensaje: str
    """
    with open('./usuarios.json', 'r', encoding='utf-8') as f:
        usuarios  = json.loads(f.read())
        for u in usuarios:
            if u['email'] == usuario.email and u['contrasena'] == usuario.contrasena:
                return UsuarioLoginOut(email=usuario.email, id_usuario=usuario.id_usuario)
            else:
                return UsuarioLoginOut(email=usuario.email, id_usuario=usuario.id_usuario, mensaje='Ingreso incorrecto')

# Mostrar usuarios
@app.get(
    path='/usuarios',
    response_model=List[Usuario],
    status_code=status.HTTP_200_OK,
    summary='Muestra todos los usuarios',
    tags=['Usuarios']
)
def mostrar_usuarios() -> List[Usuario]:
    """
    Muestra todos los usuarios de la aplicación
    
    Parameters:
        - 
        
    Regresa un JSON con todos los usuarios en la aplicación con las siguientes llaves:
        - id_usuario: str
        - email: EmailStr
        - nombre: str
        - apellido: str
        - fecha_nacimiento: date    
    """
    with open('./usuarios.json', 'r', encoding='utf-8') as f:
        contenido = json.loads(f.read())
        return contenido

# Mostrar un usuario 
@app.get(
    path='/usuarios/{id_usuario}',
    response_model=Usuario,
    status_code=status.HTTP_200_OK,
    summary='Muestra un usuario',
    tags=['Usuarios']
)
def mostrar_usuario(id_usuario: str = Path(...,
                                             title='ID Usuario',
                                             description='ID del Usuario que deseas')
    ) -> Usuario:
    """
    Muestra a un usuario de la aplicación
    
    Parameters:
        - id_usuario: str
        
    Regresa un JSON con el usuario y con las siguientes llaves:
        - id_usuario: str
        - email: EmailStr
        - nombre: str
        - apellido: str
        - fecha_nacimiento: date    
    """
    with open('./usuarios.json', 'r+', encoding='utf-8') as f:
        usuarios = json.loads(f.read())
        
        for usuario in usuarios:
            if str(usuario['id_usuario']) == str(id_usuario):
                return usuario
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Usuario no encontrado')
    
# Actualizar información de un usuario    
@app.put(
    path='/usuarios/{id_usuario}',
    response_model=Usuario,
    status_code=status.HTTP_200_OK,
    summary='Actualiza a un usuario',
    tags=['Usuarios']
)
def actualizar_usuario(id_usuario: str = Path(...,
                                             title='ID Usuario',
                                             description='ID del Usuario que deseas'),

                        usuario_act: UsuarioRegistro = Body(...,
                                                        title='Usuario Actualizado',
                                                        description='Datos del usuario actualizados')
    ) -> Usuario:
    """
    Actualizar un usuario
    
    Actualiza un usuario de un ID especifico con los datos del usuario proporcionados
    
    Parameters:
        - id_usuario: str
        - usuario: UsuarioRegistro
    
    Retorna el usuario con las actualizaciones correspondientes con las siguientes llaves:
        - id_usuario: str
        - email: EmailStr
        - nombre: str
        - apellido: str
        - fecha_nacimiento: date        
    """
    diccionario_usuario = usuario_act.dict()
    diccionario_usuario['fecha_nacimiento'] = str(diccionario_usuario['fecha_nacimiento'])
    
    with open('./usuarios.json', 'r+', encoding='utf-8') as f:
        usuarios = json.loads(f.read())
        
    for usuario in usuarios:
        if str(usuario['id_usuario']) == id_usuario:
            usuarios[usuarios.index(usuario)] = diccionario_usuario
            with open('./usuarios.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                f.write(json.dumps(usuarios))
            return diccionario_usuario
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Usuario no encontrado'
        )

# Borrar un usuario
@app.delete(
    path='/usuarios/{id_usuario}',
    status_code=status.HTTP_200_OK,
    summary='Borra a un usuario',
    tags=['Usuarios']
)
def borrar_usuario(id_usuario: str = Path(...,
                                             title='ID Usuario',
                                             description='ID del Usuario que deseas')
    ) -> Usuario:
    """
    Borrar
    
    Borrar un usuario de la app
    
    Parameters:
        - id_usuario: str
        
    Retorna el usuario que se borró con todas sus llaves:
        - id_usuario: str
        - email: EmailStr
        - contraseña: str
        - nombre: str
        - apellido: str
        - fecha_nacimiento: date      
    """
    with open('./usuarios.json', 'r+', encoding='utf-8') as f: 
        usuarios = json.loads(f.read())
    for usuario in usuarios:
        if usuario['id_usuario'] == id_usuario:
            usuarios.remove(usuario)
            with open('./usuarios.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                f.write(json.dumps(usuarios))
            return usuario
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Usario no encontrado'
    )

##### Tweets #####

# Mostrar todos los tweets
@app.get(
    path="/tweets",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Muestra a todos los tweets",
    tags=["Tweets"]
)
def mostrar_tweets() -> List[Tweet]:
    """
    Muestra todos los tweets de la aplicación
    
    Parameters:
        - 
        
    Regresa un JSON con todos los tweets en la aplicación con las siguientes llaves:
        - id_tweet: str
        - contenido: str
        - autor: Usuario
        - fecha_pub: date
        - fecha_act: date    
    """
    with open('./tweets.json', 'r', encoding='utf-8') as f:
        contenido = json.loads(f.read())
        return contenido

# Postear un tweet
@app.post(
    path="/post_tweet",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Postea un tweet",
    tags=["Tweets"]
)
def post(tweet: Tweet = Body(...)) -> Tweet: 
    """
    Postea un tweet en la aplicación
    
    Parameters:
        - 
        
    Regresa un JSON con el tweet posteado en la aplicación con las siguientes llaves:
        - id_tweet: str
        - contenido: str
        - autor: Usuario
        - fecha_pub: date
        - fecha_act: date    
    """
    with open("./tweets.json", "r+", encoding="utf-8") as f:
        tweets = json.load(f)
        tweet_dict = tweet.dict()
        tweets.append(tweet_dict)
        f.seek(0)
        json.dump(tweets, f, default=str, indent=4)
        return tweet

# Mostrar un tweet especifico
@app.get(
    path='/tweets/{id_tweet}',
    response_model=Tweet,
    summary='Muestra un tweet',
    status_code=status.HTTP_200_OK,
    tags=['Tweets']
)
def mostrar_tweet(id_tweet: str = Path(...,
                                        title='ID del tweet',
                                        description='ID del tweet a mostrar')) -> Tweet:
    """
    Muestra un tweet de la aplicación
    
    Parameters:
        - id_tweet: str
        
    Regresa un JSON con el tweet especificado con las siguientes llaves:
        - id_tweet: str
        - contenido: str
        - autor: Usuario
        - fecha_pub: date
        - fecha_act: date 
    """
    with open('./tweets.json', 'r+', encoding='utf-8') as f:
        tweets = json.loads(f.read())
        
        for tweet in tweets:
            if str(tweet['id_tweet']) == str(id_tweet):
                return tweet
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail='Tweet no encontrado')

# Actualizar un tweet
@app.put(
    path='/tweets/{id_tweet}',
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary='Actualiza un tweet',
    tags=['Tweets']
)
def actualizar_tweet(id_tweet: str = Path(...,
                                        title='ID del tweet',
                                        description='ID del tweet a actualizar'),
                     tweet_act: Tweet = Body(...,
                                             title='Tweet actualizado',
                                             description='Tweet con los valores actualizados')) -> Tweet:
    """
    Actualizar un tweet
    
    Actualiza un tweet de un ID especifico con los datos proporcionados
    
    Parameters:
        - id_tweet: str = Path
        - tweet: Tweet = Body
    
    Regresa un JSON con el tweet actualizado y con las siguientes llaves:
        - id_tweet: str
        - contenido: str
        - autor: Usuario
        - fecha_pub: date
        - fecha_act: date        
    """
    diccionario_tweet = tweet_act.dict()
    diccionario_tweet['timestamp_pub'] = str(diccionario_tweet['timestamp_pub'])
    diccionario_tweet['timestamp_act'] = str(diccionario_tweet['timestamp_act'])
    
    with open('./tweets.json', 'r+', encoding='utf-8') as f:
        tweets = json.loads(f.read())
        
    for tweet in tweets:
        if str(tweet['id_tweet']) == id_tweet:
            tweets[tweets.index(tweet)] = diccionario_tweet
            with open('./tweets.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                f.write(json.dumps(tweets))
            return diccionario_tweet
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Tweet no encontrado'
            )

# Borrar un tweet
@app.delete(
    path='/tweets/{id_tweet}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Borra un tweet',
    tags=['Tweets']
)
def borrar_tweet(id_tweet: str = Path(...,
                                        title='ID del tweet',
                                        description='ID del tweet a borrar')) -> Tweet:
    """
    Borrar
    
    Borrar un tweet de la app
    
    Parameters:
        - id_tweet: str
        
    Regresa un JSON con el tweet borrado y con las siguientes llaves:
        - id_tweet: str
        - contenido: str
        - autor: Usuario
        - fecha_pub: date
        - fecha_act: date        
    """
    with open('./tweets.json', 'r+', encoding='utf-8') as f: 
        tweets = json.loads(f.read())
    for tweet in tweets:
        if str(tweet['id_tweet']) == id_tweet:
            tweets.remove(tweet)
            with open('./tweets.json', 'w', encoding='utf-8') as f:
                f.seek(0)
                f.write(json.dumps(tweets))
            return tweet
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Tweet no encontrado'
    )