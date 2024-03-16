from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
mongo = MongoClient('localhost', 27017)

main_db = mongo['lbec2024']

users = main_db['users']
energy_db = main_db['energy']
water_db = main_db['water']
gas = main_db['gas']

if __name__ == "__main__":
    app.run(debug=True)
