# create_tables.py

from app import app, db

# Importer tous les modèles pour que SQLAlchemy les détecte
from models import Etudiant   # ajoute ici d’autres modèles si tu en as

with app.app_context():
    print("👉 Création des tables dans la base de données...")
    db.create_all()
    print("✅ Tables créées avec succès !")
