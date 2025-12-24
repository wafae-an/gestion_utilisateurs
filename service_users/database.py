import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus
from sqlalchemy.orm import Session
from fastapi import Depends

# Charger les variables d'environnement
load_dotenv()

# --- Récupération des variables d'environnement (.env) ---
DB_USER = os.getenv("MYSQL_USER")
DB_PASSWORD = quote_plus(os.getenv("MYSQL_PASSWORD"))
DB_HOST = "mysql-service"  
DB_PORT = os.getenv("DB_PORT", "3306")  # 3306 par défaut
DB_NAME = os.getenv("MYSQL_DATABASE")

# Construction de l'URL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# --- SQLAlchemy ---
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
