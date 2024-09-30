
# --- Importation des modules
# pydantic est utilisé pour la validation des données
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

# --- Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str = None

# --- User schemas
class UserBase(BaseModel):
    login: str
    email : str
    date_new : Optional[datetime] = datetime.now()
    date_login: Optional[datetime] = datetime.now()
    
# UserCreate est utilisé pour la création d'un utilisateur, il contient un champ password + les champs de UserBase
class UserCreate(UserBase):
    password: str

# User est utilisé pour la lecture d'un utilisateur, il contient un champ id + les champs de UserBase
class User(UserBase):
    id: int
    class Config:
        from_attributes = True

