from flask import Blueprint, request, jsonify
from analysis.venue import (
    venue_total_matches, venue_average_score, highest_team_total_at_venue,
    lowest_team_total_at_venue, venue_batting_first_win_percentage,
    venue_chasing_win_percentage
)

venue_bp = Blueprint('venue', __name__)

@venue_bp.route('/total_matches', methods=['GET'])
def get_total_matches():
    venue = request.args.get('venue')
    return jsonify(venue_total_matches(venue))

@venue_bp.route('/average_score', methods=['GET'])
def get_average_score():
    venue = request.args.get('venue')
    return jsonify(venue_average_score(venue))

@venue_bp.route('/highest_score', methods=['GET'])
def get_highest_score():
    venue = request.args.get('venue')
    return jsonify(highest_team_total_at_venue(venue))

@venue_bp.route('/lowest_score', methods=['GET'])
def get_lowest_score():
    venue = request.args.get('venue')
    return jsonify(lowest_team_total_at_venue(venue))

@venue_bp.route('/batting_first_win_percentage', methods=['GET'])
def get_batting_first_win_percentage():
    venue = request.args.get('venue')
    return jsonify(venue_batting_first_win_percentage(venue))

@venue_bp.route('/chasing_win_percentage', methods=['GET'])
def get_chasing_win_percentage():
    venue = request.args.get('venue')
    return jsonify(venue_chasing_win_percentage(venue))
