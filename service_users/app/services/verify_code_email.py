from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.redis_client import r
import json

def verify_otp_code(email: str, code: str, db: Session):
    key = f"otp:{email}"
    stored_code = r.get(key)

    if not stored_code:
        raise HTTPException(status_code=400, detail="Code expiré ou invalide")

    if  stored_code != code:

        raise HTTPException(status_code=401, detail="Code incorrect")

    # Supprimer le code après vérification pour qu'il ne soit pas réutilisé
    r.delete(key)

    # Récupérer l'utilisateur et son token
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    

    return {
        "token": user.token,   # supposé déjà généré/storé
         "role":user.role,
         "user_id":user.id,    
    }
