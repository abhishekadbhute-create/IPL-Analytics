from flask import Flask, jsonify
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

app = Flask(__name__)
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
    return jsonify({"message": "Welcome to IPL Analytics API"})

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, port=Config.PORT)
