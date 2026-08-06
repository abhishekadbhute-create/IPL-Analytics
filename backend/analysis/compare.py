import pandas as pd
from utils.data_loader import matches, deliveries

def compare_batsmen(player1, player2):
    def stats(player):
        df = deliveries[deliveries['striker'] == player]
        if df.empty:
            return {"error": "No data found"}
        total_runs = df['batsman_runs'].sum()
        balls = df.shape[0]
        matches_played = df['match_id'].nunique()
        fours = df[df['batsman_runs'] == 4].shape[0]
        sixes = df[df['batsman_runs'] == 6].shape[0]
        strike_rate = round((total_runs / balls) * 100, 2) if balls > 0 else 0
        average = round(total_runs / matches_played, 2) if matches_played > 0 else 0
        runs_per_match = df.groupby('match_id')['batsman_runs'].sum()
        fifties = runs_per_match[(runs_per_match >= 50) & (runs_per_match < 100)].shape[0]
        centuries = runs_per_match[runs_per_match >= 100].shape[0]
        return {
            "player": player,
            "total_runs": int(total_runs),
            "balls_faced": int(balls),
            "matches_played": int(matches_played),
            "average": float(average),
            "strike_rate": float(strike_rate),
            "fours": int(fours),
            "sixes": int(sixes),
            "fifties": int(fifties),
            "centuries": int(centuries)
        }
    return {"player1": stats(player1), "player2": stats(player2)}

def compare_bowlers(player1, player2):
    def stats(player):
        df = deliveries[deliveries['bowler'] == player]
        if df.empty:
            return {"error": "No data found"}
        balls = df.shape[0]
        overs = balls / 6
        runs_conceded = df['total_runs'].sum()
        wickets = df[df['is_wicket'] == 1].shape[0]
        matches_played = df['match_id'].nunique()
        economy = round(runs_conceded / overs, 2) if overs > 0 else 0
        average = round(runs_conceded / wickets, 2) if wickets > 0 else 0
        strike_rate = round(balls / wickets, 2) if wickets > 0 else 0
        return {
            "player": player,
            "matches_played": int(matches_played),
            "balls_bowled": int(balls),
            "runs_conceded": int(runs_conceded),
            "wickets": int(wickets),
            "economy": float(economy),
            "average": float(average),
            "strike_rate": float(strike_rate)
        }
    return {"player1": stats(player1), "player2": stats(player2)}

def compare_teams(team1, team2):
    def stats(team):
        matches_played = matches[(matches['team1'] == team) | (matches['team2'] == team)]
        total_matches = matches_played.shape[0]
        if total_matches == 0:
            return {"error": "No data found"}
        wins = matches[matches['winner'] == team].shape[0]
        losses = total_matches - wins
        win_pct = round((wins / total_matches) * 100, 2) if total_matches > 0 else 0
        team_deliveries = deliveries[deliveries['batting_team'] == team]
        totals = team_deliveries.groupby(['match_id', 'innings'])['total_runs'].sum()
        highest_total = totals.max() if not totals.empty else 0
        lowest_total = totals.min() if not totals.empty else 0
        avg_total = round(totals.mean(), 2) if not totals.empty else 0
        return {
            "team": team,
            "matches_played": int(total_matches),
            "wins": int(wins),
            "losses": int(losses),
            "win_percentage": float(win_pct),
            "highest_total": int(highest_total),
            "lowest_total": int(lowest_total),
            "average_total": float(avg_total)
        }
    return {"team1": stats(team1), "team2": stats(team2)}

def compare_venues(venue1, venue2):
    def stats(venue):
        venue_matches = matches[matches['venue'] == venue]
        total_matches = venue_matches.shape[0]
        if total_matches == 0:
            return {"error": "No data found"}
        avg_first_innings = round(venue_matches['first_innings_score'].mean(), 2) if total_matches > 0 else 0
        if pd.isna(avg_first_innings): avg_first_innings = 0
        avg_second_innings = round(venue_matches['second_innings_score'].mean(), 2) if total_matches > 0 else 0
        if pd.isna(avg_second_innings): avg_second_innings = 0
        bat_first_wins = venue_matches[venue_matches['winner'] == venue_matches['team1']].shape[0]
        chase_wins = venue_matches[venue_matches['winner'] == venue_matches['team2']].shape[0]
        highest_total = max(venue_matches['first_innings_score'].max(), venue_matches['second_innings_score'].max()) if total_matches > 0 else 0
        if pd.isna(highest_total): highest_total = 0
        return {
            "venue": venue,
            "matches_played": int(total_matches),
            "avg_first_innings_score": float(avg_first_innings),
            "avg_second_innings_score": float(avg_second_innings),
            "bat_first_wins": int(bat_first_wins),
            "chase_wins": int(chase_wins),
            "highest_total": int(highest_total)
        }
    return {"venue1": stats(venue1), "venue2": stats(venue2)}

def compare_seasons(season1, season2):
    def stats(season):
        season_matches = matches[matches['season'] == int(season)]
        total_matches = season_matches.shape[0]
        if total_matches == 0:
            return {"error": "No data found"}
        season_deliveries = deliveries[deliveries['match_id'].isin(season_matches['match_id'])]
        total_runs = season_deliveries['total_runs'].sum()
        total_wickets = season_deliveries[season_deliveries['is_wicket'] == 1].shape[0]
        totals = season_deliveries.groupby(['match_id', 'innings'])['total_runs'].sum()
        highest_total = totals.max() if not totals.empty else 0
        avg_runs_per_match = round(total_runs / total_matches, 2) if total_matches > 0 else 0
        return {
            "season": int(season),
            "matches_played": int(total_matches),
            "total_runs": int(total_runs),
            "total_wickets": int(total_wickets),
            "highest_total": int(highest_total),
            "avg_runs_per_match": float(avg_runs_per_match)
        }
    return {"season1": stats(season1), "season2": stats(season2)}
