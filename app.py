from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory,  jsonify, send_file, session, make_response, current_app
#from flask_mysqldb import MySQL
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
import psycopg2
import random
import string
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import check_password_hash, generate_password_hash
# models.py
from flask_sqlalchemy import SQLAlchemy
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pandas as pd
from werkzeug.security import generate_password_hash
from config import Config
from models import db, Etudiant
import os
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import resend
import io
import numpy as np
from wordcloud import WordCloud
from io import BytesIO
import json
import base64
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


###
### Bibliotheque

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config.from_object(Config)
resend.api_key = os.getenv("RESEND_API_KEY")

# Charger l'URL de Render

db.init_app(app)

#with app.app_context():
#    db.create_all()


# Configuration du serveur mail

# MAIL CONFIG FROM ENV
#app.config['MAIL_SERVER'] = os.environ.get("MAIL_SERVER")
#app.config['MAIL_PORT'] = int(os.environ.get("MAIL_PORT", 587))
#app.config['MAIL_USE_TLS'] = os.environ.get("MAIL_USE_TLS", "True") == "True"
#app.config['MAIL_USERNAME'] = os.environ.get("MAIL_USERNAME")
#app.config['MAIL_PASSWORD'] = os.environ.get("MAIL_PASSWORD")


#mail = Mail(app)

classes = ['LGTSD', 'L2BD', 'MAP1', 'M2SA', 'MDSMS1']


# Connexion Google Sheets
def get_gsheet_enseignement():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    
    # 🔑 récupérer le JSON depuis l'env
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(base64.b64decode(creds_json))  

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ⚠️ on ouvre le fichier Google Sheets datacraft-africa@soutenance-472701.iam.gserviceaccount.com
    spreadsheet = client.open_by_key("1VmglR-mt57Lox-yicoIxBwvCaPPu5wvL5Eh1Qf6jVXU")
    return spreadsheet


def get_gsheet_eva_enseignant():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    
    # 🔑 récupérer le JSON depuis l'env
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(base64.b64decode(creds_json))  

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ⚠️ on ouvre le fichier Google Sheets 
    spreadsheet = client.open_by_key("1T_RnPgl9DAgQRiL_P-b4WB3a96FqUB7vgHvksevMDPM")
    return spreadsheet


def get_gsheet_eva_enseignement():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    
    # 🔑 récupérer le JSON depuis l'env
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    creds_dict = json.loads(base64.b64decode(creds_json))  

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    
    # ⚠️ on ouvre le fichier Google Sheets 
    spreadsheet = client.open_by_key("1m-eYggFz6n7mvpG8JgHMf_Wqa6ZWHRscQ-iOX1VJ6CE")
    return spreadsheet


def send_email(dest, subject, body):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.environ.get("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": "appsrf42@gmail.com", "name": "DataCraft AFRICA"},
        to=[{"email": dest}],
        subject=subject,
        text_content=body,
    )

    try:
        api_instance.send_transac_email(email)
        print("📧 Email envoyé avec succès")
    except ApiException as e:
        print(f"❌ Erreur envoi mail : {e}")



# 🔑 Fonction pour générer un mot de passe aléatoire
def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def shuffle_string(s):
    # Convertir la chaîne en liste de caractères
    char_list = list(s)
    # Mélanger la liste de caractères
    random.shuffle(char_list)
    # Convertir la liste mélangée de retour en chaîne
    shuffled_string = ''.join(char_list)
    return shuffled_string


def update_etudiant(worksheet, worksheet2, email, nom_enseignant, infos1, infos2):
    """
    Met à jour les infos d'un étudiant dans la Google Sheet
    en se basant sur deux colonnes :
        - Email
        - Nom_enseignant
    
    :param worksheet: feuille Google Sheet (gspread)
    :param email: email de l'étudiant (string)
    :param nom_enseignant: nom de l'enseignant associé (string)
    :param infos: dictionnaire des nouvelles infos
    """

    # Récupérer toutes les données 
    data = worksheet.get_all_values()
    headers = data[0]

    # Récupérer toutes les données 
    data2 = worksheet2.get_all_values()
    headers2 = data2[0]

    # Vérifier que les colonnes existent
    if "Mail" not in headers or "Nom_enseignant" not in headers:
        print("❌ Colonnes mail ou Nom_enseignant introuvables dans la feuille.")
        return False

    email_col = headers.index("Mail")
    nom_col = headers.index("Nom_enseignant")

    email_col2 = headers2.index("Mail")
    nom_col2 = headers2.index("Nom_enseignant")

    row_index = None
    row_index2 = None

    # Parcourir toutes les lignes pour trouver une ligne qui match email + nom_enseignant
    for i, row in enumerate(data[1:], start=2):  # start=2 car ligne 1 = headers
        if (len(row) > max(email_col, nom_col) and 
            row[email_col] == email and 
            row[nom_col] == nom_enseignant):
            row_index = i
            break

    for i, row in enumerate(data2[1:], start=2):  # start=2 car ligne 1 = headers
        if (len(row) > max(email_col2, nom_col2) and 
            row[email_col2] == email and 
            row[nom_col2] == nom_enseignant):
            row_index2 = i
            break

    if not row_index:
        print("❌ Aucune ligne trouvée correspondant à cet mail + enseignant.")
        return False
    
    if not row_index2:
        print("❌ Aucune ligne trouvée correspondant à cet mail + enseignant.")
        return False

    # Construire la nouvelle ligne
    updated_row = []
    for col in headers:
        if col == "Mail":
            updated_row.append(email)
        elif col == "Nom_enseignant":
            updated_row.append(nom_enseignant)
        else:
            updated_row.append(infos1.get(col, ""))

    
    updated_row2 = []
    for col in headers2:
        if col == "Mail":
            updated_row2.append(email)
        elif col == "Nom_enseignant":
            updated_row2.append(nom_enseignant)
        else:
            updated_row2.append(infos2.get(col, ""))

    # Mettre à jour
    last_col_letter = chr(64 + len(headers))
    worksheet.update(f"A{row_index}:{last_col_letter}{row_index}", [updated_row])

    last_col_letter2 = chr(64 + len(headers2))
    worksheet2.update(f"A{row_index2}:{last_col_letter2}{row_index2}", [updated_row2])


    print(f"✔️ Ligne mise à jour pour {email} (enseignant: {nom_enseignant})")
    return True



@app.route('/', methods=['GET', 'POST'])
def connexion():


    return render_template('index.html')

@app.route('/enregistrement/<enseignant>', methods=['GET', 'POST'])
def enregistrement(enseignant):

    if 'username' not in session:
        return redirect(url_for('login'))

    # ----- PARTIE GET -----
    if request.method == "GET":

        spreadsheet2 = get_gsheet_eva_enseignant()
        spreadsheet1 = get_gsheet_eva_enseignement()
        spreadsheet = get_gsheet_enseignement()

        worksheet = spreadsheet.worksheet(session["user_info"]["classe"])
        data = worksheet.get_all_values()

        df = pd.DataFrame(data[1:], columns=data[0])
        result = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

        return render_template(
            'notes.html',
            username=session["user_info"]["nom"],
            enseignant=enseignant,
            data=result
        )

    # ----- PARTIE POST -----
    if request.method == "POST":

        spreadsheet2 = get_gsheet_eva_enseignant()
        spreadsheet1 = get_gsheet_eva_enseignement()
        spreadsheet = get_gsheet_enseignement()

        worksheet1 = spreadsheet1.worksheet(session["user_info"]["classe"])
        worksheet2 = spreadsheet2.worksheet(session["user_info"]["classe"])
        worksheet = spreadsheet.worksheet(session["user_info"]["classe"])

        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])
        result = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

        mail = session["username"]

        # Récupération SÉCURISÉE
        enseignement = request.form.get("enseignement")
        objectifs_cours = request.form.get("objectifs_cours")
        contenu_cours = request.form.get("contenu_cours")
        taux_couverture = request.form.get("taux_couverture")
        Connaissances_theoriques = request.form.get("Connaissances_theoriques")
        Connaissances_pratiques = request.form.get("Connaissances_pratiques")
        Conformite_evaluations = request.form.get("Conformite_evaluations")
        Rapport_duree = request.form.get("Rapport_duree")

        assiduite = request.form.get("assiduite")
        ponctualite = request.form.get("ponctualite")
        tenue_vestimentaire = request.form.get("tenue_vestimentaire")
        utilisation_materiels = request.form.get("utilisation_materiels")
        disponibilite_ecouter = request.form.get("disponibilite_ecouter")
        maitrise_salle = request.form.get("maitrise_salle")
        interaction = request.form.get("interaction")
        integration = request.form.get("integration")
        Organisation_suivi = request.form.get("Organisation_suivi")
        capacite_transmission = request.form.get("capacite_transmission")

        aspects_positifs = request.form.get("aspects_positifs")
        aspects_negatifs = request.form.get("aspects_negatifs")
        suggestion = request.form.get("suggestion")

        action = request.form.get("action")

        if action == "Enregistrer":

            worksheet1.append_row([
                mail, enseignant, enseignement, objectifs_cours,
                contenu_cours, taux_couverture, Connaissances_theoriques,
                Connaissances_pratiques, Conformite_evaluations,
                Rapport_duree
            ])

            worksheet2.append_row([
                mail, enseignant, assiduite, ponctualite, tenue_vestimentaire,
                utilisation_materiels, disponibilite_ecouter, maitrise_salle,
                interaction, integration, Organisation_suivi,
                capacite_transmission, aspects_positifs, aspects_negatifs,
                suggestion
            ])

            flash("Vos informations ont été enregistrées avec succès 🎉", "success")

        if action == 'Modifier':

            infos1 = {
                'Mail': mail,
                'Nom_enseignant': enseignant,
                'satisfait_enseignement': enseignement,
                'Enoncé_objectifs_cours': objectifs_cours,
                'Contenu_cours': contenu_cours,
                'Taux_couverture_programme': taux_couverture,
                'Connaissances_théoriques_acquises': Connaissances_theoriques,
                'Connaisssances_pratiques': Connaissances_pratiques,
                'Conformité des évaluations aux contenus': Conformite_evaluations,
                'Rapport_durée_contenu': Rapport_duree
            }

            infos2 = {
                'Mail': mail,
                'Nom_enseignant': enseignant,
                'Assiduité': assiduite,
                'Ponctualité': ponctualite,
                'Tenue_vestimentaire': tenue_vestimentaire,
                'Utilisation_outils_matériels_didactiques': utilisation_materiels,
                'Disponibilité_ecoute': disponibilite_ecouter,
                'Maîtrise_salle': maitrise_salle,
                'Interaction_enseignants-etudiants': interaction,
                'Integration_TICs': integration,
                'Organisation_suivi_TP_TPE_TD': Organisation_suivi,
                'Capacité_transmission': capacite_transmission,
                'Aspects_positifs': aspects_positifs,
                'Aspects_négatifs': aspects_negatifs,
                'Suggestions': suggestion
            }

            # Mettre à jour la ligne
            update_etudiant(worksheet1, worksheet2, mail, enseignant, infos1, infos2)

        return render_template('notes.html', username = session["user_info"]["nom"], data=result, adresse=session["username"])



@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == "POST":

        email = request.form["email"]
        mpd = request.form["mpd"]

        # Vérifier si l'utilisateur existe
        etu = Etudiant.query.filter_by(email=email).first()

        if etu:
            # Vérification du mot de passe haché
            if check_password_hash(etu.mpd, mpd):
                # Création de la session
                session["username"] = etu.email  

                # Stockage des infos dans un dictionnaire
                user_info = {
                    "email": etu.email,
                    "nom": etu.nom,
                    "sexe": etu.sexe,
                    "classe": etu.classe
                }
                session["user_info"] = user_info

                flash("Connexion réussie ✅", "success")
                print('la boite: ', session["user_info"]["classe"])

                if session["user_info"]["classe"] != 'super@user':
                
                        return redirect(url_for('register', Etudiant= session["username"]))
                
                elif session["user_info"]["classe"] == 'super@user':

                    return redirect(url_for('statistique'))  # Redirige vers une page tableau de bord
            else:
                flash("Mot de passe incorrect ❌", "danger")
        else:
            flash("Adresse email introuvable ❌", "danger")

    return render_template('login.html')


@app.route('/inscription', methods=['GET', 'POST'])
def inscription():

    if request.method == "POST":
        nom = request.form["nom"]
        sexe = request.form["sexe"]
        classe = request.form["classe"]
        email = request.form["email"]

        # Générer mot de passe aléatoire
        plain_password = generate_random_password(10)
        hashed_password = generate_password_hash(plain_password)

        # Créer un nouvel étudiant
        new_student = Etudiant(
            email=email,
            nom=nom,
            sexe=sexe,
            classe=classe,
            mpd=hashed_password
        )

        try:
            db.session.add(new_student)
            db.session.commit()
            print(f"✅ Étudiant ajouté : {nom}, Mot de passe = {plain_password}")

            # Sujet + contenu du mail
            subject = "Validation de compte !"
            body = f"""
Bonjour {nom},

Votre compte DataCraft AFRICA a été créé avec succès.

Votre mot de passe est : {plain_password}

Cordialement,
DataCraft AFRICA — Le progrès n'attend pas
"""

            # ------------ 📩 Envoi du mail via RESEND ----------------
            try:
                resend.Emails.send({
                    "from": "DataCraft AFRICA <no-reply@datacraft.africa>",
                    "to": [email],
                    "subject": subject,
                    "text": body
                })

                print("📨 Mail envoyé via Resend")

            except Exception as mail_err:
                print(f"❌ Erreur Resend : {mail_err}")
                flash(f"Compte créé, mais erreur d'envoi mail. Mot de passe = {plain_password}", "warning")
                return redirect(url_for("login"))
            # ----------------------------------------------------------

            flash("Compte créé avec succès ! Vérifiez votre boîte mail.", "success")
            return redirect(url_for("login"))

        except Exception as db_err:
            db.session.rollback()
            print(f"❌ Erreur SQL : {db_err}")
            flash("Erreur lors de l'inscription.", "danger")

    return render_template('inscription.html', classe=classes)



@app.route('/register/<Etudiant>', methods=['GET', 'POST'])
def register(Etudiant):

    # Sécurité : empêcher un "super@user" de passer ici
    if session["user_info"]["classe"] == "super@user":
        return redirect(url_for("statistique"))

    if 'username' in session:


        spreadsheet = get_gsheet_enseignement()
        
        print('la classe: ', session["user_info"]["classe"])

        # Choisir l’onglet en fonction de la classe (ex: "ClasseA", "ClasseB")
        worksheet = spreadsheet.worksheet(session["user_info"]["classe"])
        

        # Récupérer toutes les lignes sous forme de dictionnaires
        data = worksheet.get_all_values()
        

        df = pd.DataFrame(data[1:], columns=data[0])  
        print("Colonnes dispo dans df:", df.columns)
        #df = df[df['Email'] == session["user_info"]["email"]]

        matiere = list(df['Matiere'])
        result = dict(zip(df.iloc[:, 0], df.iloc[:, 1]))

        

        return render_template('notes.html', username = session["user_info"]["nom"], data=result, adresse=session["username"])
    
    redirect(url_for('connexion'))



@app.route('/statistique', methods=['GET', 'POST'])
def statistique():

    # Sécurité : empêcher un "super@user" de passer ici
    if 'username' in session and session["user_info"]["classe"] == 'super@user':

        return render_template('statistique.html', classes=classes)
    
    return redirect(url_for('login'))



@app.route('/logout')

def logout():

    session.pop('loggin', None)
    session.pop('id', None)
    session.pop('username', None)


    return redirect(url_for('connexion'))


def generate_random_number2(lower_bound=1000, upper_bound=8000, nom = 'vide'):

    var_date = datetime.now()
            # Récupérer uniquement l'année
    annee = var_date.year
    # Générer un nombre aléatoire dans la plage spécifiée
    valeur = random.randint(lower_bound, upper_bound)

    an = str(annee)
    annees = an[1:]

    mon_nom = nom.upper() +str(valeur)

    mat = shuffle_string(mon_nom)

    matricule = mat[0:5]  + annees

    return matricule




@app.route('/gestion_note', methods=['POST', 'GET'])
def gestion_note():

    if 'username' in session:

        if request.method == 'POST':

            prof = request.form['classe']

            spreadsheet1 = get_gsheet_eva_enseignement()
            worksheet1 = spreadsheet1.worksheet(session["user_info"]["classe"])
            data = worksheet1.get_all_values()

            df = pd.DataFrame(data[1:], columns=data[0])
            df2 = df[(df['Mail'] == session["user_info"]["email"]) & (df['Nom_enseignant'] == prof)]

            if df2.empty:
                modif = False
            else:
                modif = True

        return render_template('index2.html', data=classes, username=session['username'], enseignant=prof, action=modif)

    return redirect(url_for('login'))


def fetch_combined_data(classe):

    # ------------------------
    # 1) Récupération étudiants Postgres
    # ------------------------
    etudiants = Etudiant.query.filter_by(classe=classe).all()

    rows = [{
        "Mail": e.email,
        "Nom&Prenoms": e.nom,
        "Sexe": e.sexe,
        "Classe": e.classe,
        "mpd": e.mpd
    } for e in etudiants]

    df1 = pd.DataFrame(rows)

    # Si df1 est vide : on crée un DF vide propre
    if df1.empty:
        df1 = pd.DataFrame(columns=["Mail", "Nom&Prenoms", "Sexe", "Classe"])

    else:
        df1 = df1[["Mail", "Nom&Prenoms", "Sexe", "Classe"]]

    # ------------------------
    # 2) Récupération Google Sheets
    # ------------------------
    try:
        spreadsheet1 = get_gsheet_eva_enseignement()
        spreadsheet2 = get_gsheet_eva_enseignant()

        try:
            worksheet1 = spreadsheet1.worksheet(classe)
            data1 = worksheet1.get_all_values()

            worksheet2 = spreadsheet2.worksheet(classe)
            data2 = worksheet2.get_all_values()

            # Feuilles vides ?
            if len(data1) < 2 or len(data2) < 2:
                return pd.DataFrame()  # base vide

            df = pd.DataFrame(data1[1:], columns=data1[0])
            df2 = pd.DataFrame(data2[1:], columns=data2[0])

            # Sécurité : colonnes obligatoires
            if "Mail" not in df.columns or "Nom_enseignant" not in df2.columns:
                return pd.DataFrame()

            # Merge 1 : ajouter sexe / classe aux évaluations
            df = df.merge(df1, on="Mail", how="left")

            # Merge 2 : notes profs
            data = df.merge(df2,
                on=["Mail", "Nom_enseignant"],
                how="left"
            )

        except Exception:
            # Si un onglet n'existe pas → DF vide
            return pd.DataFrame()

    except Exception:
        current_app.logger.exception("Erreur connexion Google Sheet")
        return pd.DataFrame()

    return data if isinstance(data, pd.DataFrame) else pd.DataFrame()



@app.route('/admin/clear_etudiants/<token>')
def clear_etudiants(token):

    SECRET_TOKEN = "0099_SYLAR"  # Mets un token fort et temporaire

    if token != SECRET_TOKEN:
        return "⛔ Accès refusé", 403

    try:
        num_rows_deleted = db.session.query(Etudiant).delete()
        db.session.commit()
        return f"✅ Table vidée ! {num_rows_deleted} lignes supprimées."
    except Exception as e:
        db.session.rollback()
        return f"❌ Erreur : {e}", 500



@app.route('/admin/modifier_classe/email=<email>&classe=<nouvelle_classe>&token=<token>')
def modifier_classe(email, nouvelle_classe, token):

    SECRET_TOKEN = "0099_SYLAR"  # même système de sécurité

    # Vérification du token
    if token != SECRET_TOKEN:
        return "⛔ Accès refusé", 403

    try:
        # Chercher l'étudiant
        etu = Etudiant.query.filter_by(email=email).first()

        if not etu:
            return f"❌ Aucun étudiant trouvé avec l'email : {email}", 404

        ancienne_classe = etu.classe
        etu.classe = nouvelle_classe

        db.session.commit()

        return f"✅ Classe modifiée avec succès ! {email} est passé de {ancienne_classe} ➝ {nouvelle_classe}"

    except Exception as e:
        db.session.rollback()
        return f"❌ Erreur : {e}", 500



# ['LGTSD', 'L2BD', 'MAP1', 'M2SA', 'MDSMS1']
@app.route('/update_graph', methods=['POST'])
def update_graph():

    data = request.get_json()
    classe = data.get("classe")

    effectif = {
        'LGTSD': 20,
        'L2BD': 10,
        'M2SA': 7,
        'MAP1': 4,
        'MDSMS1': 19
    }

    # Charger matières depuis Google sheet
    try:
        spreadsheet = get_gsheet_enseignement()
        worksheet = spreadsheet.worksheet(classe)
        mat = worksheet.get_all_values()
        df_mat = pd.DataFrame(mat[1:], columns=mat[0])
        matiere = list(df_mat["Matiere"])
    except Exception:
        matiere = []

    # Charger base combinée
    base = fetch_combined_data(classe)
    df_evals = base.groupby("Nom&Prenoms").size().reset_index(name="nb_evaluations")

    # Convertir en dictionnaire pour JS
    evals_list = df_evals.to_dict(orient="records")
  

    # -------------------
    # COMPUTATIONS
    # -------------------
    if base.empty:
        ma_classe = 0
        classe_homme = 0
        classe_femme = 0
        total_matiere = len(matiere)
    else:
        base = base.fillna("")
        ma_classe = base["Mail"].nunique()
        total_matiere = len(matiere)

        classe_homme = len(base[base["Sexe"] == "M"])
        classe_femme = len(base[base["Sexe"] == "F"])

    response = {
        "total": effectif.get(classe, 0),
        "total_classe": ma_classe,
        "total_femme": classe_femme,
        "total_homme": classe_homme,
        "evaluations": evals_list
    }

    return jsonify(response)


def plot_score_global(df):
    # Convertir les réponses en scores
    mapping = {
        "Mauvais": 1,
        "Moyen": 2,
        "Satisfaisant": 3,
        "Très satisfaisant": 4
    }

    criteria_cols = df.columns[2:-2]  # colonnes des critères
    
    df_numeric = df.copy()
    for col in criteria_cols:
        df_numeric[col] = df_numeric[col].map(mapping)

    score_global = df_numeric.groupby("Nom_enseignant")[criteria_cols].mean().mean(axis=1)

    plt.figure(figsize=(10, 5))
    score_global.plot(kind="bar")
    plt.title("Score global moyen par enseignant")
    plt.ylabel("Score (sur 4)")
    plt.tight_layout()

    # Convert to base64 for Flask
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return img


def plot_radar(df):
    mapping = {"Mauvais":1,"Moyen":2,"Satisfaisant":3,"Très satisfaisant":4}
    criteria_cols = df.columns[2:-2]

    df_num = df.copy()
    for col in criteria_cols:
        df_num[col] = df_num[col].map(mapping)

    mean_scores = df_num[criteria_cols].mean().values

    angles = np.linspace(0, 2*np.pi, len(criteria_cols), endpoint=False)
    mean_scores = np.concatenate((mean_scores, [mean_scores[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, mean_scores, linewidth=2)
    ax.fill(angles, mean_scores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria_cols)
    ax.set_title("Répartition moyenne des évaluations par critère")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img

def plot_distribution_par_critere_enseignement(df):
    criteria_cols = df[['satisfait_enseignement', 'Enoncé_objectifs_cours', 'Contenu_cours', 'Taux_couverture_programme', 'Connaissances_théoriques_acquises', 'Connaisssances_pratiques', 'Conformité des évaluations aux contenus','Rapport_durée_contenu']]
    valeurs = ["Mauvais", "Moyen", "Satisfaisant", "Très satisfaisant"]

    counts = {}
    for col in criteria_cols:
        counts[col] = df[col].value_counts().reindex(valeurs, fill_value=0)

    result = pd.DataFrame(counts)

    plt.figure(figsize=(12, 6))
    result.T.plot(kind="bar", figsize=(12,6))
    plt.title("Distribution des évaluations par critère")
    plt.ylabel("Nombre d'évaluations")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img


def plot_distribution_par_critere_enseignant(df):
    criteria_cols = df[['Assiduité', 'Ponctualité', 'Tenue_vestimentaire', 'Disponibilité_ecoute', 'Maîtrise_salle', 'Interaction_enseignants-etudiants', 'Integration_TICs', 'Organisation_suivi_TP_TPE_TD', 'Capacité_transmission']]
    valeurs = ["Mauvais", "Moyen", "Satisfaisant", "Très satisfaisant"]

    counts = {}
    for col in criteria_cols:
        counts[col] = df[col].value_counts().reindex(valeurs, fill_value=0)

    result = pd.DataFrame(counts)

    plt.figure(figsize=(12, 6))
    result.T.plot(kind="bar", figsize=(12,6))
    plt.title("Distribution des évaluations par critère")
    plt.ylabel("Nombre d'évaluations")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img

def plot_wordcloud(df):
    text = " ".join(df["Aspects_positifs"].astype(str).tolist() + 
                    df["Aspects_négatifs"].astype(str).tolist())

    wc = WordCloud(background_color="white", width=1000, height=600).generate(text)

    plt.figure(figsize=(10, 6))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    img = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    return img

@app.post("/load_matieres")
def load_matieres():
    classe = request.form["classe"]

    spreadsheet = get_gsheet_enseignement()
    worksheet = spreadsheet.worksheet(classe)
    data = worksheet.get_all_values()

    # Supposons que la 2e colonne = Nom_enseignant ou Matière
    matieres = [row[1] for row in data[1:] if row[1]]

    return { "matieres": matieres }


@app.route("/update_dashboard", methods=["POST"])
def update_dashboard():
    classe = request.form.get("classe")
    enseignant = request.form.get("enseignant")

    base = fetch_combined_data(classe)

    if base.empty:
        return {
            "score": "",
            "critere": "",
            "wordcloud": ""
        }

    if "Nom_enseignant" not in base.columns:
        return {
            "score": "",
            "critere": "",
            "wordcloud": ""
        }

    df_filtre = base[base["Nom_enseignant"] == enseignant]

    if df_filtre.empty:
        return {
            "score": "",
            "critere": "",
            "wordcloud": ""
        }

    return {
        "score": plot_distribution_par_critere_enseignant(df_filtre),
        "critere": plot_distribution_par_critere_enseignement(df_filtre),
        "wordcloud": plot_wordcloud(df_filtre)
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
