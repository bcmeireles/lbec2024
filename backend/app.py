import json
from pymongo import MongoClient
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask_cors import CORS
import plotly.graph_objects as go
import base64
from io import BytesIO
import statistics

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

def getUserDict(email):
    user = users.find_one({'email': email})
    return {
        "gas_price": user['gas_price'],
        "electricity_price": user['electricity_price'],
        "water_price": user['water_price'],
        "min_house_temp": user['min_house_temp'],
        "max_house_temp": user['max_house_temp'],
        "enable_notifications": user['enable_notifications'],
        "notifications_default_timing": user['notifications_default_timing']
    }

def getDayMorningUsage(email, date):
    day_data = consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Morning'})
    if not day_data:
        return [0, 0, 0]
    return [day_data["gas"], day_data["electricity"], day_data["water"]]
        
def getIdealDayMorningUsage(email, date):
    day_data = consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Morning'})
    if not day_data:
        return [0, getMinimumElectricity(email), 0]
    if day_data["atHome"]:
        return [day_data["gas"], day_data["electricity"], day_data["water"]]
    else:
        return [0, getMinimumElectricity(email), 0]

def getDayAfternoonUsage(email, date):
    day_data = consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Afternoon'})
    if not day_data:
        return [0, 0, 0]
    return [day_data["gas"], day_data["electricity"], day_data["water"]]

def getIdealDayAfternoonUsage(email, date):
    day_data =consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Afternoon'})
    if not day_data:
        return [0, getMinimumElectricity(email), 0]
    if day_data["atHome"]:
        return [day_data["gas"], day_data["electricity"], day_data["water"]]
    else:
        return [0, getMinimumElectricity(email), 0]

def getDayNightUsage(email, date):
    day_data = consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Night'})
    if not day_data:
        return [0, 0, 0]
    return [day_data["gas"], day_data["electricity"], day_data["water"]]

def getIdealDayNightUsage(email, date):
    day_data = consumption_data.find_one({'email': email, 'date': date, 'timeslot': 'Night'})
    if not day_data:
        return [0, getMinimumElectricity(email), 0]
    if day_data["atHome"]:
        return [day_data["gas"], day_data["electricity"], day_data["water"]]
    else:
        return [0, getMinimumElectricity(email), 0]

def getDayUsage(email, date):
    day_data = consumption_data.find({'email': email, 'date': date})
    day_gas = 0
    day_electricity = 0
    day_water = 0
    for data in day_data:
        day_gas += data["gas"]
        day_electricity += data["electricity"]
        day_water += data["water"]
    return [day_gas, day_electricity, day_water]

def getRangeUsage(email, start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    date_list = []
    gas_usage = []
    electricity_usage = []
    water_usage = []

    current_date = start_date.date()  # convert to date object to remove time
    while current_date <= end_date.date():  # convert to date object to remove time
        usage = getDayUsage(email, str(current_date))
        if usage:
            gas_usage.append(usage[0])
            electricity_usage.append(usage[1])
            water_usage.append(usage[2])
        else:
            gas_usage.append(None)
            electricity_usage.append(None)
            water_usage.append(None)
        current_date += timedelta(days=1)

    return [sum(gas_usage), sum(electricity_usage), sum(water_usage)]

def getUserCosts(email):
    user = users.find_one({'email': email})
    return [user['gas_price'], user['electricity_price'], user['water_price']]

def getDayIdealUsage(email, date):
    day_data = consumption_data.find({'email': email, 'date': date})
    ideal_day_gas = 0
    ideal_day_electricity = 0
    ideal_day_water = 0
    for data in day_data:
        if data["atHome"]:
            ideal_day_gas += data["gas"]
            ideal_day_electricity += data["electricity"]
            ideal_day_water += data["water"]
        else:
            ideal_day_electricity += getMinimumElectricity(email)

    return [ideal_day_gas, ideal_day_electricity, ideal_day_water]

def getRangeIdealUse(email, start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    date_list = []
    gas_usage = []
    electricity_usage = []
    water_usage = []

    current_date = start_date.date()  # convert to date object to remove time
    while current_date <= end_date.date():  # convert to date object to remove time
        usage = getDayIdealUsage(email, str(current_date))
        if usage:
            gas_usage.append(usage[0])
            electricity_usage.append(usage[1])
            water_usage.append(usage[2])
        else:
            gas_usage.append(None)
            electricity_usage.append(None)
            water_usage.append(None)
        current_date += timedelta(days=1)

    return [sum(gas_usage), sum(electricity_usage), sum(water_usage)]

def getMinimumElectricity(email):
    athome_data = consumption_data.find({'atHome': True,'email': email})
    averageElectricity = 0
    l_atHome = []
    
    for data in athome_data:
        l_atHome.append(data['electricity'])
    
    return statistics.median(l_atHome) * 0.15

@app.route("/daygraph", methods=["POST"])
@jwt_required()
def getDayGraph():
    data = request.get_json()
    email = get_jwt_identity()
    date = data['date']

    morning_usage = getDayMorningUsage(email, date)
    afternoon_usage = getDayAfternoonUsage(email, date)
    night_usage = getDayNightUsage(email, date)

    timeslots = ['Morning', 'Afternoon', 'Night']

    fig = go.Figure()

    # Gas line (green)
    fig.add_trace(go.Scatter(x=timeslots, y=[morning_usage[0], afternoon_usage[0], night_usage[0]], mode='lines', name='Gas', line=dict(color='green')))

    # Electricity line (yellow)
    fig.add_trace(go.Scatter(x=timeslots, y=[morning_usage[1], afternoon_usage[1], night_usage[1]], mode='lines', name='Electricity', line=dict(color='yellow')))

    # Water line (blue)
    fig.add_trace(go.Scatter(x=timeslots, y=[morning_usage[2], afternoon_usage[2], night_usage[2]], mode='lines', name='Water', line=dict(color='blue')))

    ideal_morning_usage = getIdealDayMorningUsage(email, date)
    ideal_afternoon_usage = getIdealDayAfternoonUsage(email, date)
    ideal_night_usage = getIdealDayNightUsage(email, date)

    # Ideal gas line (dashed green)
    fig.add_trace(go.Scatter(x=timeslots, y=[ideal_morning_usage[0], ideal_afternoon_usage[0], ideal_night_usage[0]], mode='lines', name='Ideal Gas', line=dict(color='green', dash='dash')))
    # Ideal electricity line (dashed yellow)
    fig.add_trace(go.Scatter(x=timeslots, y=[ideal_morning_usage[1], ideal_afternoon_usage[1], ideal_night_usage[1]], mode='lines', name='Ideal Electricity', line=dict(color='yellow', dash='dash')))
    # Ideal water line (dashed blue)
    fig.add_trace(go.Scatter(x=timeslots, y=[ideal_morning_usage[2], ideal_afternoon_usage[2], ideal_night_usage[2]], mode='lines', name='Ideal Water', line=dict(color='blue', dash='dash')))

    fig.update_layout(
        title='Usage by Time of Day',
        xaxis_title='Time of Day',
        yaxis_title='Usage',
        paper_bgcolor='rgba(255,255,255,0.5)',
        plot_bgcolor='rgba(255,255,255,0.5)'
    )

    fig.write_image("fig1.png")

    buf = BytesIO()
    fig.write_image(buf, format='png')
    # Get the base64 encoded image data
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    total_usage = getDayUsage(email, date)
    total_costs = [total_usage[0] * getUserCosts(email)[0], total_usage[1] * getUserCosts(email)[1], total_usage[2] * getUserCosts(email)[2]]

    return jsonify({"success": True, "status": "success", "data": {
        "total_usage": {
            "gas": total_usage[0],
            "electricity": total_usage[1],
            "water": total_usage[2]
        },
        "total_costs": {
            "gas": total_costs[0],
            "electricity": total_costs[1],
            "water": total_costs[2]
        },
        "graph": "data:image/png;base64," + img_data
    }})

@app.route("/rangegraph", methods=["POST"])
@jwt_required()
def getRangeGraph():
    data = request.get_json()
    email = get_jwt_identity()
    start = data['start']
    end = data['end']

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    date_list = []
    gas_usage = []
    ideal_gas_usage = []
    electricity_usage = []
    ideal_electricity_usage = []
    water_usage = []
    ideal_water_usage = []

    current_date = start_date.date()  # convert to date object to remove time
    while current_date <= end_date.date():  # convert to date object to remove time
        date_list.append(str(current_date))  # convert date object to string
        usage = getDayUsage(email, str(current_date))
        ideal_usage = getDayIdealUsage(email, str(current_date))
        if usage:
            gas_usage.append(usage[0])
            electricity_usage.append(usage[1])
            water_usage.append(usage[2])
        else:
            gas_usage.append(None)
            electricity_usage.append(None)
            water_usage.append(None)

        if ideal_usage:
            ideal_gas_usage.append(ideal_usage[0])
            ideal_electricity_usage.append(ideal_usage[1])
            ideal_water_usage.append(ideal_usage[2])
        else:
            ideal_gas_usage.append(None)
            ideal_electricity_usage.append(None)
            ideal_water_usage.append(None)

        current_date += timedelta(days=1)

    fig = go.Figure()

    # Gas line (green)
    fig.add_trace(go.Scatter(x=date_list, y=gas_usage, mode='lines', name='Gas', line=dict(color='green')))

    # Electricity line (yellow)
    fig.add_trace(go.Scatter(x=date_list, y=electricity_usage, mode='lines', name='Electricity', line=dict(color='yellow')))

    # Water line (blue)
    fig.add_trace(go.Scatter(x=date_list, y=water_usage, mode='lines', name='Water', line=dict(color='blue')))

    # Ideal gas line (dashed green)
    fig.add_trace(go.Scatter(x=date_list, y=ideal_gas_usage, mode='lines', name='Ideal Gas', line=dict(color='green', dash='dash')))
    # Ideal electricity line (dashed yellow)
    fig.add_trace(go.Scatter(x=date_list, y=ideal_electricity_usage, mode='lines', name='Ideal Electricity', line=dict(color='yellow', dash='dash')))
    # Ideal water line (dashed blue)
    fig.add_trace(go.Scatter(x=date_list, y=ideal_water_usage, mode='lines', name='Ideal Water', line=dict(color='blue', dash='dash')))


    fig.update_layout(
        title='Usage from ' + start + ' to ' + end,
        xaxis_title='Date',
        yaxis_title='Usage',
        paper_bgcolor='rgba(255,255,255,0.5)',
        plot_bgcolor='rgba(255,255,255,0.5)'
    )

    fig.write_image("fig2.png")

    buf = BytesIO()
    fig.write_image(buf, format='png')
    # Get the base64 encoded image data
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    total_usage = getRangeUsage(email, start, end)
    total_costs = [total_usage[0] * getUserCosts(email)[0], total_usage[1] * getUserCosts(email)[1], total_usage[2] * getUserCosts(email)[2]]

    return jsonify({"success": True, "status": "success", "data": {
        "total_usage": {
            "gas": total_usage[0],
            "electricity": total_usage[1],
            "water": total_usage[2]
        },
        "total_costs": {
            "gas": total_costs[0],
            "electricity": total_costs[1],
            "water": total_costs[2]
        },
        "graph": "data:image/png;base64," + img_data
    }})

@app.route("/import", methods=["POST"])
@jwt_required()
def import_data():
    email = get_jwt_identity()
    data = request.get_json()
    for entry in data[email]:
        consumption_data.insert_one(entry)

    return jsonify({"success": True, "status": "success", "message": "Data imported successfully"})

@app.route("/export", methods=["GET"])
@jwt_required()
def export_data():
    email = get_jwt_identity()
    data = consumption_data.find({'email': email})
    returning = []
    for entry in data:
        del entry['_id']
        returning.append(entry)
    return jsonify({"success": True, "status": "success", email: returning}), 200, {'Content-Type': 'application/json'}


if __name__ == "__main__":
    app.run(debug=True, port=5000)