from flask import Blueprint, request, jsonify
from analysis.player import (
    top_run_scorers, player_total_runs, player_average, player_highest_score,
    player_centuries, player_half_centuries, player_sixes, player_fours,
    player_runs_by_season, player_runs_against_team, player_runs_at_venue, boundary_percentage
)

player_bp = Blueprint('player', __name__)

@player_bp.route('/top_scorers', methods=['GET'])
def get_top_scorers():
    top_n = int(request.args.get('top_n', 10))
    season = int(request.args.get('season', 2023))
    return jsonify(top_run_scorers(top_n, season))

@player_bp.route('/total_runs', methods=['GET'])
def get_total_runs():
    player = request.args.get('player')
    return jsonify(player_total_runs(player))

@player_bp.route('/average', methods=['GET'])
def get_average():
    player = request.args.get('player')
    return jsonify(player_average(player))

@player_bp.route('/highest_score', methods=['GET'])
def get_highest_score():
    player = request.args.get('player')
    return jsonify(player_highest_score(player))

@player_bp.route('/centuries', methods=['GET'])
def get_centuries():
    player = request.args.get('player')
    return jsonify(player_centuries(player))

@player_bp.route('/half_centuries', methods=['GET'])
def get_half_centuries():
    player = request.args.get('player')
    return jsonify(player_half_centuries(player))

@player_bp.route('/sixes', methods=['GET'])
def get_sixes():
    player = request.args.get('player')
    return jsonify(player_sixes(player))

@player_bp.route('/fours', methods=['GET'])
def get_fours():
    player = request.args.get('player')
    return jsonify(player_fours(player))

@player_bp.route('/runs_by_season', methods=['GET'])
def get_runs_by_season():
    player = request.args.get('player')
    return jsonify(player_runs_by_season(player))

@player_bp.route('/runs_against_team', methods=['GET'])
def get_runs_against_team():
    player = request.args.get('player')
    team = request.args.get('team')
    return jsonify(player_runs_against_team(player, team))

@player_bp.route('/runs_at_venue', methods=['GET'])
def get_runs_at_venue():
    player = request.args.get('player')
    venue = request.args.get('venue')
    return jsonify(player_runs_at_venue(player, venue))

@player_bp.route('/boundary_percentage', methods=['GET'])
def get_boundary_percentage():
    player = request.args.get('player')
    return jsonify(boundary_percentage(player))
