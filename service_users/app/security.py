from datetime import datetime, timedelta
from typing import Union
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models.user import UserRole  # Importez votre enum

# === Configuration ===
SECRET_KEY = "votre_clé_très_secrète"
ALGORITHM = "HS256"

# === Password hashing ===
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Empêcher erreur bcrypt (> 72 caractères)
    if len(plain_password) > 72:
        return False
    return pwd_context.verify(plain_password, hashed_password)

# === JWT Token generation ===
def create_access_token(user_email: str, role: UserRole, expires_delta: Union[timedelta, None] = None) -> str:
    expire = datetime.utcnow() + (expires_delta or timedelta(days=60))
    
    # Convertir l'enum en string pour la sérialisation JSON
    role_str = role.value if isinstance(role, UserRole) else str(role)
    
    to_encode = {
        "sub": user_email,
        "role": role_str,  # Maintenant un string sérialisable
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# === JWT Token decoding ===
def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Token invalide ou expiré")

# === Récupérer l'utilisateur courant ===
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        print(f"Token reçu dans get_current_user : {token}")
        payload = decode_access_token(token)
        user_email: str = payload.get("sub")
        role_str: str = payload.get("role")  # Récupère le string du rôle

        if user_email is None or role_str is None:
            raise HTTPException(status_code=401, detail="Token invalide")

        # Convertir le string en enum UserRole si nécessaire
        try:
            role = UserRole(role_str)
        except ValueError:
            # Si la valeur ne correspond pas à l'enum, utiliser PASSAGER par défaut
            role = UserRole.PASSAGER

        return {"email": user_email, "role": role}

    except ValueError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

def get_current_user_email(user: dict = Depends(get_current_user)) -> str:
    return user["email"]

# === Fonctions utilitaires pour vérifier les rôles ===
def require_role(required_role: UserRole):
    """Dependency pour vérifier un rôle spécifique"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] != required_role:
            raise HTTPException(
                status_code=403, 
                detail=f"Accès refusé. Rôle {required_role.value} requis."
            )
        return current_user
    return role_checker

def require_any_role(allowed_roles: list[UserRole]):
    """Dependency pour vérifier plusieurs rôles possibles"""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            allowed_roles_str = ", ".join([role.value for role in allowed_roles])
            raise HTTPException(
                status_code=403, 
                detail=f"Accès refusé. Rôles autorisés: {allowed_roles_str}"
            )
        return current_user
    return role_checker

# Fonction utilitaire pour convertir un string en UserRole
def get_user_role_from_string(role_str: str) -> UserRole:
    """Convertit un string en enum UserRole"""
    try:
        return UserRole(role_str.upper())
    except ValueError:
        return UserRole.PASSAGER  # Valeur par défaut