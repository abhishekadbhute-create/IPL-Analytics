import pandas as pd
import numpy as np
import analysis.all_functions as af
from utils.data_loader import matches, deliveries

def resolve_player(name: str) -> str:
    if not name:
        return name
    all_strikers = deliveries['striker'].dropna().unique()
    all_bowlers = deliveries['bowler'].dropna().unique()
    all_players = list(set(all_strikers).union(set(all_bowlers)))
    if name in all_players:
        return name
    lower_name = name.lower()
    for p in all_players:
        if p.lower() == lower_name:
            return p
    words = [w for w in lower_name.split() if len(w) > 2]
    matches_found = [p for p in all_players if any(w in p.lower() for w in words)]
    if matches_found:
        matches_found.sort(key=lambda p: sum(1 for w in words if w in p.lower()), reverse=True)
        return matches_found[0]
    return name

def resolve_team(name: str) -> str:
    aliases = {
        "rcb": "Royal Challengers Bangalore",
        "mi": "Mumbai Indians",
        "csk": "Chennai Super Kings",
        "kkr": "Kolkata Knight Riders",
        "srh": "Sunrisers Hyderabad",
        "dc": "Delhi Capitals",
        "kxip": "Kings XI Punjab",
        "rr": "Rajasthan Royals"
    }
    cleaned = name.lower().strip()
    if cleaned in aliases:
        return aliases[cleaned]
    all_teams = set(matches['team1'].dropna().unique()).union(set(matches['team2'].dropna().unique()))
    for t in all_teams:
        if t.lower() == cleaned or cleaned in t.lower():
            return t
    return name

def resolve_venue(name: str) -> str:
    aliases = {
        "m. chinnaswamy stadium": "Chinnaswamy Stadium",
        "chinnaswamy": "Chinnaswamy Stadium",
        "ma chidambaram stadium": "M. A. Chidambaram Stadium",
        "chepauk": "M. A. Chidambaram Stadium",
        "feroz shah kotla": "Arun Jaitley Stadium",
        "kotla": "Arun Jaitley Stadium",
        "wankhede": "Wankhede Stadium",
        "eden gardens": "Eden Gardens"
    }
    cleaned = name.lower().strip()
    if cleaned in aliases:
        return aliases[cleaned]
    all_venues = matches['venue'].dropna().unique()
    for v in all_venues:
        if cleaned in v.lower() or v.lower() in cleaned:
            return v
    return name

questions = [
    (1, "What is the total number of matches played by 'Royal Challengers Bangalore'?", lambda: af.team_total_matches(resolve_team("Royal Challengers Bangalore"))),
    (2, "How many matches has 'Mumbai Indians' won?", lambda: af.team_total_wins(resolve_team("Mumbai Indians"))),
    (3, "What is the win percentage of 'Chennai Super Kings'?", lambda: af.team_win_percentage(resolve_team("Chennai Super Kings"))),
    (4, "What is the highest score ever made by 'Kings XI Punjab'?", lambda: af.team_highest_score(resolve_team("Kings XI Punjab"))),
    (5, "What is the lowest score ever made by 'Delhi Capitals'?", lambda: af.team_lowest_score(resolve_team("Delhi Capitals"))),
    (6, "What is the total number of runs scored by 'MS Dhoni'?", lambda: af.player_total_runs(resolve_player("MS Dhoni"))),
    (7, "How many centuries has 'Virat Kohli' scored?", lambda: af.player_centuries(resolve_player("Virat Kohli"))),
    (8, "What is 'AB de Villiers' highest individual score?", lambda: af.player_highest_score(resolve_player("AB de Villiers"))),
    (9, "How many sixes has 'Chris Gayle' hit?", lambda: af.player_sixes(resolve_player("Chris Gayle"))),
    (10, "What are 'Dale Steyn's total wickets?", lambda: af.player_total_wickets(resolve_player("Dale Steyn"))),
    (11, "What is the economy rate of 'Sunil Narine'?", lambda: af.player_economy(resolve_player("Sunil Narine"))),
    (12, "What is the bowling average of 'Lasith Malinga'?", lambda: af.player_bowling_average(resolve_player("Lasith Malinga"))),
    (13, "How many matches have been played at 'M. Chinnaswamy Stadium'?", lambda: af.venue_total_matches(resolve_venue("M. Chinnaswamy Stadium"))),
    (14, "What is the average first innings score at 'Eden Gardens'?", lambda: af.venue_average_score(resolve_venue("Eden Gardens"))),
    (15, "What is the highest team total ever scored at 'Wankhede Stadium'?", lambda: af.highest_team_total_at_venue(resolve_venue("Wankhede Stadium"))),
    (16, "What is the lowest team total at 'Feroz Shah Kotla'?", lambda: af.lowest_team_total_at_venue(resolve_venue("Feroz Shah Kotla"))),
    (17, "What is the win percentage for teams batting first at 'MA Chidambaram Stadium'?", lambda: af.venue_batting_first_win_percentage(resolve_venue("MA Chidambaram Stadium"))),
    (18, "What was the summary for the 2011 season?", lambda: af.season_summary(2011)),
    (19, "What is the highest team total in the entire dataset?", lambda: af.highest_team_total()),
    (20, "What is the lowest team total in the entire dataset?", lambda: af.lowest_team_total()),
    (21, "How many half-centuries has 'Virat Kohli' scored?", lambda: af.player_fifties(resolve_player("Virat Kohli"))),
    (22, "How many fours has 'Rohit Sharma' hit?", lambda: af.player_fours(resolve_player("Rohit Sharma"))),
    (23, "What are 'MS Dhoni's runs scored season-wise?", lambda: af.player_runs_by_season(resolve_player("MS Dhoni"))),
    (24, "What are 'Virat Kohli's stats against 'Mumbai Indians'?", lambda: af.player_stats_against_team(resolve_player("Virat Kohli"), resolve_team("Mumbai Indians"))),
    (25, "What are 'AB de Villiers's stats at 'M. Chinnaswamy Stadium'?", lambda: af.player_stats_at_venue(resolve_player("AB de Villiers"), resolve_venue("M. Chinnaswamy Stadium"))),
    (26, "Who are the top 5 wicket-takers overall?", lambda: af.top_wicket_takers(top_n=5)),
    (27, "What is the bowling strike rate of 'Dale Steyn'?", lambda: af.player_bowling_strike_rate(resolve_player("Dale Steyn"))),
    (28, "What are 'Jasprit Bumrah's wickets by season?", lambda: af.player_wickets_by_season(resolve_player("Jasprit Bumrah"))),
    (29, "How many wickets has 'Sunil Narine' taken against 'Royal Challengers Bangalore'?", lambda: af.player_wickets_against_team(resolve_player("Sunil Narine"), resolve_team("Royal Challengers Bangalore"))),
    (30, "What is the dot ball percentage of 'Sunil Narine'?", lambda: af.player_dot_ball_percentage(resolve_player("Sunil Narine"))),
    (31, "What is the head-to-head record between 'Mumbai Indians' and 'Chennai Super Kings'?", lambda: af.head_to_head(resolve_team("Mumbai Indians"), resolve_team("Chennai Super Kings"))),
    (32, "What is the highest successful chase in IPL history?", lambda: af.highest_successful_chase()),
    (33, "Which match had the closest margin (in terms of runs)?", lambda: af.closest_margin_match()),
    (34, "Which match had the biggest win (in terms of runs)?", lambda: af.biggest_win_by_runs()),
    (35, "Get all unique team names in the dataset.", lambda: af.unique_teams()),
    (36, "Get the top 3 teams by win percentage.", lambda: af.top_teams_by_win_percentage(top_n=3)),
    (37, "What is 'Royal Challengers Bangalore's win percentage after winning the toss?", lambda: af.team_win_percentage_after_winning_toss(resolve_team("Royal Challengers Bangalore"))),
    (38, "What is 'Virat Kohli's strike rate in successful chases?", lambda: af.player_strike_rate_in_successful_chases(resolve_player("Virat Kohli"))),
    (39, "What is the average economy rate of 'Jasprit Bumrah' in death overs (16-20)?", lambda: af.player_economy_death_overs(resolve_player("Jasprit Bumrah"))),
    (40, "What is 'MS Dhoni's overall strike rate?", lambda: af.player_strike_rate(resolve_player("MS Dhoni"))),
    (41, "How many total runs has 'Rohit Sharma' scored?", lambda: af.player_total_runs(resolve_player("Rohit Sharma"))),
    (42, "What is 'AB de Villiers' overall batting average?", lambda: af.player_average(resolve_player("AB de Villiers"))),
    (43, "How many times has 'Chris Gayle' been dismissed for a duck?", lambda: af.player_duck_count(resolve_player("Chris Gayle"))),
    (44, "What is 'Dale Steyn's bowling average?", lambda: af.player_bowling_average(resolve_player("Dale Steyn"))),
    (45, "What is the highest score by 'Chennai Super Kings' at 'MA Chidambaram Stadium'?", lambda: getattr(af, 'team_highest_score_at_venue', lambda t, v: af.team_highest_score(t, venue=v))(resolve_team("Chennai Super Kings"), resolve_venue("MA Chidambaram Stadium"))),
    (46, "What was the champion team in the 2014 season?", lambda: getattr(af, 'season_champion', lambda s: af.season_summary(s).get('champion', 'Unknown'))(2014)),
    (47, "Who won the Orange Cap in the 2016 season?", lambda: getattr(af, 'season_orange_cap', lambda s: af.season_summary(s).get('orange_cap', 'Unknown'))(2016)),
    (48, "What is 'Virat Kohli's highest score in a single IPL season?", lambda: af.batsman_season_highest_score(resolve_player("Virat Kohli"))),
    (49, "How many wickets has 'Ravindra Jadeja' taken in total?", lambda: af.player_total_wickets(resolve_player("Ravindra Jadeja"))),
    (50, "What is 'Mumbai Indians' win percentage when batting first?", lambda: af.team_win_percentage_batting_first(resolve_team("Mumbai Indians"))),
    (51, "What is the most common dismissal type for 'Royal Challengers Bangalore' bowlers?", lambda: af.team_most_common_wicket_taking_dismissal_type(resolve_team("Royal Challengers Bangalore"))),
    (52, "What is the total number of extras conceded in match 'M0001'?", lambda: af.match_total_extras('M0001')),
    (53, "Which player has the most Player of the Match awards in the 2018 season?", lambda: af.season_most_player_of_match_award_winner(2018)),
    (54, "What is 'MS Dhoni's average runs per match?", lambda: af.batsman_runs_per_match_average(resolve_player("MS Dhoni"))),
    (55, "What is the highest partnership 'Virat Kohli' has been part of?", lambda: af.player_highest_partnership(resolve_player("Virat Kohli"))),
    (56, "How many times has 'Lasith Malinga' dismissed 'Rohit Sharma'?", lambda: af.batsman_dismissed_by_bowler_count(resolve_player("Rohit Sharma"), resolve_player("Lasith Malinga"))),
    (57, "What is 'Sunil Narine's economy rate in powerplay overs (1-6)?", lambda: getattr(af, 'bowler_economy_in_powerplay', lambda b: af.bowler_runs_conceded_in_powerplay(b))(resolve_player("Sunil Narine"))),
    (58, "What is the highest individual score in match 'M0002'?", lambda: af.match_highest_individual_score_details('M0002')),
    (59, "How many wickets did 'Jasprit Bumrah' take in matches where his team won?", lambda: af.bowler_wickets_in_wins(resolve_player("Jasprit Bumrah")))
]

print("==================================================")
print("EXECUTING ALL 59 QUESTIONS TEST SUITE")
print("==================================================")

success_count = 0
fail_count = 0

for q_no, q_text, func in questions:
    try:
        ans = func()
        print(f"\nQuestion {q_no}: {q_text}")
        print(f"Answer: {ans}")
        success_count += 1
    except Exception as e:
        print(f"\nQuestion {q_no}: {q_text}")
        print(f"ERROR: {e}")
        fail_count += 1

print("\n==================================================")
print(f"TEST SUMMARY: {success_count} SUCCESS, {fail_count} FAILED")
print("==================================================")
