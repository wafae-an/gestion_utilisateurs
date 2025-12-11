from sqlalchemy.orm import Session
from app.models.user import User
from app.security import verify_password
from fastapi import HTTPException
from app.send_email import send_otp_email
from random import randint
from app.redis_client import r
from datetime import timedelta

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    # Générer un code OTP à 6 chiffres
    code = str(randint(100000, 999999))

    # Stocker le code dans Redis AVANT d'essayer d'envoyer l'email
    r.setex(f"otp:{email}", timedelta(minutes=10), code)

    # Tenter d'envoyer l'email SANS bloquer si ça échoue
    try:
        send_otp_email(user.email, code)
        message = "Un code de vérification a été envoyé à votre adresse e-mail."
    except Exception as e:
        # L'email a échoué, mais on continue quand même
        print(f"\n⚠️ ═══════════════════════════════════════════════════════")
        print(f"⚠️  ERREUR D'ENVOI EMAIL: {e}")
        print(f"🔐  CODE OTP POUR {email}: {code}")
        print(f"⚠️ ═══════════════════════════════════════════════════════\n")
        message = "Code de vérification généré (consultez la console du serveur)"

    # ✅ IMPORTANT : On retourne toujours une réponse, même si l'email échoue
    return {
        "message": message,
        "email": user.email
    }