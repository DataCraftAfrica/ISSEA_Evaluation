import os

class Config:
    """
    Configuration pour SQLAlchemy afin de se connecter exclusivement
    à la base PostgreSQL sur Render.
    """

    # Render fournit DATABASE_URL automatiquement
    db_url = os.environ.get("DATABASE_URL")  # utiliser la variable standard Render

    if not db_url:
        raise ValueError("⚠️ DATABASE_URL non défini sur Render !")

    # Correction si l'URL commence par postgres://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    # Ajout du sslmode si pas déjà présent
    if "sslmode" not in db_url:
        db_url += "?sslmode=require"

    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "upersecret")
