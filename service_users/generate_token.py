from app.security import create_access_token
from sqlalchemy.orm import Session
from app.models.user import User
from database import SessionLocal

def update_user_token():
    db: Session = SessionLocal()
    try:
        # Récupération de l'utilisateur cible
        user = db.query(User).filter(User.email == "wafaeananouch2003@gmail.com").first()
        
        if not user:
            print("Utilisateur non trouvé")
            return
        
        # Génération du token avec le bon rôle
        token = create_access_token(user.email, user.role)
        
        # Mise à jour du champ token dans la base
        user.token = token
        db.commit()
        
        print("TOKEN AJOUTÉ :", token)
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du token: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_token()