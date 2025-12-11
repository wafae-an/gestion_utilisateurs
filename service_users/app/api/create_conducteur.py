from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

from database import get_db
from app.models.user import User, UserRole
from app.security import hash_password, create_access_token

router = APIRouter()

# Schéma Pydantic pour la création d'utilisateur
class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    numero_permis: str
    ville:str

# Schéma de réponse
class UserResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    numero_permis:str
    phone: Optional[str]
    role: str
    is_active: bool
    token: str
    created_at: datetime
    ville:str

    class Config:
        from_attributes = True

@router.post(
    "/conducteurs",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau conducteur",
    description="Crée un nouvel utilisateur avec le rôle CONDUCTEUR"
)
async def create_conducteur(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouvel utilisateur avec le rôle CONDUCTEUR
    
    - **firstname**: Prénom (obligatoire)
    - **lastname**: Nom (obligatoire) 
    - **email**: Email (obligatoire, unique)
    - **phone**: Téléphone (optionnel)
    - **password**: Mot de passe (obligatoire)
    """
    
    try:
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )

        # Hasher le mot de passe
        hashed_password = hash_password(user_data.password)
        
        # Créer le token JWT
        token = create_access_token(
            user_email=user_data.email,
            role=UserRole.CONDUCTEUR
        )

        # Créer l'utilisateur
        new_user = User(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            email=user_data.email,
            phone=user_data.phone,
            numero_permis=user_data.numero_permis,
            password=hashed_password,
            role=UserRole.CONDUCTEUR,  # Rôle fixé à CONDUCTEUR
            token=token,
            is_active=True,
            ville=user_data.ville
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Retourner la réponse
        return UserResponse(
            id=new_user.id,
            firstname=new_user.firstname,
            lastname=new_user.lastname,
            email=new_user.email,
            phone=new_user.phone,
            numero_permis=new_user.numero_permis,
            role=new_user.role.value,  # Convertir l'enum en string
            is_active=new_user.is_active,
            token=new_user.token,
            created_at=new_user.created_at,
            ville=new_user.ville
        )

    except HTTPException:
        # Re-raise les HTTPException
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de l'utilisateur: {str(e)}"
        )