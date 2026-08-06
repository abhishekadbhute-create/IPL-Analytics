import pandas as pd
import numpy as np
from utils.data_loader import matches, deliveries

def top_run_scorers(top_n, s):
    a = deliveries.merge(matches, on='match_id')
    top_run = a[a['season']==s].groupby(['striker'])['batsman_runs'].sum().sort_values(ascending=False).head(top_n).reset_index()
    season_df = a[a['season']==s]
    balls = season_df[season_df['extra_type']!='wides'].groupby('striker').size().rename('balls')
    runs = season_df.groupby('striker')['batsman_runs'].sum().rename('runs')
    strike_rate = ((runs/balls)*100).round(2).rename('strike_rate')
    stats = pd.concat([runs, balls, strike_rate], axis=1).reset_index()
    top_run = stats.sort_values('runs', ascending=False).head(top_n)
    return top_run.to_dict(orient='records')

def player_total_runs(player):
    runs = deliveries[deliveries['striker']==player]['batsman_runs'].sum()
    return {"player": player, "total_runs": int(runs)}

def player_average(player):
    played = deliveries[deliveries['striker']==player]['match_id'].nunique()
    total_runs = deliveries[deliveries['striker']==player]['batsman_runs'].sum()
    avg = total_runs / played if played > 0 else 0
    return {"player": player, "average": float(round(avg, 2))}

def player_highest_score(player):
    highest = deliveries[deliveries['striker']==player].groupby('match_id').sum(numeric_only=True)['batsman_runs'].max()
    if pd.isna(highest): highest = 0
    return {"player": player, "highest_score": int(highest)}

def player_centuries(player):
    runs = (
        deliveries[deliveries['striker'] == player]
        .groupby(['match_id', 'innings'])['batsman_runs']
        .sum()
    )
    centuries = (runs >= 100).sum()
    return {"player": player, "centuries": int(centuries)}

def player_half_centuries(player):
    runs = (
        deliveries[deliveries['striker'] == player]
        .groupby(['match_id', 'innings'])['batsman_runs']
        .sum()
    )
    fifties = ((runs >= 50) & (runs < 100)).sum()
    return {"player": player, "fifties": int(fifties)}

def player_sixes(player):
    a = deliveries[deliveries['striker']==player]
    sixes = a[a['batsman_runs']==6].shape[0]
    return {"player": player, "sixes": int(sixes)}

def player_fours(player):
    a = deliveries[deliveries['striker']==player]
    fours = a[a['batsman_runs']==4].shape[0]
    return {"player": player, "fours": int(fours)}

def player_runs_by_season(player):
    merged = deliveries.merge(matches[['match_id', 'season']], on='match_id')
    runs = merged[merged['striker']==player].groupby('season')['batsman_runs'].sum().reset_index()
    return runs.to_dict(orient='records')

def player_runs_against_team(player, team):
    a = deliveries[(deliveries['bowling_team'] == team) & (deliveries['striker'] == player)]
    innings_data = a.groupby(['match_id', 'innings'])['batsman_runs'].sum().reset_index()
    matches_count = innings_data['match_id'].nunique()
    innings_count = len(innings_data)
    runs = innings_data['batsman_runs'].sum()
    highest_score = innings_data['batsman_runs'].max()
    if pd.isna(highest_score): highest_score = 0
    balls = a[(a['extra_type'] != 'wides')].shape[0]
    strike_rate = (runs / balls * 100) if balls > 0 else 0
    dismissals = deliveries[(deliveries['dismissed_player'] == player) & (deliveries['bowling_team'] == team)].shape[0]
    average = runs / dismissals if dismissals > 0 else runs
    
    result = {
        'Player': player,
        'Against_Team': team,
        'Matches': int(matches_count),
        'Innings': int(innings_count),
        'Runs': int(runs),
        'Average': float(round(average, 2)),
        'Strike_Rate': float(round(strike_rate, 2)),
        'Highest_Score': int(highest_score)
    }
    return result

def player_runs_at_venue(player, venue):
    a = matches.merge(deliveries, on='match_id', how='inner')
    a = a[(a['venue'] == venue) & (a['striker'] == player)]
    total_matches = a['match_id'].nunique()
    innings_count = a.groupby(['match_id', 'innings']).ngroups
    runs = a['batsman_runs'].sum()
    dismissals = a[a['dismissed_player'] == player].shape[0]
    average = runs / dismissals if dismissals > 0 else runs
    balls = a[a['extra_type'] != 'wides'].shape[0]
    strike_rate = (runs / balls * 100) if balls > 0 else 0
    
    highest_score = a.groupby(['match_id', 'innings'])['batsman_runs'].sum().max()
    if pd.isna(highest_score): highest_score = 0
    
    result = {
        'Player': player,
        'Venue': venue,
        'Matches': int(total_matches),
        'Innings': int(innings_count),
        'Runs': int(runs),
        'Average': float(round(average, 2)),
        'Strike_Rate': float(round(strike_rate, 2)),
        'Highest_Score': int(highest_score)
    }
    return result

def boundary_percentage(player):
    player_df = deliveries[deliveries['striker'] == player]
    if player_df.empty:
        return {"error": f"No data found for player '{player}'"}
    
    total_runs = player_df['batsman_runs'].sum()
    fours = player_df[player_df['batsman_runs'] == 4].shape[0]
    sixes = player_df[player_df['batsman_runs'] == 6].shape[0]
    boundary_runs = (fours * 4) + (sixes * 6)
    percentage = (boundary_runs / total_runs * 100) if total_runs > 0 else 0
    
    return {
        "player": player,
        "total_runs": int(total_runs),
        "fours": int(fours),
        "sixes": int(sixes),
        "boundary_runs": int(boundary_runs),
        "boundary_percentage": float(round(percentage, 2))
    }
