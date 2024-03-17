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

'''
@app.route('C', methods=['GET'])
def dayClicked(email, date):
    usage = getUsageDay(email,date)
    cost = getPriceDay(email, date)
    data = {
        'graph' : getDayGraph(email, date),
        'cost' : cost ,
        'wastedgas' : usage['gas'] - usage['inhousegas'],
        'wastedwater' : usage['water'] - usage['inhousewater'],
        'wastedelectricity' : (usage['electricity'] - usage['inhouseelectricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
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
        'wastedelectricity' : (usage['electricity'] - usage['inhouseelectricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
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
        'wastedelectricity' : (usage['electricity'] - usage['inhouseelectricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
        'wastedmoney' : cost - getIdealPrice(email,date)
    }
    return jsonify(data)
'''


app = Flask(__name__)
CORS(app)

mongo = MongoClient('localhost', 27017)
main_db = mongo['lbec2024']

users = main_db['users']
consumption_data = main_db['consumption_data']



def getGasPrice(email):
    user = users.find_one({'email': email})
    return user['gas_price']

def getWaterPrice(email):
    user = users.find_one({'email': email})
    return user['water_price']

def getElecPrice(email):
    user = users.find_one({'email': email})
    return user['electricity_price']


#By day
def getUsageDay(email, date): 
    gas = 0
    electricity = 0
    water = 0
    inhousetempchange = 0
    tempChange = 0
    inHouseElectricity = 0
    
    user_temp_min = getPreferedTemperatureMin(email)
    user_temp_max = getPreferedTemperatureMax(email)
    

    day_data = consumption_data.find({'email': email, 'day': date})
    
    
    for x in day_data:
        gas += x['gas']
        electricity += x['electricity']
        water += x['water']
        
        if isAtHome(x):
            if x['temperature'] < user_temp_min:
                inhousetempchange += user_temp_min - x['temperature']
            elif x['temperature'] > user_temp_max:
                inhousetempchange += x['temperature'] - user_temp_max 
            inhousegas +=  x['gas']
            inhousewater += x['water']
            inhouseelectricity += x['electricity']
            
            
        if x['temperature'] < user_temp_min:
            tempChange += user_temp_min - x['temperature']
            
        elif x['temperature'] > user_temp_max:
            tempChange += x['temperature'] - user_temp_max
        
    
    day_struct = {
        'email': email,
        'date': date,
        
        'gas': gas,
        'electricity': electricity,
        'water': water,
        
        'tempChange': tempChange,
        'inhousetempchange': inhousetempchange,
        'inhouseelectricity': inhouseelectricity,
        'inhousegas' : inhousegas
    }
    
    return day_struct

def getIdealThroughout(email, date):
    
    morning = {'Water': '', 'Gas': '', 'Electricity' : ''}
    afternoon = {'Water': '', 'Gas': '', 'Electricity' : ''}
    night = {'Water': '', 'Gas': '', 'Electricity' : ''}
    
    answer= {'Morning': morning, 'Afternoon': afternoon, 'Night' : night}
    
    
    min = getUserMin(email)
    day_data = consumption_data.find({'email': email, 'day': date})
    
    for data in day_data:
        if data['timeslot'] == 'Morning':
            if data['atHouse']:
                answer['Morning']['Water'] = data['water']
                answer['Morning']['Gas'] = data['gas']
                answer['Morning']['Electricity'] = data['electricity']
            else:
                answer['Morning']['Water'] = 0
                answer['Morning']['Gas'] = 0
                answer['Morning']['Electricity'] = min
                
        elif data['timeslot'] == 'Afternoon':
            if data['atHouse']:
                answer['Afternoon']['Water'] = data['water']
                answer['Afternoon']['Gas'] = data['gas']
                answer['Afternoon']['Electricity'] = data['electricity']
            else:
                answer['Afternoon']['Water'] = 0
                answer['Afternoon']['Gas'] = 0
                answer['Afternoon']['Electricity'] = min
        
        elif data['timeslot'] == 'Night':
            if data['atHouse']:
                answer['Night']['Water'] = data['water']
                answer['Night']['Gas'] = data['gas']
                answer['Night']['Electricity'] = data['electricity']
            else:
                answer['Night']['Water'] = 0
                answer['Night']['Gas'] = 0
                answer['Night']['Electricity'] = min
    
    return answer
           
def getIdealDay(email,date):
    throughout = getIdealThroughout(email,date)
    
    answer = {'Water': 0, 'Gas': 0, 'Electricity' : 0}
    
    for key in throughout.keys:
        answer['Water'] += throughout[key]['Water']
        answer['Electricity'] += throughout[key]['Electricity']  
        answer['Gas'] += throughout[key]['Gas']
    
    return answer    
    
def getPriceDay(email, date):
    usage = getUsageDay(email, date)
    return usage['gas']* getGasPrice(email) + usage['electricity']*getElecPrice(email) + usage['water']*getWaterPrice(email)

def getIdealPriceDay(email, date):
    idealDay = getIdealDay(email,date)
    return idealDay['water'] * getPriceWater(email) + idealDay['gas'] * getPriceGas(email) + idealDay['electricity'] * getPriceElectricity(email)

def getWastedDay(email, date):
    answer = {'Water': 0, 'Electricity': 0, 'Gas': 0}
    day = getUsageDay(email, date)
    ideal = getIdealDay(email, date)
    answer['Water'] = day['Water'] - ideal['Water']
    answer['Electricity'] = day['Electricity'] - ideal['Electricity']
    answer['Gas'] = day['Gas'] - ideal['Gas']
    
    return answer

def getMoneyWastedDay(email, date):
    return getPriceDay(email, date) - getIdealPriceDay(email, date)
    
def howManyMoreDay(email, date): 
    return getPriceDay(email, date) / getIdealPriceDay(email, date)

def getDayGraph(email, date):
    usage = getUsageDay(email, date)
    day_data = consumption_data.find({'email': email, 'day': date})
    l_electricity = []
    l_gas = []
    l_water = []
    for x in day_data:
        if x['time'] == 'Morning':
            morning = x
        elif x['time'] == 'Afternoon':
            afternoon = x
        elif x['time'] == 'Night':
            night = x
            
    l_electricity.append(morning['electricity'])
    l_water.append(morning['water'])
    l_gas.append(morning['gas'])
    
    l_electricity.append(afternoon['electricity'])
    l_water.append(afternoon['water'])
    l_gas.append(afternoon['gas'])
    
    l_electricity.append(night['electricity'])
    l_water.append(night['water'])
    l_gas.append(night['gas'])
    
    ideal = getIdealThroughout(email, date)
    data = {
        'time':['Morning', 'Afternoon', 'Night'],
        'electricity':l_electricity,
        'water':l_water,
        'gas':l_gas,
        'ideal_electricity': [ideal['Morning']['Electricity'], ideal['Afternoon']['Electricity'], ideal['Night']['Electricity']],
        'ideal_gas': [ideal['Morning']['Gas'], ideal['Afternoon']['Gas'], ideal['Night']['Gas']],
        'ideal_water': [ideal['Morning']['Water'], ideal['Afternoon']['Water'], ideal['Night']['Water']]
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='electricity', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    
    fig.add_traces(px.line(df, x='time', y='ideal_electricity', color_discrete_sequence=['orange'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_water', color_discrete_sequence=['blue'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_gas', color_discrete_sequence=['green'], markers=True, line_dash="dash").data)
    
    return fig


def getIdealGraphDay(email, date):
    label = ['Total Usage', 'Ideal Usage']
    percentage = howManyMoreDay(email,date)
    usages = [percentage, 1]
    colors = ['blue', 'white']
    fig = go.Figure(data=[go.Pie(labels=label, values=usages, marker_colors = colors)])
    return fig

#By week
def getUsageWeek(email, date):
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    weekday = date.weekday()
    monday = date - timedelta(days=weekday)
    dates = [monday + timedelta(days=i) for i in range(7)]
    week_data = []
    
    for date in dates:
        week_data.append(getUsageDay(email, date))
        
    gas = 0
    electricity = 0
    water = 0

    for x in week_data:
        gas += x['gas']
        electricity += x['electricity']
        water += x['water']
        
    
    week_struct = {
        'email': email,
        'gas': gas,
        'electricity': electricity,
        'water': water,
        'dates': dates
    }
    
    return week_struct
 
def getIdealWeek(email, date):
    answer = {'Water': 0, 'Gas': 0, 'Electricity' : 0}
    
    usageWeek = getUsageWeek(email, date)
    for day in usageWeek['dates']:
        answer['Water'] += getIdealDay(email, day)['Water']
        answer['Gas'] += getIdealDay(email, day)['Gas']
        answer['Electricity'] += getIdealDay(email, day)['Electricity']
    
    return answer

def getPriceWeek(email,date):
    answer = 0
    
    usageWeek = getUsageWeek(email, date)
    
    for day in usageWeek['dates']:
        answer += getPriceDay(email, day)

    return answer

def getIdealPriceWeek(email,date):
    answer = 0
    
    usageWeek = getUsageWeek(email, date)
    
    for day in usageWeek['dates']:
        answer += getIdealPriceDay(email, day)

    return answer

def getWasteWeek(email,date):
    answer = 0
    
    usageWeek = getUsageWeek(email, date)
    
    for day in usageWeek['dates']:
        answer += getWastedDay(email, day)

    return answer

def getMoneyWasteWeek(email,date):
    answer = 0
    
    usageWeek = getUsageWeek(email, date)
    
    for day in usageWeek['dates']:
        answer += getMoneyWastedDay(email, day)

    return answer

def howManyMoreWeek(email, date): 
    return getPriceWeek(email, date) / getIdealPriceWeek(email, date)

def getWeekGraph(email,date):
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    weekday = date.weekday()
    monday = date - timedelta(days=weekday)
    dates = [monday + timedelta(days=i) for i in range(7)]
    
    l_electricity = []
    l_water = []
    l_gas = []
    i_electricity = []
    i_water = []
    i_gas = []
    weekData = []
    idealData = []
    
    
    for date in dates:
        weekData.append(getUsageDay(email, date))
        idealData.append(getIdealDay(email, date))
    
    for x in weekData:
        l_electricity.append(x['electricity'])
        l_water.append(x['water']) 
        l_gas.append(x['gas'])
        
    for y in idealData:
        i_electricity.append(x['electricity'])
        i_water.append(x['water']) 
        i_gas.append(x['gas'])
    
    data = {
        'time':['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'electricity':l_electricity,
        'water':l_water,
        'gas':l_gas,
        'ideal_electricity': i_electricity,
        'ideal_gas': i_gas,
        'ideal_water': i_water
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='electricity', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    
    fig.add_traces(px.line(df, x='time', y='ideal_electricity', color_discrete_sequence=['orange'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_water', color_discrete_sequence=['blue'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_gas', color_discrete_sequence=['green'], markers=True, line_dash="dash").data)
    
    return fig

def getIdealGraphWeek(email, date):
    label = ['Total Usage', 'Ideal Usage']
    percentage = howManyMoreWeek(email,date)
    usages = [percentage, 1]
    colors = ['blue', 'white']
    fig = go.Figure(data=[go.Pie(labels=label, values=usages, marker_colors = colors)])
    return fig

#By month
def getUsageMonth(email, date):
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    
    first_day = date.replace(day=1)

    _, last_day = (first_day + timedelta(days=32)).strftime("%Y-%m-%d").split('-')
    last_day = int(last_day)

    dates = [first_day + timedelta(days=i) for i in range(last_day)]
    
    month_data = []
    
    for date in dates:
        month_data.append(getUsageDay(email, date))
        
    gas = 0
    electricity = 0
    water = 0

    for x in month_data:
        gas += x['gas']
        electricity += x['electricity']
        water += x['water']
        
    
    month_struct = {
        'email': email,
        'gas': gas,
        'electricity': electricity,
        'water': water,
        'dates': dates
    }
    
    return month_struct

def getIdealMonth(email, date):
    answer = {'Water': 0, 'Gas': 0, 'Electricity' : 0}
    
    usagemonth = getUsageMonth(email, date)
    for day in usagemonth['dates']:
        answer['Water'] += getIdealDay(email, day)['Water']
        answer['Gas'] += getIdealDay(email, day)['Gas']
        answer['Electricity'] += getIdealDay(email, day)['Electricity']
    
    return answer

def getPriceMonth(email,date):
    answer = 0
    
    usageMonth = getUsageMonth(email, date)
    
    for day in usageMonth['dates']:
        answer += getPriceDay(email, day)

    return answer

def getIdealPriceMonth(email,date):
    answer = 0
    
    usageMonth = getUsageMonth(email, date)
    
    for day in usageMonth['dates']:
        answer += getIdealPriceDay(email, day)

    return answer

def getWasteMonth(email,date):
    answer = 0
    
    usageMonth = getUsageMonth(email, date)
    
    for day in usageMonth['dates']:
        answer += getWastedDay(email, day)

    return answer

def getMoneyWasteMonth(email,date):
    answer = 0
    
    usageMonth = getUsageMonth(email, date)
    
    for day in usageMonth['dates']:
        answer += getMoneyWastedDay(email, day)

    return answer

def howManyMoreMonth(email, date): 
    return getPriceMonth(email, date) / getIdealPriceMonth(email, date)

def getMonthGraph(email, date):
    
    l_electricity = []
    l_water = []
    l_gas = []
    i_electricity = []
    i_water = []
    i_gas = []
    dayList = []
    
    date = datetime.strptime(date, "%Y-%m-%d") if isinstance(date, str) else date
    
    first_day = date.replace(day=1)

    _, last_day = (first_day + timedelta(days=32)).strftime("%Y-%m-%d").split('-')
    last_day = int(last_day)

    dates = [first_day + timedelta(days=i) for i in range(last_day)]
    
    month_data = []
    ideal_month_data = []
    i = 1
    for date in dates:
        dayList.append(str(i))
        i += 1
        month_data.append(getUsageDay(email, date))
        ideal_month_data.append(getIdealDay(email,date))
        
    for x in ideal_month_data:
        i_electricity.append(x['electricity'])
        i_water.append(x['water']) 
        i_gas.append(x['gas'])
        
        
    data = {
        'time': dayList,
        'electricity':l_electricity,
        'water':l_water,
        'gas':l_gas,
        'ideal_electricity': i_electricity,
        'ideal_gas': i_gas,
        'ideal_water': i_water
    }

    df = pd.DataFrame(data)

    fig = px.line(df, x='time', y='electricity', color_discrete_sequence=['orange'], markers=True)
    fig.add_traces(px.line(df, x='time', y='water', color_discrete_sequence=['blue'], markers=True).data)
    fig.add_traces(px.line(df, x='time', y='gas', color_discrete_sequence=['green'], markers=True).data)
    
    fig.add_traces(px.line(df, x='time', y='ideal_electricity', color_discrete_sequence=['orange'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_water', color_discrete_sequence=['blue'], markers=True, line_dash="dash").data)
    fig.add_traces(px.line(df, x='time', y='ideal_gas', color_discrete_sequence=['green'], markers=True, line_dash="dash").data)
    
    return fig

def getIdealGraphMonth(email, date):
    label = ['Total Usage', 'Ideal Usage']
    percentage = howManyMoreMonth(email,date)
    usages = [percentage, 1]
    colors = ['blue', 'white']
    fig = go.Figure(data=[go.Pie(labels=label, values=usages, marker_colors = colors)])
    return fig

'''@app.route('B', methods=['GET'])
def monthClicked(email, date):
    usage = aux_getUsageMonth(email,date)
    cost = getPriceMonth(email, date)
    data = {
        'graph' : getMonthGraph(email, date),
        'cost' : cost ,
        'wastedgas' : usage['gas'] - usage['inhousegas'],
        'wastedwater' : usage['water'] - usage['inhousewater'],
        'wastedelectricity' : (usage['electricity'] - usage['inhouseelectricity']) * 0.85 + (usage['tempchange'] - usage['inhousetempchange']) * 0.03 * 0.46,
        'wastedmoney' : cost - getIdealPrice(email,date)
    }
    return jsonify(data)'''

