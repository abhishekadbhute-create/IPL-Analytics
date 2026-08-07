import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config

# Import Blueprints
from routes.player_routes import player_bp
from routes.bowler_routes import bowler_bp
from routes.team_routes import team_bp
from routes.venue_routes import venue_bp
from routes.season_routes import season_bp
from routes.match_routes import match_bp
from routes.compare_routes import compare_bp
from routes.search_routes import search_bp

frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
app = Flask(__name__, static_folder=frontend_folder, static_url_path='')
app.config.from_object(Config)

# Enable CORS for all routes
CORS(app)

# Register Blueprints
app.register_blueprint(player_bp, url_prefix='/player')
app.register_blueprint(bowler_bp, url_prefix='/bowler')
app.register_blueprint(team_bp, url_prefix='/team')
app.register_blueprint(venue_bp, url_prefix='/venue')
app.register_blueprint(season_bp, url_prefix='/season')
app.register_blueprint(match_bp, url_prefix='/match')
app.register_blueprint(compare_bp, url_prefix='/compare')
app.register_blueprint(search_bp, url_prefix='/api')

@app.route('/', methods=['GET'])
def home():
    return send_from_directory(frontend_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    if os.path.exists(os.path.join(frontend_folder, path)):
        return send_from_directory(frontend_folder, path)
    return send_from_directory(frontend_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
