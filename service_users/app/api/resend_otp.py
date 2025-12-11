from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from app.services.resend_otp_service import resend_otp_code

router = APIRouter()

class ResendRequest(BaseModel):
    email: str

@router.post("/resend_code",summary="Réenvoyer un code OTP",
    description=(
        "Génère un **nouveau code OTP** (6 chiffres), le **stocke 5 minutes** dans Redis, "
        "puis l'**envoie par e-mail** à l'utilisateur correspondant."
    ),
   
    responses={
        200: {"description": "Nouveau code OTP généré et envoyé"},
        404: {"description": "Utilisateur introuvable"},
        500: {"description": "Erreur lors de l'envoi d'e-mail (si levée par le service d'envoi)"},
    },
    response_description="Confirmation d'envoi du nouveau code")
def resend_code(data: ResendRequest, db: Session = Depends(get_db)):
    return resend_otp_code(data.email, db)
