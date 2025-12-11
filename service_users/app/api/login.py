from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from app.services.login_service import authenticate_user  

router = APIRouter()

@router.post("/login",summary="Initier la connexion (étape 1/2) avec OTP e-mail",
    description=(
        "Vérifie l'e-mail et le mot de passe, génère un OTP de 6 chiffres, "
        "l'envoie par e-mail et le stocke temporairement (5 minutes) pour la vérification. "
        "Étape suivante : **/auth/verify-otp** pour valider le code et finaliser la connexion."
    ),
    
    responses={
        200: {"description": "OTP envoyé par e-mail"},
        401: {"description": "Identifiants invalides"},
        429: {"description": "Trop de tentatives (rate limit)"},
        500: {"description": "Erreur lors de l'envoi d'e-mail"},
    },
    response_description="Confirmation d'envoi de l'OTP")
async def login(request: Request):
    data = await request.json()
    print("Reçu du frontend :", data)

    email = data.get("email")
    password = data.get("password")

    db: Session = SessionLocal()
    return authenticate_user(email, password, db)
