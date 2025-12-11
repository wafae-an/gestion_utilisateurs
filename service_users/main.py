from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from app.api import login, resend_otp, verify_otp, sign_up,create_conducteur,view_users
from dotenv import load_dotenv
import os


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "hello world"}

# ✅ Crée toutes les tables déclarées dans Base
Base.metadata.create_all(bind=engine)

# ✅ Autoriser les requêtes venant du front (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:3001",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(login.router)
app.include_router(verify_otp.router)
app.include_router(resend_otp.router)
app.include_router(sign_up.router)
app.include_router(create_conducteur.router)
app.include_router(view_users.router)