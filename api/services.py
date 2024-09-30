# --- Importation des modules
# sqlalchemy.orm est utilisé pour la session de la base de données, cela permet d'accéder à la base de données, de la lire et de l'écrire, etc.
from sqlalchemy.orm import Session
# fastapi.HTTPException est utilisé pour lever des exceptions HTTP
from fastapi import HTTPException, status, Depends
# OAuth2PasswordBearer est utilisé pour la gestion de l'authentification
from fastapi.security import OAuth2PasswordBearer
# typing.Annotated est utilisé pour les annotations
from typing import Annotated
# jose.JWTError est utilisé pour gérer les erreurs liées au JWT, jose.jwt est utilisé pour la gestion des JWT
from jose import JWTError
import models, schemas, tasks, database, random

# --- Configuration de l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Fonctions de services
def create_database():
    """
    Cette fonction permet de créer la base de données
    @return None
    """
    return database.Base.metadata.create_all(bind=database.engine)

def get_db() -> Session:
    """
    Cette fonction permet de récupérer la session de la base de données
    @return Session
    """
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Users
async def get_all_users(db: Session) -> list:
    """
    Cette fonction permet de récupérer tous les utilisateurs
    @param db: Session
    @return list
    """
    return db.query(models.User).all()

async def add_user(db: Session, user: schemas.UserCreate) -> models.User:
    """
    Cette fonction permet d'ajouter un utilisateur
    @param db: Session
    @param user: schemas.UserCreate
    @return models.User
    """
    existing_user = db.query(models.User).filter(
        (models.User.login == user.login) | (models.User.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already registered",
        )

    hashed_password = tasks.get_password_hash(user.password)
    db_user = models.User(
        login=user.login,
        email=user.email,
        password=hashed_password,
        date_new=user.date_new,
        date_login=user.date_login
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def authenticate_user(db: Session, username: str, password: str):
    """
    Cette fonction permet d'authentifier un utilisateur par son email ou son login.
    @param db: Session
    @param login: str (peut être un email ou un nom d'utilisateur)
    @param password: str
    @return dict
    """
    # Rechercher l'utilisateur par email ou nom d'utilisateur
    user = db.query(models.User).filter(
        (models.User.login == username) | (models.User.email == username)
    ).first()
    
    if not user or not tasks.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = tasks.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.User:
    """
    Cette fonction permet de récupérer l'utilisateur actuel
    @param db: Session
    @param token: str
    @return models.User
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = tasks.jwt.decode(token, tasks.SECRET_KEY, algorithms=[tasks.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user