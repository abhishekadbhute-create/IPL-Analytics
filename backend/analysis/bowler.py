import pandas as pd
import numpy as np
from utils.data_loader import matches, deliveries

def top_wicket_takers(top_n=10):
    wickets = deliveries.groupby('bowler')['is_wicket'].sum()
    match_counts = deliveries.groupby('bowler')['match_id'].nunique()
    result = pd.DataFrame({
        'Player': wickets.index,
        'Wickets': wickets.values,
        'Matches': match_counts.values
    })
    top = result.sort_values('Wickets', ascending=False).head(top_n).reset_index(drop=True)
    return top.to_dict(orient='records')

def player_total_wickets(player):
    wickets = deliveries[deliveries['bowler']==player]['is_wicket'].sum()
    return {"player": player, "total_wickets": int(wickets)}

def player_economy(player):
    run = deliveries.groupby('bowler')['total_runs'].sum().get(player, 0)
    overs = len(deliveries[deliveries['bowler']==player]) / 6
    eco = run / overs if overs > 0 else 0
    return {"player": player, "economy": float(round(eco, 2))}

def player_bowling_average(player):
    run = deliveries.groupby('bowler')['total_runs'].sum().get(player, 0)
    wicket = deliveries[deliveries['bowler']==player]['is_wicket'].sum()
    avg = run / wicket if wicket > 0 else 0
    return {"player": player, "bowling_average": float(round(avg, 2))}

def player_bowling_strike_rate(player):
    balls = len(deliveries[deliveries['bowler']==player])
    wicket = deliveries[deliveries['bowler']==player]['is_wicket'].sum()
    sr = balls / wicket if wicket > 0 else 0
    return {"player": player, "bowling_strike_rate": float(round(sr, 2))}

def player_best_figures(player):
    a = deliveries[deliveries['bowler']==player].groupby('match_id')['total_runs'].sum()
    b = deliveries[deliveries['bowler']==player].groupby('match_id')['is_wicket'].sum()
    
    if b.empty:
        return {"player": player, "best_figures": {"wickets": 0, "runs": 0}}
        
    df = pd.DataFrame({'wickets': b, 'runs': a})
    df = df.sort_values(by=['wickets', 'runs'], ascending=[False, True])
    best = df.iloc[0]
    return {"player": player, "best_figures": {"wickets": int(best['wickets']), "runs": int(best['runs'])}}

def player_wickets_by_season(player):
    a = matches.merge(deliveries, on='match_id')
    w = a[a['bowler']==player].groupby('season')['is_wicket'].sum().reset_index()
    return w.to_dict(orient='records')

def player_wickets_against_team(player, team):
    wickets = deliveries[(deliveries['batting_team']==team) & (deliveries['bowler']==player)]['is_wicket'].sum()
    return {"player": player, "against_team": team, "wickets": int(wickets)}

def player_dot_ball_percentage(player):
    b = deliveries[(deliveries['bowler']==player)].shape[0]
    a = deliveries[(deliveries['bowler']==player) & (deliveries['total_runs']==0)].shape[0]
    pct = (a / b * 100) if b > 0 else 0
    return {"player": player, "dot_ball_percentage": float(round(pct, 2))}

def bowler_vs_batsman(bowler, batsman):
    df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['striker'] == batsman)]
    balls_faced = df.shape[0]
    runs_scored = df['batsman_runs'].sum()
    wickets = df['is_wicket'].sum()
    dot_balls = (df['batsman_runs'] == 0).sum()
    strike_rate = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0
    boundaries_4 = (df['batsman_runs'] == 4).sum()
    boundaries_6 = (df['batsman_runs'] == 6).sum()
    return {
        "bowler": bowler,
        "batsman": batsman,
        "Balls Faced": int(balls_faced),
        "Runs Scored": int(runs_scored),
        "Wickets": int(wickets),
        "Dot Balls": int(dot_balls),
        "Strike Rate": float(round(strike_rate, 2)),
        "Boundaries": {
            "4s": int(boundaries_4),
            "6s": int(boundaries_6)
        }
    }
