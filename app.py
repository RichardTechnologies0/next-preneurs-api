import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from mysql.connector import connect, Error

from mysql.connector import pooling

# Configurer un pool de connexions
dbconfig = {
    "host": "82.197.82.14",
    "user": "u119316410_richardFervel",
    "password": "@ZHj*cjYt8",
    "database": "u119316410_presence_db"
}
connection_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **dbconfig)

def get_db_connection():
    """Récupère une connexion à partir du pool."""
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Erreur lors de la récupération de la connexion : {e}")
        return None


app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin depuis le frontend

# Récupérer les données depuis la table 'post'
@app.route('/api/post', methods=['GET'])
def get_items():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM post")
        items = cursor.fetchall()
        return jsonify(items), 200
    except Error as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return jsonify({"error": "Erreur lors de l'exécution de la requête"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Ajouter une image et une description dans la base de données
@app.route('/api/send-post', methods=['POST'])
def add_item():
    data = request.json
    description = data.get('description')
    image_url = data.get('image_url')

    if not description or not image_url:
        return jsonify({"error": "La description et l'URL de l'image sont requis"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO post (content, image_url) VALUES (%s, %s)", (description, image_url))
        connection.commit()
        return jsonify({"message": "Item ajouté avec succès!"}), 200
    except Error as e:
        print(f"Erreur lors de l'ajout de l'item : {e}")
        return jsonify({"error": "Erreur lors de l'ajout de l'item"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Récupérer les utilisateurs
@app.route('/api/friends', methods=['GET'])
def get_friends():
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        return jsonify(users), 200
    except Error as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return jsonify({"error": "Erreur lors de l'exécution de la requête"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Récupérer les utilisateurs
@app.route('/api/suivi', methods=['POST'])
def suivi_friends():
    info = request.json

    # Vérifier si l'email est fourni dans les données POST
    suivi = info.get('email')
    if not suivi:
        return jsonify({"error": "Email est requis"}), 400

    # Connexion à la base de données
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        # Requête pour récupérer les amis suivis
        query = """
            SELECT * FROM friends 
            WHERE master = %s
        """
        cursor.execute(query, (suivi,))
        users = cursor.fetchall()

        # Vérifier si des utilisateurs sont trouvés
        if not users:
            return jsonify({"message": "Aucun utilisateur trouvé"}), 404

        return jsonify(users), 200
    except Error as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")
        return jsonify({"error": "Erreur lors de l'exécution de la requête"}), 500
    finally:
        # Toujours fermer la connexion
        if connection.is_connected():
            cursor.close()
            connection.close()


# Authentification de l'utilisateur (connexion)
@app.route('/api/session', methods=['POST'])
def get_session():
    info = request.json
    email = info.get('email')
    password_request = info.get('password')

    if not email or not password_request:
        return jsonify({"error": "Email et mot de passe sont requis"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            stored_password = user['password']
            if stored_password == password_request:  # Comparez les mots de passe
                return jsonify(user), 200
            else:
                return jsonify({"error": "Mot de passe incorrect"}), 401
        else:
            return jsonify({"error": "Compte introuvable"}), 404
    except Error as e:
        print(f"Erreur lors de l'authentification : {e}")
        return jsonify({"error": "Erreur interne du serveur"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Inscription d'un nouvel utilisateur
@app.route('/api/signin', methods=['POST'])
def post_session():
    info = request.json
    nom = info.get('nom')
    occupation = info.get('occupation')
    email = info.get('email')
    password = info.get('password')
    url = info.get('url')

    if not nom or not occupation or not email or not password or not url:
        return jsonify({"error": "Tous les champs sont requis"}), 400

    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (nom, occupation, email, password, url) VALUES (%s, %s, %s, %s, %s)",
            (nom, occupation, email, password, url)
        )
        connection.commit()
        return jsonify({"message": "Compte créé avec succès!"}), 200
    except Error as e:
        print(f"Erreur lors de l'inscription : {e}")
        return jsonify({"error": "Erreur lors de l'inscription"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/api/add_friends', methods=['POST'])
def add_friends():
    data = request.json
    masterEmail = data.get('email')
    suivi = data.get('key')
    nom = data.get('nom')
    occupation = data.get('occupation')
    url = data.get('url')

    # Vérification des données reçues
    if not masterEmail:
        return jsonify({"error": "L'email est requis"}), 400
    if not nom:
        return jsonify({"error": "Le nom est requis"}), 400
    if not occupation:
        return jsonify({"error": "L'occupation est requise"}), 400
    if not url:
        return jsonify({"error": "L'URL est requise"}), 400

    # Connexion à la base de données
    connection = get_db_connection()
    if connection is None:
        return jsonify({"error": "Impossible de se connecter à la base de données"}), 500

    try:
        cursor = connection.cursor()

        # Requête SQL pour insérer un ami
        cursor.execute(
            "INSERT INTO friends (master, suivi, nom, occupation, url) VALUES (%s, %s, %s, %s, %s)",
            (masterEmail, suivi, nom, occupation, url)
        )
        connection.commit()

        return jsonify({"message": "Ami ajouté avec succès!"}), 200
    except Error as e:
        print(f"Erreur lors de l'ajout de l'ami : {e}")
        return jsonify({"error": f"Erreur lors de l'ajout de l'ami : {str(e)}"}), 500
    finally:
        # Fermeture sécurisée du curseur et de la connexion
        try:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        except Exception as e:
            print(f"Erreur lors de la fermeture de la connexion : {e}")

chat_idea = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

@app.route('/api/chatAI', methods=['POST'])
def process_idea():
    data = request.json
    idea = data.get('idea')

    if not idea:
        return jsonify({"error": "Aucune idée valide n'a été fournie."}), 400

    prompt = (
        f"L'utilisateur a une idée entrepreneuriale : '{idea}'. "
        "Proposez une description claire et détaillée de cette idée. "
        "Incluez des conseils concrets pour la mettre en œuvre, comme : "
        "1. Analyse de marché\n"
        "2. Modèle économique\n"
        "3. Stratégies de marketing\n"
        "4. Étapes pour démarrer."
    )

    try:
        print(f"Traitement de l'idée : {idea}")
        response = chat_idea(prompt, max_length=200)
        prediction = response[0]["generated_text"]

        # Nettoyage de la réponse générée
        cleaned_prediction = prediction.split(".")[1] + "."  # Prend la première phrase complète
        return jsonify({"prediction": prediction})

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return jsonify({"error": f"Une erreur s'est produite : {str(e)}"}), 500


if __name__ == '__main__':
    app.run()
