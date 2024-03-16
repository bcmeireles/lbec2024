from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

mongo = MongoClient('localhost', 27017)
main_db = mongo['lbec2024']

users = main_db['users']

# Set a secret key for generating JWT tokens
app.config['SECRET_KEY'] = 'your_secret_key_here'

# User registration route
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
        'hashed_password': hashed_password
    }
    users.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # Check if all fields are present
    if not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    # Check if user exists
    user = users.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Check if password is correct
    if not check_password_hash(user['hashed_password'], password):
        return jsonify({'error': 'Invalid password'}), 401

    # Generate a JWT token for the authenticated user
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'])

    return jsonify({'token': token}), 200

# Protected route example
@app.route('/protected', methods=['GET'])
def protected():
    # Get the token from the request headers
    token = request.headers.get('Authorization')

    try:
        # Decode the token and get the user ID
        user_id = jwt.decode(token, app.config['SECRET_KEY'])['user_id']

        # Get the user from the database
        user = users.find_one({'_id': ObjectId(user_id)})

        # Return user information
        return jsonify({
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email']
        }), 200
    except:
        # Return an error if the token is invalid or expired
        return jsonify({'error': 'Invalid or expired token'}), 401
if __name__ == "__main__":
    app.run(debug=True)
