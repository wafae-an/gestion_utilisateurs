from passlib.context import CryptContext

# Crée un contexte de hachage avec bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Mot de passe à hacher
plain_password = ""

# Hachage
hashed_password = pwd_context.hash(plain_password)

print("Mot de passe haché :")
print(hashed_password)
