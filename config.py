import os

class Config:
    # Render fournit DATABASE_URL automatiquement
    db_url = os.environ.get("DATABASE_URL2")  # Render définit DATABASE_URL
    if db_url and db_url.startswith("postgres://"):
        # Correction obligatoire pour SQLAlchemy
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    # Ajout du SSL si pas déjà présent
    if db_url and "sslmode" not in db_url:
        db_url += "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = db_url or "sqlite:///local.db"  # fallback local
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "upersecret")