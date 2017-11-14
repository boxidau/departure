from flask import Flask, jsonify
from graph_driver import GraphDriver
from flask_cors import CORS

app = Flask(__name__)
app.config.from_envvar('CONFIG_FILE')
CORS(app)

routing_engine = GraphDriver(
    app.config.get('NEO4J_USER'),
    app.config.get('NEO4J_PASSWORD'),
    app.config.get('NEO4J_HOST'))

@app.route('/routes/<string:origin>/<string:destination>')
def get_routes(origin, destination):
    routes = [route.to_dict() for route in
              routing_engine.get_all_routes(origin, destination)]

    routes = sorted(routes, key=lambda x: x['steps'][0]['departure_time'])
    return jsonify({
        "origin": origin,
        "destination": destination,
        "routes": routes
    })

