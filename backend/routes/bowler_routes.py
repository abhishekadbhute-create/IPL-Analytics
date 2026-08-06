from flask import Blueprint, request, jsonify
from analysis.bowler import (
    top_wicket_takers, player_total_wickets, player_economy, player_bowling_average,
    player_bowling_strike_rate, player_best_figures, player_wickets_by_season,
    player_wickets_against_team, player_dot_ball_percentage, bowler_vs_batsman
)

bowler_bp = Blueprint('bowler', __name__)

@bowler_bp.route('/top_wicket_takers', methods=['GET'])
def get_top_wicket_takers():
    top_n = int(request.args.get('top_n', 10))
    return jsonify(top_wicket_takers(top_n))

@bowler_bp.route('/total_wickets', methods=['GET'])
def get_total_wickets():
    player = request.args.get('player')
    return jsonify(player_total_wickets(player))

@bowler_bp.route('/economy', methods=['GET'])
def get_economy():
    player = request.args.get('player')
    return jsonify(player_economy(player))

@bowler_bp.route('/bowling_average', methods=['GET'])
def get_bowling_average():
    player = request.args.get('player')
    return jsonify(player_bowling_average(player))

@bowler_bp.route('/bowling_strike_rate', methods=['GET'])
def get_bowling_strike_rate():
    player = request.args.get('player')
    return jsonify(player_bowling_strike_rate(player))

@bowler_bp.route('/best_figures', methods=['GET'])
def get_best_figures():
    player = request.args.get('player')
    return jsonify(player_best_figures(player))

@bowler_bp.route('/wickets_by_season', methods=['GET'])
def get_wickets_by_season():
    player = request.args.get('player')
    return jsonify(player_wickets_by_season(player))

@bowler_bp.route('/wickets_against_team', methods=['GET'])
def get_wickets_against_team():
    player = request.args.get('player')
    team = request.args.get('team')
    return jsonify(player_wickets_against_team(player, team))

@bowler_bp.route('/dot_ball_percentage', methods=['GET'])
def get_dot_ball_percentage():
    player = request.args.get('player')
    return jsonify(player_dot_ball_percentage(player))

@bowler_bp.route('/vs_batsman', methods=['GET'])
def get_bowler_vs_batsman():
    bowler = request.args.get('bowler')
    batsman = request.args.get('batsman')
    return jsonify(bowler_vs_batsman(bowler, batsman))
