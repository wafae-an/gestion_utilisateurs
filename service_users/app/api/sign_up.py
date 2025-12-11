from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserRegister, UserRegisterResponse
from app.security import hash_password, create_access_token
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post(
    "/register",
    response_model=UserRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouveau passager"
)
async def register_passager(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Inscription d'un nouveau passager avec génération automatique du token.
    
    - **firstname**: Prénom (obligatoire)
    - **lastname**: Nom (obligatoire) 
    - **phone**: Téléphone (optionnel)
    - **email**: Email (obligatoire, unique)
    - **password**: Mot de passe (sera haché)
    """
    
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )

    try:
        # Hacher le mot de passe
        hashed_password = hash_password(user_data.password)
        
        # Créer le nouvel utilisateur
        new_user = User(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            phone=user_data.phone,
            email=user_data.email,
            role=UserRole.PASSAGER,
            password=hashed_password,
            is_active=True
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Générer le token JWT
        token = create_access_token(
            user_email=new_user.email,
            role=new_user.role
        )

        # Mettre à jour l'utilisateur avec le token
        new_user.token = token
        db.commit()

        # Retourner la réponse
        return {
            "id": new_user.id,
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "email": new_user.email,
            "role": new_user.role.value,
            "token": token
        }

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la création du compte"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )