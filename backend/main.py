from flask import Flask
from flask import jsonify
from flask import request
from journey import compute_journey

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({'message': 'Hello Explorify!'})

@app.route('/poi', methods=['GET'])
def get_poi():
    return jsonify({
        'poi': [
            {
                'name': 'TTH restaurant',
                'latitude': 121.478,
                'longitude': 31.27
            },
            {
                'name': 'Chalam restaurant',
                'latitude': 121.480,
                'longitude': 31.27
            },
        ]
    })

@app.route('/journey', methods=['GET'])
def get_journey():
    '''Return journey object used in front application'''

    keywords = []
    if 'keywords' in request.args:
        keywords = [x.strip() for x in request.args.get('keywords').split()]

    price = None
    if 'price' in request.args:
        price = request.args.get('price')

    return jsonify(compute_journey(keywords, price))
