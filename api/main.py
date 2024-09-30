# --- Importation des modules
# -- Fast API
from fastapi import FastAPI, Depends
# OAuth2PasswordBearer est utilisé pour la gestion de l'authentification, OAuth2PasswordRequestForm est utilisé pour la gestion de la requête d'authentification
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# CORS est utilisé pour la gestion des requêtes CORS
from fastapi.middleware.cors import CORSMiddleware
# --- SQLAlchemy
from sqlalchemy.orm import Session
# datetime est utilisé pour la gestion des dates
from datetime import datetime
# typing.Annotated est utilisé pour la gestion des annotations
from typing import Annotated
import schemas, services
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# --- Catégories des endpoints (voir documentations Swagger/redocs)
tags_metadata = [
     {
        "name": "Server",
        "description": "Monitor the server state",
    },
    {
        "name": "Users",
        "description": "Operations with users. The **login** logic is also here.",
    },
]

# --- FastAPI app
app = FastAPI(
    title="API FastAPI",
    description="This is the API documentation for the API FastAPI",
)
# Servir les fichiers statiques du dossier 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# Migration de la base de données
services.create_database()

# Instance de la base de données
services.get_db()

# --- Configuration CORS
# il est possible de passer un tableau avec les origines autorisées, les méthodes autorisées, les en-têtes autorisés, etc.
# ici, on autorise toutes les origines, les méthodes, les en-têtes, etc car on est en développement, en production, il faudra restreindre ces valeurs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Créer une instance de OAuth2PasswordBearer avec l'URL personnalisée
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Routes
# --- Server
# @app.get("/", tags=["Server"])
# async def root():
#     """
#     Cette route permet de vérifier si le serveur est en ligne
#     """
#     return {"message": "API is online, welcome to the API documentation at /docs or /redocs"}


@app.get("/", response_class=HTMLResponse)
async def read_item():
    """
    Cette route permet de vérifier si le serveur est en ligne
    """
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API is online</title>
        </head>
        <body>
            <h1>API is online, welcome to the API documentation at <a href="/docs">/docs</a> or <a href="/redocs">/redocs</a></h1>
        </body>
    </html>
    """


@app.get("/unixTimes", tags=["Server"])
async def read_item():
    """
    Cette route permet de récupérer le temps UNIX
    """
    unix_timestamp = datetime.now().timestamp()
    return {"unixTime": unix_timestamp}

# --- Users
# On ne peut pas changer le nom de la route, c'est une route prédéfinie par FastAPI
@app.get("/token/", response_model=schemas.Token, tags=["Users"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(services.get_db)
)-> schemas.Token:
    """
    Cette route permet de se connecter et de récupérer un token d'accès, à noter qu'ici : username = email
    @param form_data: OAuth2PasswordRequestForm
    @param db: Session
    @return schemas.Token
    """
    return await services.authenticate_user(db, form_data.username, form_data.password)

@app.get("/users/", response_model=list[schemas.User], tags=["Users"])
async def read_users(
    current_user: Annotated[schemas.User, Depends(services.get_current_user)],
    db: Session = Depends(services.get_db)
)-> list[schemas.User]:
    """
    Cette route permet de récupérer tous les utilisateurs
    @param db: Session
    @return list[schemas.User]
    """
    return await services.get_all_users(db)

@app.post("/user/", response_model=schemas.User, tags=["Users"])
async def add_user(
    user: schemas.UserCreate,
    db: Session = Depends(services.get_db)
)-> schemas.User:
    """
    Cette route permet d'ajouter un utilisateur
    @param user: schemas.UserCreate
    @param db: Session
    @return schemas.User
    """
    return await services.add_user(db, user)

@app.get("/user/me/", response_model=schemas.User, tags=["Users"])
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(services.get_current_user)]
):
    return current_user
