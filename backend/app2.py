from flask import Flask, request, jsonify
from numpy import mod
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from constants import GAS_PRICE, WATER_PRICE, ELETRICITY_PRICE
from flask_cors import CORS
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)
CORS(app)

mongo = MongoClient('localhost', 27017)
main_db = mongo['lbec2024']

users = main_db['users']
consumption_data = main_db['consumption_data']
event_calendar = main_db['event_calendar']

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
        'hashed_password': hashed_password,
        'prefered_temperature': -1000
    }
    users.insert_one(new_user)

    return jsonify({'message': 'User registered successfully'}), 201

# User login route
@app.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    user = users.find_one({'email': email})

    print(user)
    if not user or not check_password_hash(user['hashed_password'], password):
        return jsonify({'success': False, 'message': 'Invalid email or password'})

    token = jwt.encode({
        'id': str(user['_id']),
        'email': user['email'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, app.config['SECRET_KEY'])

    return jsonify({'success': True, 'token': token})


#TODO
#@app.route('/login', methods=['PUT'])
#def addPreferedTemp(email):

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
 
@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = users.find()
    user_list = []
    for user in all_users:
        user['_id'] = str(user['_id'])
        user_list.append(user)
    return jsonify(user_list)

@app.route('/users/<email>', methods=['GET'])
def get_user_info(email):
    user = users.find_one({'email': email})
    return jsonify(str(user))

def get_user_info_by_email(email):
    user = users.find_one({'email': email})
    return jsonify(str(user))

@app.route('/consumptiondata', methods=['POST'])
def send_consumptionData():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Missing fields'}), 400
    
    email = data.get('email')
    day = data.get('day')
    time = data.get('time')
    gas = data.get('gas')
    eletricity = data.get('eletricity')
    water = data.get('water')
    temperature = data.get('temperature')
    at_home = data.get('at_home')

    # Check if all fields are present
    if not all(data[x] for x in ["email", "time", "gas", "eletricity", "water", "temperature", "at_home"]):
        return jsonify({'error': 'Missing fields'}), 400

    # Create a new data and send it to the database
    new_data = {
        'email': email,
        'time': time,
        'day': day,
        'gas': gas,
        'eletricity': eletricity,
        'water': water,
        'temperature': temperature,
        'at_home':at_home
    }
    consumption_data.insert_one(new_data)

    return jsonify({'message': 'User registered successfully'}), 201


    send_consumptionData()
    send_consumptionData()
    send_consumptionData()

def isAtHome(data):
    return data['at_home']

def getPreferedTemperatureMin(email):
    return get_user_info_by_email(email)['preferred_temperature_min']

def getPreferedTemperatureMax(email):
    return get_user_info_by_email(email)['preferred_temperature_max']

def aux_getUsageDay(email, date): 
    gas = 0
    eletricity = 0
    water = 0
    inhousetempchange = 0
    tempChange = 0
    inHouseEletricity = 0
    user_temp_min = getPreferedTemperatureMin(email)
    user_temp_max = getPreferedTemperatureMax(email)
    day_data = consumption_data.find({'email': email, 'day': date})
    for x in day_data:
        gas += x['gas']
        eletricity += x['eletricity']
        water += x['water']
        if isAtHome(x):
            if x['temperature'] < user_temp_min:
                inhousetempchange += user_temp_min - x['temperature']
            elif x['temperature'] > user_temp_max:
                inhousetempchange += x['temperature'] - user_temp_max
            inHouseGas +=  x['gas']
            inHouseWater += x['water']
            inHouseEletricity += x['eletricity']
        if x['temperature'] < user_temp_min:
            tempChange += user_temp_min - x['temperature']
        elif x['temperature'] > user_temp_max:
            tempChange += x['temperature'] - user_temp_max
        
    
    day_struct = {
        'email': email,
        'date': date,
        'gas': gas,
        'eletricity': eletricity,
        'water': water,
        'tempChange': tempChange,
        'usefulTempChange': inhousetempchange,
        'inHouseEletricity': inHouseEletricity
    }
    
    return day_struct

def getPriceDay(email, date):
    usage = aux_getUsageDay(email, date)
    return usage['gas']* GAS_PRICE + usage['eletricity']*ELETRICITY_PRICE + usage['water']*WATER_PRICE
    
#@app.route('/data/<week>', methods=['GET'])
def aux_getUsageWeek(email, date):
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    weekday = date.weekday()
    monday = date - timedelta(days=weekday)
    dates = [monday + timedelta(days=i) for i in range(7)]
    week_data = []
    for date in dates:
        week_data.append(aux_getUsageDay(email, date))
    inhousetempchange = 0
    tempChange = 0
    gas = 0
    eletricity = 0
    water = 0
    inHouseEletricity = 0
    inhousewater = 0
    inhousegas = 0
    for x in week_data:
        gas += x['gas']
        eletricity += x['eletricity']
        water += x['water']
        inhousetempchange += x['usefulTempChange']
        inhouseeletricity += x['inhouseletricity']
        inhouseGas += x['inhouseGas']
        inhouseWater += x['inhouseWater']
        tempChange += x['tempChange']
    
    wek_struct = {
        'email': email,
        'date': date,
        'gas': gas,
        'eletricity': eletricity,
        'water': water,
        'tempChange': tempChange,
        'inhousegas' : inhouseGas,
        'inhousewater' : inhouseWater,
        'usefultempchange': inhousetempchange,
        'inhouseletricity': inhouseeletricity
    }
    
    return week_struct
 
def getPriceWeek(email,date):
    usage = aux_getUsageWeek(email, date)
    return usage['gas']* GAS_PRICE + usage['eletricity']*ELETRICITY_PRICE + usage['water']*WATER_PRICE
    
#@app.route('/data/<month>', methods=['GET'])

def aux_getUsageMonth(email, date):
    inhousetempchange = 0
    tempChange = 0
    gas = 0
    eletricity = 0
    water = 0
    inhouseeletricity = 0
    inhousewater = 0
    inhousegas = 0
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    
    first_day = date.replace(day=1)

    _, last_day = (first_day + timedelta(days=32)).strftime("%Y-%m-%d").split('-')
    last_day = int(last_day)

    dates = [first_day + timedelta(days=i) for i in range(last_day)]
    
    month_data = []
    for date in dates:
        month_data.append(aux_getUsageDay(email, date))
    l_temperature = []
    for x in month_data:
        gas += month_data.gas
        eletricity += month_data.eletricity
        water += month_data.water
        inhousetempchange += x['inhousetempchange']
        tempChange += x['tempChange']
        inhouseeletricity += x['inhouseeletricity']
        inhousewater += x['inhousewater']
        inhousegas += x['inhousegas']
    
    month_struct = {
        'email': email,
        'date': date,
        'gas': gas,
        'eletricity': eletricity,
        'water': water,
        'tempChange': tempChange,
        'usefulTempChange': inhousetempchange,
        'inhouseeletricity': inhouseeletricity,
        'inhousewater': inhousewater,
        'inhousegas': inhousegas
    }
    
    return month_struct

def getPriceMonth(email,date):
    usage = aux_getUsageMonth(email, date)
    return usage['gas']* GAS_PRICE + usage['eletricity']*ELETRICITY_PRICE + usage['water']*WATER_PRICE
    
def getIdealUsage(email, date):
    aux_data = aux_getUsageMonth(email,date)
    return aux_data['usefulTempChange']*0.03*0.46 + aux_data['inhouseEletricity']*0.15

def getIdealPrice(email, date):
    usage = getIdealUsage(email, date)
    return usage * ELETRICITY_PRICE
    
def aux_getPercentageIdeal(email, date):
    return  (getPriceMonth / getIdealPrice(email, date))

def getDayGraph(email, date):
    usage = aux_getUsageDay(email, date)
    day_data = consumption_data.find({'email': email, 'day': date})
    l_energy = []
    l_gas = []
    l_water = []
    for x in day_data:
        if x['time'] == 'Morning':
            morning = x
        elif x['time'] == 'Afternoon':
            afternoon = x
        elif x['time'] == 'Night':
            night = x
        else:
            print("Algo de muito errado aconteceu")
            
    l_energy.append(morning['energy'])
    l_water.append(morning['water'])
    l_gas.append(morning['gas'])
    
    l_energy.append(afternoon['energy'])
    l_water.append(afternoon['water'])
    l_gas.append(afternoon['gas'])
    
    l_energy.append(night['energy'])
    l_water.append(night['water'])
    l_gas.append(night['gas'])
    
    data = {
        'time':['Morning', 'Afternoon', 'Night'],
        'energy':l_energy,
        'water':l_water,
        'gas':l_gas,
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='energy', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    
    return fig

def getWeekGraph(email,date):
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    weekday = date.weekday()
    monday = date - timedelta(days=weekday)
    dates = [monday + timedelta(days=i) for i in range(7)]
    
    l_energy = []
    l_water = []
    l_gas = []
    weekData = []
    
    
    for date in dates:
        weekData.append(aux_getUsageDay(email, date))
    
    for x in weekData:
        l_energy.append(x['energy'])
        l_water.append(x['water']) 
        l_gas.append(x['gas'])
    
    data = {
        'time':['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'energy':l_energy,
        'water':l_water,
        'gas':l_gas,
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='energy', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    return fig

def getMonthGraph(email, date):
    
    l_energy = []
    l_water = []
    l_gas = []
    dayList = []
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    
    first_day = date.replace(day=1)

    _, last_day = (first_day + timedelta(days=32)).strftime("%Y-%m-%d").split('-')
    last_day = int(last_day)

    dates = [first_day + timedelta(days=i) for i in range(last_day)]
    
    month_data = []
    i = 1
    for date in dates:
        dayList.append(str(i))
        i += 1
        month_data.append(aux_getUsageDay(email, date))
    for x in month_data:
        l_energy.append(x['energy'])
        l_water.append(x['water']) 
        l_gas.append(x['gas'])
    
    data = {
        'time': dayList,
        'energy':l_energy,
        'water':l_water,
        'gas':l_gas,
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='energy', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    
    return fig

@app.route('D', methods=['GET'])
def getPercentageIdeal(email, date):
    return jsonify(aux_getPercentageIdeal)

@app.route('Z', methods=['GET'])
def getIdealGraph(email, date):
    label = ['Total Usage', 'Ideal Usage']
    percentage = aux_getPercentageIdeal(email,date)
    usages = [percentage, 1]
    colors = ['blue', 'white']
    fig = go.Figure(data=[go.Pie(labels=label, values=usages, marker_colors = colors)])
    return fig
    
@app.route('C', methods=['GET'])
def monthClicked(email, date):
    usage = aux_getUsageDay(email,date)
    cost = getPriceDay(email, date)
    data = {
        'graph' : getDayGraph(email, date),
        'cost' : cost ,
        'wastedgas' : usage['gas'] - usage['inhousegas'],
        'wastedwater' : usage['water'] - usage['inhousewater'],
        'wastedenergy' : (usage['eletricity'] - usage['inhouseeletricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
        'wastedmoney' : cost - getIdealPrice(email,date)
    }
    return jsonify(data)

@app.route('A', methods=['GET'])
def weekClicked(email, date):
    usage = aux_getUsageWeek(email,date)
    cost = getPriceWeek(email, date)
    data = {
        'graph' : getWeekGraph(email, date),
        'cost' : cost ,
        'wastedgas' : usage['gas'] - usage['inhousegas'],
        'wastedwater' : usage['water'] - usage['inhousewater'],
        'wastedenergy' : (usage['eletricity'] - usage['inhouseeletricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
        'wastedmoney' : cost - getIdealPrice(email,date)
    }
    return jsonify(data)

@app.route('B', methods=['GET'])
def monthClicked(email, date):
    usage = aux_getUsageMonth(email,date)
    cost = getPriceMonth(email, date)
    data = {
        'graph' : getMonthGraph(email, date),
        'cost' : cost ,
        'wastedgas' : usage['gas'] - usage['inhousegas'],
        'wastedwater' : usage['water'] - usage['inhousewater'],
        'wastedenergy' : (usage['eletricity'] - usage['inhouseeletricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
        'wastedmoney' : cost - getIdealPrice(email,date)
    }
    return jsonify(data)



@app.route('J', methods=['POST'])
def addEvent(day, title, description, at_home, time):
    new_data = {
        'title': title,
        'description': description,
        'time': time,
        'at_home': at_home,
        'day': day
    }
    event_calendar.insert_one(new_data)

@app.route('DELETE', methods=['DELETE'])
def deleteEvent(day, title):
    event_calendar.find_one_and_delete({'title': title}, {'day': day})

@app.route('PUT', methods=['PUT'])
def editEvent(day, title, which, edit): #which is a num value from 0 to 4 that assinalates what will be changed
    event = event_calendar.find_one({'title': title}, {'day': day})
    if which == 0:
        event['title'] = edit
    elif which == 1:
        event['description'] = edit
    elif which == 2:
        event['time'] = edit
    elif which == 3:
        event['at_home'] = bool(edit)
    elif which == 4:
        event['day'] = edit
        
    event_calendar.update_one({'title': title, 'day': day}, {"$set": event})


if __name__ == "__main__":
    app.run(debug=True)