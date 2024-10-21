from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from tasks import get_current_datetime

# --- Modèle Utilisateur
class Utilisateur(Base):
    __tablename__ = "Utilisateur"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String, index=True, unique=True)
    email = Column(String, index=True, unique=True)
    password = Column(String)
    date_creation = Column(DateTime, default=get_current_datetime)
    date_derniere_connexion = Column(DateTime, default=get_current_datetime)

    # Relation : un utilisateur peut avoir plusieurs comptes
    comptes = relationship("Compte", back_populates="utilisateur")

# --- Modèle Compte
class Compte(Base):
    __tablename__ = "Compte"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True)
    utilisateur_id = Column(Integer, ForeignKey("Utilisateur.id"))

    # Relation : un compte est associé à un utilisateur
    utilisateur = relationship("Utilisateur", back_populates="comptes")

    # Relation : un compte peut avoir plusieurs personnages
    personnages = relationship("Personnage", back_populates="compte")

# --- Modèle Personnage
class Personnage(Base):
    __tablename__ = "Personnage"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True)
    compte_id = Column(Integer, ForeignKey("Compte.id"))

    # Relation : un personnage est associé à un compte
    compte = relationship("Compte", back_populates="personnages")

    # Relation : un personnage a un seul inventaire
    inventaire = relationship("Inventaire", uselist=False, back_populates="personnage")

# --- Modèle Inventaire
class Inventaire(Base):
    __tablename__ = "Inventaire"
    id = Column(Integer, primary_key=True, index=True)
    objet = Column(String)
    personnage_id = Column(Integer, ForeignKey("Personnage.id"))

    # Relation : un inventaire est associé à un seul personnage
    personnage = relationship("Personnage", back_populates="inventaire")
