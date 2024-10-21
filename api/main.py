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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import schemas 
import services.utils as service_utils
import services.user as service_user

# --- Catégories des endpoints (voir documentations Swagger/redocs)
tags_metadata = [
     {
        "name": "Server",
        "description": "Monitor the server state",
    },
    {
        "name": "Utilisateur",
        "description": "Operations with users.",
    },
    {
        "name": "Auth",
        "description": "Operations with authentication.",
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
service_utils.create_database()

# Instance de la base de données
service_utils.get_db()

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
@app.get("/", tags=["Server"])
async def read_item():
    return {
        "message": "Welcome to the API documentation, you can access the documentation at /docs or /redocs",
    }


@app.get("/unixTimes/", tags=["Server"])
async def read_item():
    """
    Cette route permet de récupérer le temps UNIX
    """
    unix_timestamp = datetime.now().timestamp()
    return {"unixTime": unix_timestamp}

# --- Authentification
# On ne peut pas changer le nom de la route, c'est une route prédéfinie par FastAPI
@app.post("/token/", response_model=schemas.Token, tags=["Auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(service_utils.get_db)
)-> schemas.Token:
    """
    Cette route permet de se connecter et de récupérer un token d'accès, à noter qu'ici : username = email
    @param form_data: OAuth2PasswordRequestForm
    @param db: Session
    @return schemas.Token
    """
    return await service_user.authenticate_user(db, form_data.username, form_data.password)

# --- Users
@app.post("/user/", response_model=schemas.Utilisateur, tags=["Utilisateur"])
async def add_user(
    user: schemas.UtilisateurCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Utilisateur:
    """
    Cette route permet d'ajouter un utilisateur
    @param user: schemas.UtilisateurCreate
    @param db: Session
    @return schemas.Utilisateur
    """
    return await service_user.add_user(db, user)

# route qui modifie les informations d'un utilisateur 
@app.put("/user/{user_id}", response_model=schemas.Utilisateur, tags=["Utilisateur"])
async def update_user(
    user_id: int,
    user: schemas.UtilisateurCreate,
    current_user: Annotated[schemas.Utilisateur, Depends(service_user.get_current_user)],
    db: Session = Depends(service_utils.get_db)
)-> schemas.Utilisateur:
    """
    Cette route permet de modifier les informations d'un utilisateur
    @param user_id: int
    @param user: schemas.UtilisateurCreate
    @param db: Session
    @return schemas.Utilisateur
    """
    return await service_user.update_user(db, user_id, user,current_user )

# route qui supprime un utilisateur
@app.delete("/user/{user_id}", response_model=schemas.Utilisateur, tags=["Utilisateur"])
async def delete_user(
    user_id: int,
    current_user: Annotated[schemas.Utilisateur, Depends(service_user.get_current_user)],
    db: Session = Depends(service_utils.get_db)
)-> schemas.Utilisateur:
    """
    Cette route permet de supprimer un utilisateur
    @param user_id: int
    @param db: Session
    @return schemas.Utilisateur
    """
    return await service_user.delete_user(db, user_id, current_user)

@app.get("/user/me/", response_model=schemas.Utilisateur, tags=["Utilisateur"])
async def read_users_me(
    current_user: Annotated[schemas.Utilisateur, Depends(service_user.get_current_user)]
):
    return current_user


@app.get("/users/", response_model=list[schemas.Utilisateur], tags=["Utilisateur"])
async def read_users(
    current_user: Annotated[schemas.Utilisateur, Depends(service_user.get_current_user)],
    db: Session = Depends(service_utils.get_db)
)-> list[schemas.Utilisateur]:
    """
    Cette route permet de récupérer tous les utilisateurs
    @param db: Session
    @return list[schemas.Utilisateur]
    """
    return await service_user.get_all_users(db)

# route qui permet de récupérer les comptes d'un utilisateur 
@app.get("/user/{user_id}/comptes/", response_model=list[schemas.Compte], tags=["Utilisateur"])
async def read_user_comptes(
    user_id: int,
    db: Session = Depends(service_utils.get_db)
)-> list[schemas.Compte]:
    """
    Cette route permet de récupérer les comptes d'un utilisateur
    @param user_id: int
    @param db: Session
    @return list[schemas.Compte]
    """
    return await service_user.get_user_comptes(db, user_id)

# route qui permet de créer un compte pour un utilisateur
@app.post("/user/{user_id}/compte/", response_model=schemas.Compte, tags=["Utilisateur"])
async def add_user_compte(
    user_id: int,
    compte: schemas.CompteCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Compte:
    """
    Cette route permet de créer un compte pour un utilisateur
    @param user_id: int
    @param compte: schemas.CompteCreate
    @param db: Session
    @return schemas.Compte
    """
    return await service_user.add_user_compte(db, user_id, compte)

# route qui permet de de supprimer un compte pour un utilisateur
@app.delete("/user/{user_id}/compte/{compte_id}", response_model=schemas.Compte, tags=["Utilisateur"])
async def delete_user_compte(
    user_id: int,
    compte_id: int,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Compte:
    """
    Cette route permet de supprimer un compte pour un utilisateur
    @param user_id: int
    @param compte_id: int
    @param db: Session
    @return schemas.Compte
    """
    return await service_user.delete_user_compte(db, user_id, compte_id)

# route qui permet de modifier un compte pour un utilisateur
@app.put("/user/{user_id}/compte/{compte_id}", response_model=schemas.Compte, tags=["Utilisateur"])
async def update_user_compte(
    user_id: int,
    compte_id: int,
    compte: schemas.CompteCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Compte:
    """
    Cette route permet de modifier un compte pour un utilisateur
    @param user_id: int
    @param compte_id: int
    @param compte: schemas.CompteCreate
    @param db: Session
    @return schemas.Compte
    """
    return await service_user.update_user_compte(db, user_id, compte_id, compte)

# route qui permet de récupérer d'ajouter un personnage pour un compte
@app.post("/user/{user_id}/compte/{compte_id}/personnage/", response_model=schemas.Personnage, tags=["Utilisateur"])
async def add_user_personnage(
    user_id: int,
    compte_id: int,
    personnage: schemas.PersonnageCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Personnage:
    """
    Cette route permet d'ajouter un personnage pour un compte
    @param user_id: int
    @param compte_id: int
    @param personnage: schemas.PersonnageCreate
    @param db: Session
    @return schemas.Personnage
    """
    return await service_user.add_user_personnage(db, user_id, compte_id, personnage)

# route qui permet de récupérer les personnages d'un compte
@app.get("/user/{user_id}/compte/{compte_id}/personnages/", response_model=list[schemas.Personnage], tags=["Utilisateur"])
async def read_user_personnages(
    user_id: int,
    compte_id: int,
    db: Session = Depends(service_utils.get_db)
)-> list[schemas.Personnage]:
    """
    Cette route permet de récupérer les personnages d'un compte
    @param user_id: int
    @param compte_id: int
    @param db: Session
    @return list[schemas.Personnage]
    """
    return await service_user.get_user_personnages(db, user_id, compte_id)

# route qui permet de supprimer un personnage d'un compte
@app.delete("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}", response_model=schemas.Personnage, tags=["Utilisateur"])
async def delete_user_personnage(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Personnage:
    """
    Cette route permet de supprimer un personnage d'un compte
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param db: Session
    @return schemas.Personnage
    """
    return await service_user.delete_user_personnage(db, user_id, compte_id, personnage_id)

# route qui permet de modifier un personnage d'un compte
@app.put("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}", response_model=schemas.Personnage, tags=["Utilisateur"])
async def update_user_personnage(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    personnage: schemas.PersonnageCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Personnage:
    """
    Cette route permet de modifier un personnage d'un compte
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param personnage: schemas.PersonnageCreate
    @param db: Session
    @return schemas.Personnage
    """
    return await service_user.update_user_personnage(db, user_id, compte_id, personnage_id, personnage)

# route qui permet de récupérer l'inventaire d'un personnage
@app.get("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}/inventaire/", response_model=schemas.Inventaire, tags=["Utilisateur"])
async def read_user_inventaire(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Inventaire:
    """
    Cette route permet de récupérer l'inventaire d'un personnage
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param db: Session
    @return schemas.Inventaire
    """
    return await service_user.get_user_inventaire(db, user_id, compte_id, personnage_id)

# route qui permet de modifier l'inventaire d'un personnage
@app.put("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}/inventaire/", response_model=schemas.Inventaire, tags=["Utilisateur"])
async def update_user_inventaire(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    inventaire: schemas.InventaireCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Inventaire:
    """
    Cette route permet de modifier l'inventaire d'un personnage
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param inventaire: schemas.InventaireCreate
    @param db: Session
    @return schemas.Inventaire
    """
    return await service_user.update_user_inventaire(db, user_id, compte_id, personnage_id, inventaire)

# route qui permet de supprimer l'inventaire d'un personnage
@app.delete("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}/inventaire/", response_model=schemas.Inventaire, tags=["Utilisateur"])

async def delete_user_inventaire(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Inventaire:
    """
    Cette route permet de supprimer l'inventaire d'un personnage
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param db: Session
    @return schemas.Inventaire
    """
    return await service_user.delete_user_inventaire(db, user_id, compte_id, personnage_id)


# route qui permet d'ajouter un objet à l'inventaire d'un personnage
@app.post("/user/{user_id}/compte/{compte_id}/personnage/{personnage_id}/inventaire/", response_model=schemas.Inventaire, tags=["Utilisateur"])
async def add_user_inventaire(
    user_id: int,
    compte_id: int,
    personnage_id: int,
    inventaire: schemas.InventaireCreate,
    db: Session = Depends(service_utils.get_db)
)-> schemas.Inventaire:
    """
    Cette route permet d'ajouter un objet à l'inventaire d'un personnage
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param inventaire: schemas.InventaireCreate
    @param db: Session
    @return schemas.Inventaire
    """
    return await service_user.add_user_inventaire(db, user_id, compte_id, personnage_id, inventaire)





