import os

class Config:
    # Récupère la variable d'environnement (Render fournit DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://issea_bd2_user:IOAodAB8qWSDTCORHSFZBDNLnK559u2z@dpg-d4bidfshg0os73evkao0-a.oregon-postgres.render.com/issea_bd2")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "upersecret")  # pour les sessions
