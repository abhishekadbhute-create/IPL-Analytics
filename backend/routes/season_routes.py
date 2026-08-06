from flask import Blueprint, request, jsonify
from analysis.season import season_summary

season_bp = Blueprint('season', __name__)

@season_bp.route('/summary', methods=['GET'])
def get_summary():
    season = request.args.get('season')
    if season:
        return jsonify(season_summary(int(season)))
    return jsonify({"error": "Season parameter is required"})
