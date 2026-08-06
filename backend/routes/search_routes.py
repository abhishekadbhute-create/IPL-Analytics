import os
import json
import inspect
import re
import pandas as pd
import numpy as np
from flask import Blueprint, request, jsonify
from google import genai
from google.genai import types

import analysis.all_functions as af
from utils.data_loader import matches, deliveries

search_bp = Blueprint('search', __name__)
client = None

def get_gemini_client():
    global client
    if not client:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=gemini_api_key)
    return client

# ---------------------------------------------------------
# Team, Player & Venue Resolvers
# ---------------------------------------------------------
TEAM_ALIASES = {
    "csk": "Chennai Super Kings",
    "chennai": "Chennai Super Kings",
    "chennai super kings": "Chennai Super Kings",
    "mi": "Mumbai Indians",
    "mumbai": "Mumbai Indians",
    "mumbai indians": "Mumbai Indians",
    "rcb": "Royal Challengers Bangalore",
    "bangalore": "Royal Challengers Bangalore",
    "royal challengers bangalore": "Royal Challengers Bangalore",
    "kkr": "Kolkata Knight Riders",
    "kolkata": "Kolkata Knight Riders",
    "kolkata knight riders": "Kolkata Knight Riders",
    "srh": "Sunrisers Hyderabad",
    "hyderabad": "Sunrisers Hyderabad",
    "sunrisers hyderabad": "Sunrisers Hyderabad",
    "dc": "Delhi Capitals",
    "delhi": "Delhi Capitals",
    "delhi capitals": "Delhi Capitals",
    "delhi daredevils": "Delhi Daredevils",
    "rr": "Rajasthan Royals",
    "rajasthan": "Rajasthan Royals",
    "rajasthan royals": "Rajasthan Royals",
    "pbks": "Punjab Kings",
    "kxip": "Kings XI Punjab",
    "punjab": "Punjab Kings",
    "punjab kings": "Punjab Kings",
    "kings xi punjab": "Kings XI Punjab",
    "gt": "Gujarat Titans",
    "gujarat": "Gujarat Titans",
    "gujarat titans": "Gujarat Titans",
    "lsg": "Lucknow Super Giants",
    "lucknow": "Lucknow Super Giants",
    "lucknow super giants": "Lucknow Super Giants",
    "deccan": "Deccan Chargers",
    "deccan chargers": "Deccan Chargers",
    "pune": "Pune Warriors India",
    "pune warriors": "Pune Warriors India"
}

VENUE_ALIASES = {
    "wankhede": "Wankhede Stadium",
    "wankhede stadium": "Wankhede Stadium",
    "eden": "Eden Gardens",
    "eden gardens": "Eden Gardens",
    "chinnaswamy": "Chinnaswamy Stadium",
    "chinnaswamy stadium": "Chinnaswamy Stadium",
    "chepauk": "M. A. Chidambaram Stadium",
    "chidambaram": "M. A. Chidambaram Stadium",
    "m. a. chidambaram stadium": "M. A. Chidambaram Stadium",
    "narendra modi": "Narendra Modi Stadium",
    "narendra modi stadium": "Narendra Modi Stadium",
    "motera": "Narendra Modi Stadium",
    "arun jaitley": "Arun Jaitley Stadium",
    "arun jaitley stadium": "Arun Jaitley Stadium",
    "kotla": "Arun Jaitley Stadium",
    "feroz shah kotla": "Arun Jaitley Stadium",
    "dy patil": "DY Patil Stadium",
    "dy patil stadium": "DY Patil Stadium",
    "brabourne": "Brabourne Stadium",
    "brabourne stadium": "Brabourne Stadium",
    "ekana": "Ekana Cricket Stadium",
    "ekana cricket stadium": "Ekana Cricket Stadium",
    "lucknow stadium": "Ekana Cricket Stadium",
    "rajiv gandhi": "Rajiv Gandhi Intl Cricket Stadium",
    "hyderabad stadium": "Rajiv Gandhi Intl Cricket Stadium",
    "sawai mansingh": "Sawai Mansingh Stadium",
    "jaipur stadium": "Sawai Mansingh Stadium",
    "pca": "Punjab Cricket Association Stadium",
    "mca": "MCA Stadium",
    "pune stadium": "MCA Stadium",
    "holkar": "Holkar Cricket Stadium",
    "indore stadium": "Holkar Cricket Stadium",
    "barabati": "Barabati Stadium",
    "cuttack stadium": "Barabati Stadium",
    "jsca": "JSCA Intl Stadium Complex",
    "ranchi stadium": "JSCA Intl Stadium Complex",
    "dharamsala": "Himachal Pradesh Cricket Association Stadium",
    "hpca": "Himachal Pradesh Cricket Association Stadium"
}

WORD_NUMS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twenty": 20
}

def resolve_team_name(val):
    if not isinstance(val, str) or not val.strip():
        return val
    cleaned = val.strip().lower()
    if cleaned in TEAM_ALIASES:
        return TEAM_ALIASES[cleaned]
    all_teams = matches['team1'].dropna().unique()
    for t in all_teams:
        if cleaned in t.lower() or t.lower() in cleaned:
            return t
    return val

def resolve_player_name(val):
    if not isinstance(val, str) or not val.strip():
        return val
    val_clean = val.strip()
    all_strikers = deliveries['striker'].dropna().unique()
    if val_clean in all_strikers:
        return val_clean
    lower_val = val_clean.lower()
    for s in all_strikers:
        if s.lower() == lower_val:
            return s
    matches_found = [s for s in all_strikers if lower_val in s.lower()]
    if matches_found:
        return matches_found[0]
    words = lower_val.split()
    for w in words:
        if len(w) > 2:
            word_matches = [s for s in all_strikers if w in s.lower()]
            if word_matches:
                return word_matches[0]
    return val_clean

def resolve_venue_name(val):
    if not isinstance(val, str) or not val.strip():
        return val
    cleaned = val.strip().lower()
    if cleaned in VENUE_ALIASES:
        return VENUE_ALIASES[cleaned]
    all_venues = matches['venue'].dropna().unique()
    for v in all_venues:
        if cleaned in v.lower() or v.lower() in cleaned:
            return v
    return val

def extract_team_from_query(query):
    q = query.lower()
    for alias, official in TEAM_ALIASES.items():
        if re.search(r'\b' + re.escape(alias) + r'\b', q):
            return official
    all_teams = matches['team1'].dropna().unique()
    for t in all_teams:
        if t.lower() in q:
            return t
    return None

def extract_player_from_query(query):
    q = query.lower()
    all_strikers = deliveries['striker'].dropna().unique()
    all_bowlers = deliveries['bowler'].dropna().unique()
    all_players = set(all_strikers).union(set(all_bowlers))
    
    for p in all_players:
        if p.lower() in q:
            return p
            
    words = q.split()
    ignore_words = {'total', 'matches', 'runs', 'wickets', 'highest', 'lowest', 'played', 'score', 'team', 'player', 'stat', 'stats', 'top', 'best', 'give', 'show', 'tell', 'baller', 'bowler', 'stadium', 'venue', 'bounders', 'boundary', 'boundaries', 'number', 'fours', 'sixes', 'economy', 'death', 'overs', 'rate', 'average', 'avg', 'what', 'which', 'who'}
    for w in words:
        clean_w = re.sub(r'[^a-zA-Z]', '', w.lower())
        if len(clean_w) > 3 and clean_w not in ignore_words:
            word_matches = [p for p in all_players if clean_w in p.lower()]
            if word_matches:
                return word_matches[0]
    return None

def extract_venue_from_query(query):
    q = query.lower()
    for alias, official in VENUE_ALIASES.items():
        if alias in q:
            return official
    all_venues = matches['venue'].dropna().unique()
    for v in all_venues:
        if v.lower() in q:
            return v
        words = v.lower().split()
        for w in words:
            if len(w) > 4 and w in q:
                return v
    return None

# ---------------------------------------------------------
# Tool Mapping & Execution Engine
# ---------------------------------------------------------
TOOL_MAPPING = {}
for name, obj in inspect.getmembers(af):
    if inspect.isfunction(obj) and obj.__module__ == 'analysis.all_functions':
        if "chart" in name or "by_season" in name or "_breakdown" in name or "run_rate_by_over" in name:
            view_type = "chart"
        elif "top_" in name or "compare_" in name or "_details" in name or "names" in name or "years" in name or "table" in name or "summary" in name or "closest_match" in name or "biggest_win" in name or "partnership_analysis" in name or "bowler_vs_batsman" in name or "venue_toss_decision" in name or "team_head_to_head" in name or "batsman_average_against_bowling_style" in name or "batsman_runs_in_innings_phase" in name or "batsman_performance_against_team" in name or "batsman_innings_with_most_fours" in name or "batsman_innings_with_most_sixes" in name or "batsman_fastest_strike_rate_innings" in name or "batsman_slowest_strike_rate_innings" in name or "bowler_wickets_against_batting_style" in name or "bowler_dot_ball_percentage_in_phase" in name or "bowler_performance_against_team" in name or "bowler_best_economy_innings" in name or "bowler_worst_economy_innings" in name or "bowler_best_figures_match" in name:
            view_type = "table"
        else:
            view_type = "metric"
            
        TOOL_MAPPING[name] = {"func": obj, "view_type": view_type}

def clean_output(obj, max_records=10):
    if isinstance(obj, pd.DataFrame):
        obj_capped = obj.head(max_records)
        return obj_capped.fillna('').to_dict(orient='records')
    elif isinstance(obj, pd.Series):
        return obj.fillna('').to_dict()
    elif isinstance(obj, np.generic):
        return obj.item()
    elif isinstance(obj, dict):
        return {k: clean_output(v, max_records) for k, v in obj.items()}
    elif isinstance(obj, list):
        capped = obj[:max_records]
        return [clean_output(v, max_records) for v in capped]
    return obj

def execute_tool_call(func_name, args):
    if func_name not in TOOL_MAPPING:
        return None
    func_info = TOOL_MAPPING[func_name]
    parsed_args = {}
    for k, v in args.items():
        if isinstance(v, str):
            v_str = v.strip()
            if 'team' in k or k in ['opponent', 'opposing_team', 'team1', 'team2', 'team_a', 'team_b']:
                v_str = resolve_team_name(v_str)
            elif 'player' in k or k in ['batsman', 'bowler', 'striker', 'player1', 'player2']:
                v_str = resolve_player_name(v_str)
            elif 'venue' in k or k in ['stadium']:
                v_str = resolve_venue_name(v_str)
            if v_str.isdigit() or (v_str.startswith('-') and v_str[1:].isdigit()):
                parsed_args[k] = int(v_str)
            else:
                try:
                    val = float(v_str)
                    parsed_args[k] = int(val) if val.is_integer() else val
                except ValueError:
                    parsed_args[k] = v_str
        else:
            parsed_args[k] = v
            
    raw_res = func_info["func"](**parsed_args)
    return {
        "title": func_name.replace("_", " ").title(),
        "view_type": func_info["view_type"],
        "data": clean_output(raw_res)
    }

def package_multiple_results(query, results):
    valid_results = [r for r in results if r is not None and r.get("data") is not None]
    if not valid_results:
        return jsonify({"error": "No data returned"}), 400
    if len(valid_results) == 1:
        return jsonify(valid_results[0])
        
    dashboard_data = {}
    for r in valid_results:
        title = r["title"]
        data = r["data"]
        dashboard_data[title] = data
        
    return jsonify({
        "view_type": "dashboard",
        "title": query.strip().title(),
        "data": dashboard_data
    })

def rule_based_fallback(query):
    # Normalize common misspellings (e.g. 'baller' -> 'bowler', 'bounders' -> 'boundary')
    q = query.lower()
    q = re.sub(r'\bballer(s)?\b', r'bowler\1', q)
    q = re.sub(r'\bboller(s)?\b', r'bowler\1', q)
    q = re.sub(r'\bbounder(s)?\b', r'boundary', q)
    q = re.sub(r'\bboundarie(s)?\b', r'boundary', q)
    
    venue = extract_venue_from_query(query)
    team = extract_team_from_query(query)
    player = extract_player_from_query(query)
    
    numbers = re.findall(r'\b\d+\b', query)
    season = next((int(n) for n in numbers if len(n) == 4), None)
    
    top_n = 10
    if numbers:
        top_n = next((int(n) for n in numbers if len(n) < 4), 10)
    else:
        for word, val in WORD_NUMS.items():
            if re.search(r'\b' + word + r'\b', q):
                top_n = val
                break
                
    # Orange cap / Purple cap
    if "orange cap" in q:
        res = execute_tool_call("top_run_scorers", {"top_n": 1, "s": season})
        return package_multiple_results("Orange Cap Winner (Most Runs)", [res])
    if "purple cap" in q:
        res = execute_tool_call("top_wicket_takers", {"top_n": 1})
        return package_multiple_results("Purple Cap Winner (Most Wickets)", [res])

    # 1. Compare queries
    if "compare" in q or " vs " in q or " versus " in q:
        teams_found = []
        for alias, official in TEAM_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', q) and official not in teams_found:
                teams_found.append(official)
        if len(teams_found) >= 2:
            res = execute_tool_call("compare_teams", {"team1": teams_found[0], "team2": teams_found[1]})
            return package_multiple_results(query, [res])
            
    # 2. Stadium / Venue Queries
    if venue:
        res1 = execute_tool_call("venue_total_matches", {"venue": venue})
        res2 = execute_tool_call("venue_average_score", {"venue": venue})
        res3 = execute_tool_call("highest_team_total_at_venue", {"venue": venue})
        res4 = execute_tool_call("lowest_team_total_at_venue", {"venue": venue})
        res5 = execute_tool_call("venue_batting_first_win_percentage", {"venue": venue})
        res6 = execute_tool_call("venue_toss_decision_impact", {"venue": venue})
        return package_multiple_results(f"{venue} Overview & Performance", [res1, res2, res3, res4, res5, res6])

    # 3. General Team Overview
    if team and ("stat" in q or "about" in q or "info" in q or "overview" in q or len(q.split()) <= 3):
        res1 = execute_tool_call("team_total_matches", {"team": team})
        res2 = execute_tool_call("team_total_wins", {"team": team})
        res3 = execute_tool_call("team_win_percentage", {"team": team})
        res4 = execute_tool_call("team_highest_score", {"team": team})
        return package_multiple_results(f"{team} Performance Overview", [res1, res2, res3, res4])

    # 4. Specific Team queries
    if team:
        if "match" in q:
            return package_multiple_results(query, [execute_tool_call("team_total_matches", {"team": team})])
        elif "win" in q and ("percent" in q or "%" in q or "rate" in q):
            return package_multiple_results(query, [execute_tool_call("team_win_percentage", {"team": team})])
        elif "win" in q:
            return package_multiple_results(query, [execute_tool_call("team_total_wins", {"team": team})])
        elif "highest" in q or "max" in q:
            return package_multiple_results(query, [execute_tool_call("team_highest_score", {"team": team})])
        elif "lowest" in q or "min" in q:
            return package_multiple_results(query, [execute_tool_call("team_lowest_score", {"team": team})])
        elif "avg" in q or "average" in q:
            return package_multiple_results(query, [execute_tool_call("team_average_score", {"team": team})])

    # 5. Death Overs Economy Check
    if player and ("death" in q or "16-20" in q or "16 to 20" in q):
        return package_multiple_results(query, [execute_tool_call("player_economy_death_overs", {"player": player})])

    # 6. Player Boundaries / Fours / Sixes
    if player and (re.search(r'\b(four|fours|six|sixes|4|6)\b', q) or "bound" in q):
        res1 = execute_tool_call("player_fours", {"player": player})
        res2 = execute_tool_call("player_sixes", {"player": player})
        res3 = execute_tool_call("player_boundaries_per_innings", {"player": player})
        res4 = execute_tool_call("boundary_percentage", {"player": player})
        return package_multiple_results(f"{player} Boundary Statistics", [res1, res2, res3, res4])

    # 6. General Player Overview
    if player and ("stat" in q or "about" in q or "info" in q or "overview" in q or len(q.split()) <= 3):
        res1 = execute_tool_call("player_total_runs", {"player": player})
        res2 = execute_tool_call("player_average", {"player": player})
        res3 = execute_tool_call("player_highest_score", {"player": player})
        res4 = execute_tool_call("player_centuries", {"player": player})
        return package_multiple_results(f"{player} Career Overview", [res1, res2, res3, res4])

    # 7. Specific Player queries
    if player:
        if "wicket" in q or "bowl" in q:
            return package_multiple_results(query, [execute_tool_call("player_total_wickets", {"player": player})])
        elif "run" in q or "score" in q or "bat" in q:
            return package_multiple_results(query, [execute_tool_call("player_total_runs", {"player": player})])
        elif "average" in q or "avg" in q:
            return package_multiple_results(query, [execute_tool_call("player_average", {"player": player})])

    # 8. Top Rankings & Leaderboards
    if "top team" in q or ("team" in q and ("win percentage" in q or "win %" in q or "win pct" in q or "best team" in q)):
        return package_multiple_results(query, [execute_tool_call("top_teams_by_win_percentage", {"top_n": top_n})])

    if "top" in q or "most" in q or "highest" in q or "best" in q:
        if ("run" in q or "batsman" in q or "scorer" in q) and ("wicket" in q or "bowler" in q):
            res1 = execute_tool_call("top_run_scorers", {"top_n": top_n, "s": season})
            res2 = execute_tool_call("top_wicket_takers", {"top_n": top_n})
            return package_multiple_results(f"Top IPL Performers", [res1, res2])
        elif "wicket" in q or "bowler" in q or "bowl" in q:
            return package_multiple_results(query, [execute_tool_call("top_wicket_takers", {"top_n": top_n})])
        elif "run" in q or "batsman" in q or "scorer" in q or "score" in q:
            return package_multiple_results(query, [execute_tool_call("top_run_scorers", {"top_n": top_n, "s": season})])

    # 9. Death Overs / Economy / Specific Player Analytics
    if player:
        if "death" in q or "16-20" in q or "16 to 20" in q:
            return package_multiple_results(query, [execute_tool_call("player_economy_death_overs", {"player": player})])
        elif "chase" in q and ("strike" in q or "rate" in q or "sr" in q):
            return package_multiple_results(query, [execute_tool_call("player_strike_rate_in_successful_chases", {"player": player})])
        elif "strike rate" in q or "sr" in q:
            return package_multiple_results(query, [execute_tool_call("player_strike_rate", {"player": player})])
        elif "dot" in q or "dot ball" in q:
            return package_multiple_results(query, [execute_tool_call("player_dot_ball_percentage", {"player": player})])
        elif "fifty" in q or "fifties" in q or "50" in q or "half centur" in q:
            return package_multiple_results(query, [execute_tool_call("player_fifties", {"player": player})])
        elif team:
            return package_multiple_results(query, [execute_tool_call("player_stats_against_team", {"player": player, "team": team})])
        elif venue:
            return package_multiple_results(query, [execute_tool_call("player_stats_at_venue", {"player": player, "venue": venue})])

    # 10. Head to Head / Chases / Record Matches
    if "head to head" in q or "h2h" in q:
        teams_found = []
        for alias, official in TEAM_ALIASES.items():
            if re.search(r'\b' + re.escape(alias) + r'\b', q) and official not in teams_found:
                teams_found.append(official)
        if len(teams_found) >= 2:
            return package_multiple_results(query, [execute_tool_call("head_to_head", {"team1": teams_found[0], "team2": teams_found[1]})])

    if "chase" in q:
        return package_multiple_results(query, [execute_tool_call("highest_successful_chase", {})])

    if "closest" in q or "narrowest" in q:
        return package_multiple_results(query, [execute_tool_call("closest_margin_match", {})])

    if "biggest" in q or "largest" in q:
        return package_multiple_results(query, [execute_tool_call("biggest_win_by_runs", {})])

    if "unique" in q or "all team" in q or "teams" in q:
        return package_multiple_results(query, [execute_tool_call("unique_teams", {})])

    # 11. Season Summary
    if season and ("summary" in q or "season" in q or "info" in q or "stats" in q or "orange" in q):
        return package_multiple_results(query, [execute_tool_call("season_summary", {"season": season})])

    # Default: Return Top Run Scorers and Top Wicket Takers dashboard
    res1 = execute_tool_call("top_run_scorers", {"top_n": 5})
    res2 = execute_tool_call("top_wicket_takers", {"top_n": 5})
    return package_multiple_results("IPL Overall Overview", [res1, res2])

ROUTER_SYSTEM_PROMPT = """
You are an expert IPL Analytics Assistant.
Your task is to analyze the user query and return a JSON list of function calls to execute to answer the query thoroughly.

TEAM NAME MAP (Always convert short forms/cities to official team names):
- "CSK" / "Chennai" -> "Chennai Super Kings"
- "MI" / "Mumbai" -> "Mumbai Indians"
- "RCB" / "Bangalore" -> "Royal Challengers Bangalore"
- "KKR" / "Kolkata" -> "Kolkata Knight Riders"
- "SRH" / "Hyderabad" -> "Sunrisers Hyderabad"
- "DC" / "Delhi" -> "Delhi Capitals"
- "RR" / "Rajasthan" -> "Rajasthan Royals"
- "PBKS" / "KXIP" / "Punjab" -> "Punjab Kings"
- "GT" / "Gujarat" -> "Gujarat Titans"
- "LSG" / "Lucknow" -> "Lucknow Super Giants"

VENUE NAME MAP:
- "Wankhede" -> "Wankhede Stadium"
- "Eden" / "Eden Gardens" -> "Eden Gardens"
- "Chinnaswamy" -> "Chinnaswamy Stadium"
- "Chepauk" / "Chidambaram" -> "M. A. Chidambaram Stadium"
- "Motera" / "Narendra Modi" -> "Narendra Modi Stadium"
- "Kotla" / "Arun Jaitley" -> "Arun Jaitley Stadium"

AVAILABLE FUNCTIONS CATALOG:
1. Player Analytics & Boundaries:
- player_fours(player)
- player_sixes(player)
- player_boundaries_per_innings(player)
- boundary_percentage(player)
- player_total_runs(player)
- player_average(player)
- player_highest_score(player)
- player_centuries(player)
- player_fifties(player)
- player_runs_by_season(player)
- player_stats_against_team(player, team)
- player_stats_at_venue(player, venue)
- player_total_wickets(player)
- player_economy(player)
- player_bowling_strike_rate(player)
- player_wickets_by_season(player)
- player_wickets_against_team(player, team)
- player_dot_ball_percentage(player)
- player_strike_rate(player)
- player_strike_rate_in_successful_chases(player)
- player_economy_death_overs(player)
- compare_batsmen(player1, player2)
- compare_bowlers(player1, player2)

2. Stadium / Venue Analytics:
- venue_total_matches(venue)
- venue_average_score(venue)
- highest_team_total_at_venue(venue)
- lowest_team_total_at_venue(venue)
- venue_batting_first_win_percentage(venue)
- venue_toss_decision_impact(venue)

3. Team Analytics:
- team_total_matches(team)
- team_total_wins(team)
- team_win_percentage(team)
- team_highest_score(team)
- team_lowest_score(team)
- top_teams_by_win_percentage(top_n)
- team_win_percentage_after_winning_toss(team)
- head_to_head(team1, team2)
- compare_teams(team1, team2)
- unique_teams()

4. Leaderboards & Record Matches:
- top_run_scorers(top_n, s)
- top_wicket_takers(top_n)
- highest_successful_chase()
- closest_margin_match()
- biggest_win_by_runs()

INSTRUCTIONS:
1. If the user asks about boundaries, bounders, 4s, 6s or boundary percentage for a player, call `player_fours`, `player_sixes`, `player_boundaries_per_innings`, and `boundary_percentage`.
2. If the user asks about economy in death overs (16-20), call `player_economy_death_overs`.
3. If the user asks for top teams by win percentage, call `top_teams_by_win_percentage`.
4. Format your response strictly as a JSON array of objects:
[
  {"func": "function_name", "args": {"param1": "value1"}}
]
"""

@search_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data.get('query')
    
    if not query:
        return jsonify({"error": "No query provided"}), 400
        
    models_to_try = ['gemini-2.0-flash', 'gemini-2.0-flash-lite-001']
    
    for model_name in models_to_try:
        try:
            client = get_gemini_client()
            prompt = f"{ROUTER_SYSTEM_PROMPT}\nUser Query: {query}"
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            calls = json.loads(response.text)
            if isinstance(calls, list) and len(calls) > 0:
                results = []
                for call in calls:
                    fn = call.get("func")
                    args = call.get("args", {})
                    res = execute_tool_call(fn, args)
                    if res:
                        results.append(res)
                if results:
                    return package_multiple_results(query, results)
                    
        except Exception as e:
            err_msg = str(e)
            print(f"Model {model_name} failed: {err_msg}")
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                continue
            else:
                break

    print("Using smart dashboard fallback router for query:", query)
    return rule_based_fallback(query)
