import json
from pymongo import MongoClient
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

mongo = MongoClient('localhost', 27017)
main_db = mongo['lbec2024']

users = main_db['users']
consumption_data = main_db['consumption_data']

app.config["JWT_SECRET_KEY"] = "do-not-want-to-change"
jwt = JWTManager(app)

@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token 
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    # Check if all fields are present
    if not name or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    # Check if user already exists
    existing_user = users.find_one({'email': email})
    if existing_user:
        return jsonify({'error': 'User already exists'}), 400

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create a new user and save it to the database
    new_user = {
        'name': name,
        'email': email,
        'hashed_password': hashed_password,
        'prefered_temperature': -1000
    }
    users.insert_one(new_user)

    access_token = create_access_token(identity=email)

    return jsonify({"status": "success", 'message': 'User registered successfully', "token": access_token}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = users.find_one({'email': email})

    print(user)
    if not user or not check_password_hash(user['hashed_password'], password):
        return jsonify({'status': "failed", 'message': 'Invalid email or password'})

    access_token = create_access_token(identity=email)

    return jsonify({"status": "success", 'token': access_token}), 200


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route('/profile')
@jwt_required()
def my_profile():

    # get the user's email from the token
    email = get_jwt_identity()
    
    # get the user from the database
    user = users.find_one({'email': email})

    return jsonify({"status": "success", "data": str(user)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)