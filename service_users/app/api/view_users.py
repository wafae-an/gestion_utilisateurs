from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from database import get_db
from app.models.user import User, UserRole

router = APIRouter()

# Schéma de réponse pour un utilisateur
class UserResponse(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str
    phone: Optional[str] = None
    numero_permis: Optional[str] = None
    ville: Optional[str] = None
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schéma de réponse pour la liste
class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total: int

@router.get(
    "/users",
    response_model=UsersListResponse,
    summary="Récupérer tous les utilisateurs",
    description="Retourne la liste de tous les utilisateurs de la base de données"
)
async def get_all_users(
    db: Session = Depends(get_db),
    role: Optional[UserRole] = Query(None, description="Filtrer par rôle"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif")
):
    """
    Récupère tous les utilisateurs avec filtres optionnels
    
    - **role**: Filtre par rôle (PASSAGER, CONDUCTEUR, ADMIN)
    - **is_active**: Filtre par statut actif/inactif
    """
    
    try:
        # Construction de la requête de base
        query = db.query(User)
        
        # Application des filtres
        if role:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Récupération de tous les utilisateurs
        users = query.order_by(User.created_at.desc()).all()
        
        # Conversion des utilisateurs en schéma de réponse
        users_response = [
            UserResponse(
                id=user.id,
                firstname=user.firstname,
                lastname=user.lastname,
                email=user.email,
                phone=user.phone,
                numero_permis=user.numero_permis,
                ville=user.ville,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            for user in users
        ]
        
        return UsersListResponse(
            users=users_response,
            total=len(users_response)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des utilisateurs: {str(e)}"
        )