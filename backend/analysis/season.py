import pandas as pd
from utils.data_loader import seasons

def season_summary(season):
    a = seasons[seasons['season'] == season]
    if len(a) == 0:
        return {"error": "Season not found"}

    row = a.iloc[0]
    return {
        "season": int(row['season']),
        "total_matches": int(row['total_matches']),
        "total_runs": int(row['total_runs_scored']),
        "average_score": float(row['avg_first_innings_score']),
        "highest_score": int(row['highest_team_total']),
        "lowest_score": int(row['lowest_team_total']),
        "champion": str(row['champion']),
        "runner_up": str(row['runner_up']),
        "most_sixes": int(row['total_sixes']),
        "most_fours": int(row['total_fours']),
        "orange_cap_winner": str(row['orange_cap_winner']),
        "purple_cap_winner": str(row['purple_cap_winner']),
        "most_valuable_player": str(row['most_valuable_player'])
    }
