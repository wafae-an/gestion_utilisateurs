from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base
import enum

# Définition des rôles possibles
class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    PASSAGER = "PASSAGER"
    CONDUCTEUR = "CONDUCTEUR"

class User(Base):
    __tablename__ = "users"  # Changement recommandé pour le pluriel

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    phone = Column(String(255), nullable=True)
    email = Column(String(180), nullable=False, unique=True)
    numero_permis=Column(String(255), nullable=True)

    ville = Column(String(100), nullable=True) 
    
    # Nouvel attribut role avec valeurs prédéfinies
    role = Column(
        Enum(UserRole), 
        nullable=False, 
        default=UserRole.PASSAGER
    )
    
    password = Column(String(255), nullable=False)
    token = Column(String(255), nullable=True)
    
    # Champs supplémentaires recommandés
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role.value})>"