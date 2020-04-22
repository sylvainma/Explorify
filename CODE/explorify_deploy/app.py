import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import urllib.parse
import requests
import pymongo

def load_database():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".mongodb.txt")
    with open(path, "r") as f:
        line = f.readline()
        return line

#give the app a name
app = Flask(__name__)
CORS(app)
#Temporary client for local stuffs
mongoclient = pymongo.MongoClient(load_database(), retryWrites=False)
db = mongoclient["heroku_9r8vqzsk"]
features_collection = db["features"]

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": 200}), 200

@app.route('/view', methods=['GET'])
def view():
    city = request.args.get('city', default="Atlanta")
    return render_template("viewer/index.html", data={"city":city})


@app.route('/', methods=['GET'])
def landing():
    return render_template("home/index.html")

@app.route('/city', methods=['GET'])
def get_city_geojson():
    if request.args.get('city'):
        city = request.args.get('city')
    else:
        json = request.get_json()
        city = json["city"]
    result = list(features_collection.find({"city":city}))
    print(result)
    print(type(result))
    if len(result) == 0:
        return jsonify({"err":"city not in collection"}), 404
    response = {"type": "FeatureCollection","features": result}
    return jsonify(response), 200

@app.route('/city', methods=['POST'])
def update_city_geojson():
    json = request.get_json()
    geojson = json["data"]
    city = json["city"]
    features = geojson["features"]
    expected_ids = set()
    for i in range(len(features)):
        features[i]["_id"] = features[i]["properties"]["id"]
        features[i]["city"] = city
        expected_ids.add(features[i]["_id"])
    try:
        result = features_collection.insert_many(features)
    except BulkWriteError:
        return jsonify({"Failed To Insert": list(expected_ids), "reason":"malformed request"}), 400

    failed = expected_ids - set(result.inserted_ids)
    return jsonify({"Failed To Insert": list(), "reason": "unknown"}), 200

@app.route('/image', methods=['POST'])
def update_image_props():
    print("hi")
    json = request.get_json()
    city = json["city"]
    newProperties = json["properties"]
    image_id = newProperties["id"]
    query = {"city": city, "_id": image_id}
    newValue = {"$set": {"properties": newProperties}}
    result = features_collection.update_one(query,newValue)
    if result.modified_count == 0:
        return jsonify({"err":"city or image not in collection"}), 404
    return jsonify("Success"), 200

@app.route('/city', methods=['DELETE'])
def delete_city():
    json = request.get_json()
    city = json["city"]
    features_collection.delete_many({"city": city})
    return jsonify("Hello"), 200

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r