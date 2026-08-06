from flask import Blueprint, request, jsonify
from analysis.compare import (
    compare_batsmen, compare_bowlers, compare_teams,
    compare_venues, compare_seasons
)

compare_bp = Blueprint('compare', __name__)

@compare_bp.route('/batsmen', methods=['GET'])
def get_compare_batsmen():
    player1 = request.args.get('player1')
    player2 = request.args.get('player2')
    return jsonify(compare_batsmen(player1, player2))

@compare_bp.route('/bowlers', methods=['GET'])
def get_compare_bowlers():
    player1 = request.args.get('player1')
    player2 = request.args.get('player2')
    return jsonify(compare_bowlers(player1, player2))

@compare_bp.route('/teams', methods=['GET'])
def get_compare_teams():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    return jsonify(compare_teams(team1, team2))

@compare_bp.route('/venues', methods=['GET'])
def get_compare_venues():
    venue1 = request.args.get('venue1')
    venue2 = request.args.get('venue2')
    return jsonify(compare_venues(venue1, venue2))

@compare_bp.route('/seasons', methods=['GET'])
def get_compare_seasons():
    season1 = request.args.get('season1')
    season2 = request.args.get('season2')
    return jsonify(compare_seasons(season1, season2))
