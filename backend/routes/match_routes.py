from flask import Blueprint, request, jsonify
from analysis.match import (
    run_rate_by_over, win_probability, highest_successful_chase,
    closest_match, biggest_win
)

match_bp = Blueprint('match', __name__)

@match_bp.route('/run_rate_by_over', methods=['GET'])
def get_run_rate_by_over():
    match_id = request.args.get('match_id')
    return jsonify(run_rate_by_over(match_id))

@match_bp.route('/win_probability', methods=['GET'])
def get_win_probability():
    match_id = request.args.get('match_id')
    return jsonify(win_probability(match_id))

@match_bp.route('/highest_successful_chase', methods=['GET'])
def get_highest_successful_chase():
    return jsonify(highest_successful_chase())

@match_bp.route('/closest_match', methods=['GET'])
def get_closest_match():
    return jsonify(closest_match())

@match_bp.route('/biggest_win', methods=['GET'])
def get_biggest_win():
    return jsonify(biggest_win())
