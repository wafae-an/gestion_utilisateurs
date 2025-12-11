from sqlalchemy.orm import Session
from app.models.user import User
from app.send_email import send_otp_email
from app.redis_client import r
from random import randint
from datetime import timedelta
from fastapi import HTTPException

def resend_otp_code(email: str, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Génération d'un nouveau code
    code = str(randint(100000, 999999))

    # Stocker dans Redis avec expiration 5 min
    r.setex(f"otp:{email}", timedelta(minutes=5), code)

    # Envoyer par email
    send_otp_email(email, code)

    return {"message": "Nouveau code envoyé avec succès"}
