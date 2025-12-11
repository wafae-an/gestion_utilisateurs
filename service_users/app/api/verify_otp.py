from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from app.services.verify_code_email import verify_otp_code

router = APIRouter()

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

@router.post("/verify_code",summary="Vérifier le code OTP (étape 2/2) et finaliser la connexion",
    description=(
        "Valide le code OTP envoyé par e-mail, supprime le code (anti-replay), "
        "puis renvoie le jeton d'accès et les rôles de l'utilisateur."
    ),
    responses={
        200: {"description": "OTP valide, token retourné"},
        400: {"description": "Code expiré ou invalide"},
        401: {"description": "Code incorrect"},
        404: {"description": "Utilisateur introuvable"},
    },
    response_description="Jeton d'accès et rôles de l'utilisateur")
def verify_code(data: VerifyCodeRequest, db: Session = Depends(get_db)):
    return verify_otp_code(data.email, data.code, db)
