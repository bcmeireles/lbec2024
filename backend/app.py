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
calendar_data = main_db['calendar_data']

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
        'gas_price': 0,
        'electricity_price': 0,
        'water_price': 0,
        'min_house_temp': 0,
        'max_house_temp': 0,
        'enable_notifications': False,
        'notifications_default_timing': 0
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
        return jsonify({'success': False, 'status': "failed", 'message': 'Invalid email or password'})

    access_token = create_access_token(identity=email)

    return jsonify({"success": True, "status": "success", 'token': access_token}), 200


@app.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route("/profile", methods=["GET"])
@jwt_required()
def my_profile():

    # get the user's email from the token
    email = get_jwt_identity()
    
    # get the user from the database
    user = users.find_one({'email': email})
    user['_id'] = str(user['_id'])

    return jsonify({"status": "success", "data": user})

@app.route("/settings", methods=["GET"])
@jwt_required()
def get_settings():
    email = get_jwt_identity()
    user = users.find_one({'email': email})
    return jsonify({"success": True, "status": "success", "data": {
        "gas_price": user['gas_price'],
        "electricity_price": user['electricity_price'],
        "water_price": user['water_price'],
        "min_house_temp": user['min_house_temp'],
        "max_house_temp": user['max_house_temp'],
        "enable_notifications": user['enable_notifications'],
        "notifications_default_timing": user['notifications_default_timing']
    }})

@app.route("/settings", methods=["POST"])
@jwt_required()
def update_settings():
    email = get_jwt_identity()
    user = users.find_one({'email': email})
    data = request.get_json()
    user['gas_price'] = data['gas']
    user['electricity_price'] = data['electricity']
    user['water_price'] = data['water']
    user['min_house_temp'] = data['minTemp']
    user['max_house_temp'] = data['maxTemp']
    user['enable_notifications'] = data['receiveNotifications']
    user['notifications_default_timing'] = data['timing']

    users.update_one({'email': email}, {"$set": user})

    return jsonify({"success": True, "status": "success", "message": "Settings updated successfully"})

@app.route("/consumption", methods=["POST"])
@jwt_required()
def add_consumption_data():
    email = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Missing fields'}), 400
    
    if not all(x in data.keys() for x in ["gas", "electricity", "water", "temperature", "atHome", "date", "timeslot"]):
        return jsonify({'error': 'Missing fields'}), 400

    consumption_data.insert_one({
        "email": email,
        "gas": data['gas'],
        "electricity": data['electricity'],
        "water": data['water'],
        "temperature": data['temperature'],
        "atHome": data['atHome'],
        "date": data['date'],
        "timeslot": data['timeslot']
    })

    return jsonify({"success": True, "status": "success", "message": "Consumption data added successfully"})

@app.route("/events", methods=["GET"])
@jwt_required()
def get_events():
    email = get_jwt_identity()
    events = calendar_data.find({"email": email})
    returning = []
    for event in events:
        del event['email']
        event['_id'] = str(event['_id'])
        returning.append(event)
    return jsonify({"success": True, "status": "success", "data": returning})

@app.route("/events", methods=["POST"])
@jwt_required()
def add_event():
    email = get_jwt_identity()
    data = request.get_json()

    print(data)

    if not data:
        return jsonify({'error': 'Missing fields'}), 400
    
    if not all(x in data.keys() for x in ["title", "start", "end", "toNotify", "notifyTiming"]):
        return jsonify({'error': 'Missing fields'}), 400

    calendar_data.insert_one({
        "email": email,
        "title": data['title'],
        "start": data['start'],
        "end": data['end'],
        "toNotify": data['toNotify'],
        "notifyTiming": data['notifyTiming']
    })

    return jsonify({"success": True, "status": "success", "message": "Event added successfully"})

@app.route("/events", methods=["DELETE"])
@jwt_required()
def delete_event():
    email = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Missing fields'}), 400
    
    if not all(x in data.keys() for x in ["title", "start", "end"]):
        return jsonify({'error': 'Missing fields'}), 400

    calendar_data.delete_one({
        "email": email,
        "title": data['title'],
        "start": data['start'],
        "end": data['end']
    })

    return jsonify({"success": True, "status": "success", "message": "Event deleted successfully"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)