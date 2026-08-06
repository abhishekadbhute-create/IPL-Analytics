import pandas as pd
from utils.data_loader import matches

def venue_total_matches(venue):
    count = matches[matches['venue']==venue].shape[0]
    return {"venue": venue, "total_matches": int(count)}

def venue_average_score(venue):
    venue_matches = matches[matches['venue'] == venue]
    avg = venue_matches['first_innings_score'].mean()
    if pd.isna(avg): avg = 0
    return {
        "venue": venue,
        "average_score": float(round(avg, 1))
    }

def highest_team_total_at_venue(venue):
    df = matches[matches['venue'] == venue]
    highest_score = -1
    team = against = season = None

    for _, row in df.iterrows():
        if not pd.isna(row.get('first_innings_score', None)) and row['first_innings_score'] > highest_score:
            highest_score = row['first_innings_score']
            team = row['team1']
            against = row['team2']
            season = row['season']
        
        if not pd.isna(row.get('second_innings_score', None)) and row['second_innings_score'] > highest_score:
            highest_score = row['second_innings_score']
            team = row['team2']
            against = row['team1']
            season = row['season']

    if highest_score == -1:
        return {"error": "No data found"}

    return {
        "score": int(highest_score),
        "team": team,
        "against": against,
        "season": int(season)
    }

def lowest_team_total_at_venue(venue):
    venue_matches = matches[matches['venue'] == venue]
    lowest_score = float('inf')
    team = against = season = None

    for _, row in venue_matches.iterrows():
        if not pd.isna(row.get('first_innings_score', None)) and row['first_innings_score'] < lowest_score:
            lowest_score = row['first_innings_score']
            team = row['team1']
            against = row['team2']
            season = row['season']

        if not pd.isna(row.get('second_innings_score', None)) and row['second_innings_score'] < lowest_score:
            lowest_score = row['second_innings_score']
            team = row['team2']
            against = row['team1']
            season = row['season']

    if lowest_score == float('inf'):
        return {"error": "No data found"}

    return {
        "score": int(lowest_score),
        "team": team,
        "against": against,
        "season": int(season)
    }

def venue_batting_first_win_percentage(venue):
    venue_matches = matches[matches['venue']==venue]
    if len(venue_matches) == 0:
        return {"venue": venue, "batting_first_win_percentage": 0.0}
    
    batting_first_wins = venue_matches[venue_matches['win_by']=='runs']
    percentage = (len(batting_first_wins) / len(venue_matches)) * 100
    return {"venue": venue, "batting_first_win_percentage": float(round(percentage, 2))}

def venue_chasing_win_percentage(venue):
    venue_matches = matches[matches['venue']==venue]
    if len(venue_matches) == 0:
        return {"venue": venue, "chasing_win_percentage": 0.0}
    
    chasing_wins = venue_matches[venue_matches['win_by']=='wickets']
    percentage = (len(chasing_wins) / len(venue_matches)) * 100
    return {"venue": venue, "chasing_win_percentage": float(round(percentage, 2))}
