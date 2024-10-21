from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from tasks import get_current_datetime

# --- Schémas pour Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Schémas Utilisateur
class UtilisateurBase(BaseModel):
    login: str
    email: str
    date_creation: Optional[datetime] = Field(default_factory=get_current_datetime)
    date_derniere_connexion: Optional[datetime] = Field(default_factory=get_current_datetime)

class UtilisateurCreate(UtilisateurBase):
    password: str

class Utilisateur(UtilisateurBase):
    id: int
    comptes: Optional[List['Compte']] = []

    class Config:
        from_attributes = True

# --- Schémas Compte
class CompteBase(BaseModel):
    nom: str

class CompteCreate(CompteBase):
    pass

class Compte(CompteBase):
    id: int
    utilisateur_id: int
    personnages: Optional[List['Personnage']] = []

    class Config:
        from_attributes = True

# --- Schémas Personnage
class PersonnageBase(BaseModel):
    nom: str

class PersonnageCreate(PersonnageBase):
    pass

class Personnage(PersonnageBase):
    id: int
    compte_id: int
    inventaire: Optional['Inventaire'] = None

    class Config:
        from_attributes = True

# --- Schémas Inventaire
class InventaireBase(BaseModel):
    objet : str
    pass

class InventaireCreate(InventaireBase):
    pass

class Inventaire(InventaireBase):
    id: int
    personnage_id: int


    class Config:
        from_attributes = True
