from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (JWTManager, create_access_token, jwt_required, get_jwt_identity, current_user)
import mysql.connector
from socks import method

app = Flask(__name__)
app.config['JWT_SECRET_KEY']=""
JWTManager(app)
CORS(app,supports_credentials=True)  # Pour permettre les requêtes cross-origin depuis le frontend

# Configuration de la base de données
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="reseau_social"
)
cursor = db.cursor(dictionary=True)

# Récupérer les données depuis la base de données
@app.route('/api/post', methods=['GET'])
def get_items():
    cursor.execute("SELECT * FROM post")
    items = cursor.fetchall()
    return jsonify(items)

# Ajouter une image et une description dans la base de données
@app.route('/api/send-post', methods=['POST'])
def add_item():
    data = request.json
    description = data.get('description')
    image_url = data.get('image_url')
    author=data.get('nom')

    # Ajout dans la base de données
    cursor.execute("INSERT INTO post (content, image_url,author) VALUES (%s, %s,%s)", (description, image_url,author))
    db.commit()
    return jsonify({"message": "Item ajouté avec succès!"}), 200

@app.route('/api/friends',methods=['GET'])
def get_friends():
    cursor.execute('SELECT * FROM users')
    users=cursor.fetchall()
    return jsonify(users)



@app.route('/api/session',methods=['POST'])
def get_session():
    try:
        info = request.json
        email = info.get('email')
        password_request = info.get('password')

        if not email or not password_request:
            return jsonify({"error": "Email et mot de passe sont requis"}), 400

            # Requête sécurisée avec des paramètres
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        # Vérification si l'utilisateur existe
        if user:
            stored_password = user['password']
            stored_email=user['email']
            if stored_password == password_request:  # Comparez les mots de passe

                return jsonify(user)
            else:
                return jsonify({"error": "Mot de passe incorrect"}), 401
        else:
            return jsonify({"error": "Compte introuvable"}), 404

    except Exception as e:
        return jsonify({"error": f"Une erreur est survenue : {str(e)}"}), 500
    finally:
        cursor.close()
        db.close()


@app.route('/api/signin',methods=['POST'])
def post_session():
    info=request.json
    nom=info.get('nom')
    occupation=info.get('occupation')
    email=info.get('email')
    password=info.get('password')
    url=info.get('url')

    cursor.execute("INSERT INTO users (nom,occupation,email,password,url) VALUES(%s,%s,%s,%s,%s)",(nom,occupation,email,password,url))
    db.commit()
    return jsonify("Compte Creer avec success"),200


if __name__ == '__main__':
    app.run(debug=True)
