import pandas as pd
import numpy as np
from utils.data_loader import matches, deliveries

def team_total_matches(team):
    a = matches['team1'].value_counts().get(team, 0) + matches['team2'].value_counts().get(team, 0)
    return {"team": team, "total_matches": int(a)}

def team_total_wins(team):
    a = matches['winner'].value_counts().get(team, 0)
    return {"team": team, "total_wins": int(a)}

def team_win_percentage(team):
    a = matches['team1'].value_counts().get(team, 0) + matches['team2'].value_counts().get(team, 0)
    b = matches['winner'].value_counts().get(team, 0)
    pct = (b / a * 100) if a > 0 else 0
    return {"team": team, "win_percentage": float(round(pct, 2))}

def team_highest_score(team, opponent=None):
    scores = deliveries.groupby(["match_id", "innings", "batting_team"])["total_runs"].sum().reset_index(name="score")
    team_df = scores[scores["batting_team"] == team]
    
    if opponent is not None:
        ids = matches[
            ((matches["team1"] == team) & (matches["team2"] == opponent)) |
            ((matches["team1"] == opponent) & (matches["team2"] == team))
        ]["match_id"]
        team_df = team_df[team_df["match_id"].isin(ids)]
        
    if team_df.empty:
        return {"error": "No data found"}
        
    highest = team_df.loc[team_df["score"].idxmax()]
    match = matches[matches["match_id"] == highest["match_id"]].iloc[0]
    opp = match["team2"] if match["team1"] == team else match["team1"]
    
    return {
        "score": int(highest["score"]),
        "opponent": str(opp),
        "season": int(match["season"]),
        "venue": str(match["venue"]),
        "winner": str(match["winner"])
    }

def team_lowest_score(team, opponent=None):
    scores = deliveries.groupby(["match_id", "innings", "batting_team"])["total_runs"].sum().reset_index(name="score")
    team_df = scores[scores["batting_team"] == team]
    
    if opponent is not None:
        ids = matches[
            ((matches["team1"] == team) & (matches["team2"] == opponent)) |
            ((matches["team1"] == opponent) & (matches["team2"] == team))
        ]["match_id"]
        team_df = team_df[team_df["match_id"].isin(ids)]
        
    if team_df.empty:
        return {"error": "No data found"}
        
    lowest = team_df.loc[team_df["score"].idxmin()]
    match = matches[matches["match_id"] == lowest["match_id"]].iloc[0]
    opp = match["team2"] if match["team1"] == team else match["team1"]
    
    return {
        "score": int(lowest["score"]),
        "opponent": str(opp),
        "season": int(match["season"]),
        "venue": str(match["venue"]),
        "winner": str(match["winner"])
    }

def team_average_score(team):
    a = deliveries.groupby('batting_team')['total_runs'].sum().get(team, 0)
    b = matches['team1'].value_counts().get(team, 0) + matches['team2'].value_counts().get(team, 0)
    avg = a / b if b > 0 else 0
    
    try:
        highest = team_highest_score(team).get("score", 0)
        lowest = team_lowest_score(team).get("score", 0)
    except:
        highest = 0
        lowest = 0
        
    return {
        "team": team,
        "average_score": float(round(avg, 2)),
        "highest_score": highest,
        "lowest_score": lowest
    }

def team_head_to_head(team_a, team_b):
    h2h = matches[((matches['team1']==team_a) & (matches['team2']==team_b)) | ((matches['team1']==team_b) & (matches['team2']==team_a))]
    total_matches = len(h2h)
    wins_a = len(h2h[h2h['winner']==team_a])
    wins_b = len(h2h[h2h['winner']==team_b])
    no_result = len(h2h[h2h['winner'].isna()])
    
    highest_a = team_highest_score(team_a, team_b).get("score", 0)
    highest_b = team_highest_score(team_b, team_a).get("score", 0)
    lowest_a = team_lowest_score(team_a, team_b).get("score", 0)
    lowest_b = team_lowest_score(team_b, team_a).get("score", 0)
    
    season_graph = h2h.groupby(["season", "winner"]).size().reset_index(name="wins").to_dict(orient="records")
    match_history = h2h.sort_values(by=["season", "match_number"], ascending=False)[
        ["season", "match_number", "team1", "team2", "winner", "result", "venue", "toss_winner", "player_of_match"]
    ].reset_index(drop=True).fillna("").to_dict(orient="records")
    
    return {
        "matches": int(total_matches),
        "team1_wins": int(wins_a),
        "team2_wins": int(wins_b),
        "no_result": int(no_result),
        "highest_team1": int(highest_a),
        "highest_team2": int(highest_b),
        "lowest_team1": int(lowest_a),
        "lowest_team2": int(lowest_b),
        "season_graph": season_graph,
        "match_history": match_history
    }

def _team_innings_totals():
    totals = deliveries.groupby(['match_id', 'innings', 'batting_team'])['total_runs'].sum().reset_index()
    totals = totals.merge(matches[['match_id', 'season', 'venue', 'city', 'date']], on='match_id', how='left')
    return totals

def highest_team_total():
    totals = _team_innings_totals()
    row = totals.loc[totals['total_runs'].idxmax()]
    return {
        "team": str(row['batting_team']),
        "total_runs": int(row['total_runs']),
        "match_id": str(row['match_id']),
        "season": int(row['season']),
        "venue": str(row['venue']),
        "date": str(row['date'])
    }

def lowest_team_total():
    totals = _team_innings_totals()
    row = totals.loc[totals['total_runs'].idxmin()]
    return {
        "team": str(row['batting_team']),
        "total_runs": int(row['total_runs']),
        "match_id": str(row['match_id']),
        "season": int(row['season']),
        "venue": str(row['venue']),
        "date": str(row['date'])
    }

def partnership_analysis(team):
    team_deliveries = deliveries[deliveries['batting_team'] == team].copy()
    if team_deliveries.empty:
        return {"error": f"No data found for team '{team}'"}

    partnerships = []

    for match_id, match_df in team_deliveries.groupby('match_id'):
        for innings, inn_df in match_df.groupby('innings'):
            inn_df = inn_df.sort_values(['over', 'ball'])
            current_pair = tuple(sorted([inn_df.iloc[0]['striker'], inn_df.iloc[0]['non_striker']]))
            partnership_runs = 0
            balls_faced = 0

            for _, ball in inn_df.iterrows():
                pair = tuple(sorted([ball['striker'], ball['non_striker']]))
                if pair != current_pair:
                    partnerships.append({
                        "match_id": match_id,
                        "innings": innings,
                        "batsmen": f"{current_pair[0]} & {current_pair[1]}",
                        "runs": partnership_runs,
                        "balls": balls_faced
                    })
                    current_pair = pair
                    partnership_runs = 0
                    balls_faced = 0

                partnership_runs += ball['total_runs']
                balls_faced += 1

            partnerships.append({
                "match_id": match_id,
                "innings": innings,
                "batsmen": f"{current_pair[0]} & {current_pair[1]}",
                "runs": partnership_runs,
                "balls": balls_faced
            })

    partnerships_df = pd.DataFrame(partnerships)
    summary = (
        partnerships_df.groupby('batsmen')
        .agg(total_runs=('runs', 'sum'), partnerships_count=('runs', 'count'), avg_runs=('runs', 'mean'))
        .sort_values('total_runs', ascending=False)
        .reset_index()
    )

    if summary.empty:
        return {"error": "No partnerships found"}
        
    best = summary.iloc[0]

    return {
        "team": team,
        "best_partnership_pair": best['batsmen'],
        "total_runs": int(best['total_runs']),
        "partnerships_count": int(best['partnerships_count']),
        "avg_runs": float(round(best['avg_runs'], 2)),
        "all_partnerships": summary.head(20).to_dict(orient="records")
    }
