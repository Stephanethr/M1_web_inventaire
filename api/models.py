# --- Importation des modules
# sqlalchemy est utilisé pour la gestion de la base de données, cela permet de créer des modèles de données, de les manipuler, etc.
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
# sqlalchemy.orm est utilisé pour la session de la base de données, cela permet d'accéder à la base de données, de la lire et de l'écrire, etc.
from sqlalchemy.orm import relationship
# sqlalchemy.ext.declarative est utilisé pour la déclaration de la base de données
from database import Base
from datetime import datetime

# --- User model
class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True, unique=True)
    password = Column(String)
    email = Column(String, index=True, unique=True)
    date_new = Column(DateTime, default=datetime.now)
    date_login = Column(DateTime, default=datetime.now)
    # user_compte_id 