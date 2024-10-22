# --- Importation des modules
# sqlalchemy.orm est utilisé pour la session de la base de données, cela permet d'accéder à la base de données, de la lire et de l'écrire, etc.
from datetime import timedelta
from services.utils import get_db
from sqlalchemy.orm import Session
# fastapi.HTTPException est utilisé pour lever des exceptions HTTP
from fastapi import HTTPException, status, Depends
# OAuth2PasswordBearer est utilisé pour la gestion de l'authentification
from fastapi.security import OAuth2PasswordBearer
# typing.Annotated est utilisé pour les annotations
from typing import Annotated
# jose.JWTError est utilisé pour gérer les erreurs liées au JWT, jose.jwt est utilisé pour la gestion des JWT
from jose import JWTError
import models, schemas, tasks

# --- Configuration de l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def add_user(db: Session, user: schemas.UtilisateurCreate) -> models.Utilisateur:
    """
    Cette fonction permet d'ajouter un utilisateur
    @param db: Session
    @param user: schemas.UtilisateurCreate
    @return models.Utilisateur
    """
    existing_user = db.query(models.Utilisateur).filter(
        (models.Utilisateur.login == user.login) | (models.Utilisateur.email == user.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur already registered",
        )

    hashed_password = tasks.get_password_hash(user.password)
    db_user = models.Utilisateur(
        login=user.login,
        email=user.email,
        password=hashed_password,
        date_creation=user.date_creation,
        date_derniere_connexion=user.date_derniere_connexion,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def get_all_users(db: Session) -> list:
    """
    Cette fonction permet de récupérer tous les utilisateurs
    @param db: Session
    @return list
    """
    return db.query(models.Utilisateur).all()

async def authenticate_user(db: Session, username: str, password: str):
    """
    Cette fonction permet d'authentifier un utilisateur par son email ou son login.
    @param db: Session
    @param login: str (peut être un email ou un nom d'utilisateur)
    @param password: str
    @return dict
    """
    # Rechercher l'utilisateur par email ou nom d'utilisateur
    user = db.query(models.Utilisateur).filter(
        (models.Utilisateur.login == username) | (models.Utilisateur.email == username)
    ).first()
    
    if not user or not tasks.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # modifie date_derniere_connexion
    user.date_derniere_connexion = tasks.get_current_datetime()
    db.commit()

    
    access_token = tasks.create_access_token(data={"sub": user.email},expires_delta=timedelta(minutes=300))
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> models.Utilisateur:
    """
    Cette fonction permet de récupérer l'utilisateur actuel
    @param db: Session
    @param token: str
    @return models.Utilisateur
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
    user = db.query(models.Utilisateur).filter(models.Utilisateur.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

async def update_user(db: Session, user_id: int, user: schemas.UtilisateurCreate, current_user: models.Utilisateur) -> models.Utilisateur:
    """
    Cette fonction permet de modifier les informations d'un utilisateur
    @param db: Session
    @param user_id: int
    @param user: schemas.UtilisateurCreate
    @param current_user: models.Utilisateur
    @return models.Utilisateur
    """
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if db_user:
        if db_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough permissions",
            )
        db_user.login = user.login
        db_user.email = user.email
        db_user.date_creation = user.date_creation
        db_user.date_derniere_connexion = user.date_derniere_connexion
        db.commit()
        db.refresh(db_user)
        return db_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Utilisateur not found",
    )

async def delete_user(db: Session, user_id: int, current_user: models.Utilisateur) -> models.Utilisateur:
    """
    Cette fonction permet de supprimer un utilisateur
    @param db: Session
    @param user_id: int
    @param current_user: models.Utilisateur
    @return models.Utilisateur
    """
    db_user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if db_user:
        if db_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough permissions",
            )
        db.delete(db_user)
        db.commit()
        return db_user
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Utilisateur not found",
    )


async def get_user_comptes(db: Session, user_id: int) -> list:
    """
    Cette fonction permet de récupérer les comptes d'un utilisateur
    @param db: Session
    @param user_id: int
    @return list
    """
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if user:
        return user.comptes
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Utilisateur not found",
    )

async def add_user_compte(db: Session, user_id: int, compte: schemas.CompteCreate) -> models.Compte:
    """
    Cette fonction permet de créer un compte pour un utilisateur
    @param db: Session
    @param user_id: int
    @param compte: schemas.CompteCreate
    @return models.Compte
    """
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if user:
        db_compte = models.Compte(**compte.dict(), utilisateur_id=user_id)
        db.add(db_compte)
        db.commit()
        db.refresh(db_compte)
        return db_compte
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Utilisateur not found",
    )

async def delete_user_compte(db: Session, user_id: int, compte_id: int) -> models.Compte:
    """
    Cette fonction permet de supprimer un compte pour un utilisateur
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @return models.Compte
    """
    db_compte = db.query(models.Compte).filter(models.Compte.id == compte_id).first()
    if db_compte:
        db.delete(db_compte)
        db.commit()
        return db_compte
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Compte not found",
    )

async def update_user_compte(db: Session, user_id: int, compte_id: int, compte: schemas.CompteCreate) -> models.Compte:
    """
    Cette fonction permet de modifier un compte pour un utilisateur
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param compte: schemas.CompteCreate
    @return models.Compte
    """
    db_compte = db.query(models.Compte).filter(models.Compte.id == compte_id).first()
    if db_compte:
        db_compte.nom = compte.nom
        db.commit()
        db.refresh(db_compte)
        return db_compte
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Compte not found",
    )

async def add_user_personnage(db: Session, user_id: int, compte_id: int, personnage: schemas.PersonnageCreate) -> models.Personnage:
    """
    Cette fonction permet d'ajouter un personnage pour un compte
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage: schemas.PersonnageCreate
    @return models.Personnage
    """
    compte = db.query(models.Compte).filter(models.Compte.id == compte_id).first()
    if compte:
        db_personnage = models.Personnage(**personnage.dict(), compte_id=compte_id)
        db.add(db_personnage)
        db.commit()
        db.refresh(db_personnage)
        return db_personnage
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Compte not found",
    )

async def get_user_personnages(db: Session, user_id: int, compte_id: int) -> list:
    """
    Cette fonction permet de récupérer les personnages d'un compte
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @return list
    """
    compte = db.query(models.Compte).filter(models.Compte.id == compte_id).first()
    if compte:
        return compte.personnages
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Compte not found",
    )

async def delete_user_personnage(db: Session, user_id: int, compte_id: int, personnage_id: int) -> models.Personnage:
    """
    Cette fonction permet de supprimer un personnage pour un compte
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @return models.Personnage
    """
    db_personnage = db.query(models.Personnage).filter(models.Personnage.id == personnage_id).first()
    if db_personnage:
        db.delete(db_personnage)
        db.commit()
        return db_personnage
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Personnage not found",
    )

async def update_user_personnage(db: Session, user_id: int, compte_id: int, personnage_id: int, personnage: schemas.PersonnageCreate) -> models.Personnage:
    """
    Cette fonction permet de modifier un personnage pour un compte
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param personnage: schemas.PersonnageCreate
    @return models.Personnage
    """
    db_personnage = db.query(models.Personnage).filter(models.Personnage.id == personnage_id).first()
    if db_personnage:
        db_personnage.nom = personnage.nom
        db.commit()
        db.refresh(db_personnage)
        return db_personnage
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Personnage not found",
    )

async def get_user_inventaire(db: Session, user_id: int, compte_id: int, personnage_id: int) -> models.Inventaire:
    """
    Cette fonction permet de récupérer l'inventaire d'un personnage
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @return models.Inventaire
    """
    personnage = db.query(models.Personnage).filter(models.Personnage.id == personnage_id).first()
    if personnage:
        return personnage.inventaire
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Personnage not found",
    )

async def update_user_inventaire(db: Session, user_id: int, compte_id: int, personnage_id: int, inventaire: schemas.InventaireCreate) -> models.Inventaire:
    """
    Cette fonction permet de modifier l'inventaire d'un personnage
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param inventaire: schemas.InventaireCreate
    @return models.Inventaire
    """
    db_inventaire = db.query(models.Inventaire).filter(models.Inventaire.personnage_id == personnage_id).first()
    if db_inventaire:
        db_inventaire = models.Inventaire(**inventaire.dict(), personnage_id=personnage_id)
        db.commit()
        db.refresh(db_inventaire)
        return db_inventaire
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Inventaire not found",
    )

async def delete_user_inventaire(db: Session, user_id: int, compte_id: int, personnage_id: int) -> models.Inventaire:
    """
    Cette fonction permet de supprimer l'inventaire d'un personnage
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @return models.Inventaire
    """
    db_inventaire = db.query(models.Inventaire).filter(models.Inventaire.personnage_id == personnage_id).first()
    if db_inventaire:
        db.delete(db_inventaire)
        db.commit()
        return db_inventaire
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Inventaire not found",
    )


async def add_user_inventaire(db: Session, user_id: int, compte_id: int, personnage_id: int, inventaire: schemas.InventaireCreate) -> models.Inventaire:
    """
    Cette fonction permet d'ajouter un inventaire pour un personnage
    @param db: Session
    @param user_id: int
    @param compte_id: int
    @param personnage_id: int
    @param inventaire: schemas.InventaireCreate
    @return models.Inventaire
    """
    personnage = db.query(models.Personnage).filter(models.Personnage.id == personnage_id).first()
    if personnage:
        db_inventaire = models.Inventaire(**inventaire.dict(), personnage_id=personnage_id)
        db.add(db_inventaire)
        db.commit()
        db.refresh(db_inventaire)
        return db_inventaire
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Personnage not found",
    )