from flask import Blueprint, request, jsonify
from analysis.team import (
    team_total_matches, team_total_wins, team_win_percentage,
    team_highest_score, team_lowest_score, team_average_score,
    team_head_to_head, partnership_analysis,
    highest_team_total, lowest_team_total
)

team_bp = Blueprint('team', __name__)

@team_bp.route('/total_matches', methods=['GET'])
def get_total_matches():
    team = request.args.get('team')
    return jsonify(team_total_matches(team))

@team_bp.route('/total_wins', methods=['GET'])
def get_total_wins():
    team = request.args.get('team')
    return jsonify(team_total_wins(team))

@team_bp.route('/win_percentage', methods=['GET'])
def get_win_percentage():
    team = request.args.get('team')
    return jsonify(team_win_percentage(team))

@team_bp.route('/highest_score', methods=['GET'])
def get_highest_score():
    team = request.args.get('team')
    opponent = request.args.get('opponent')
    return jsonify(team_highest_score(team, opponent))

@team_bp.route('/lowest_score', methods=['GET'])
def get_lowest_score():
    team = request.args.get('team')
    opponent = request.args.get('opponent')
    return jsonify(team_lowest_score(team, opponent))

@team_bp.route('/average_score', methods=['GET'])
def get_average_score():
    team = request.args.get('team')
    return jsonify(team_average_score(team))

@team_bp.route('/head_to_head', methods=['GET'])
def get_head_to_head():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    return jsonify(team_head_to_head(team1, team2))

@team_bp.route('/partnerships', methods=['GET'])
def get_partnerships():
    team = request.args.get('team')
    return jsonify(partnership_analysis(team))

@team_bp.route('/overall_highest', methods=['GET'])
def get_overall_highest():
    return jsonify(highest_team_total())

@team_bp.route('/overall_lowest', methods=['GET'])
def get_overall_lowest():
    return jsonify(lowest_team_total())
