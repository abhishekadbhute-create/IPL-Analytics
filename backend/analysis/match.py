import pandas as pd
from utils.data_loader import matches, deliveries

def run_rate_by_over(match_id):
    match_df = deliveries[deliveries['match_id'] == match_id]
    if match_df.empty:
        return {"error": f"No data found for match_id '{match_id}'"}

    over_runs = (
        match_df.groupby(['innings', 'over'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'runs_in_over'})
    )

    over_runs['run_rate'] = over_runs['runs_in_over']
    over_runs['cumulative_runs'] = over_runs.groupby('innings')['runs_in_over'].cumsum()
    over_runs['overs_completed'] = over_runs.groupby('innings').cumcount() + 1
    over_runs['cumulative_run_rate'] = round(over_runs['cumulative_runs'] / over_runs['overs_completed'], 2)

    return over_runs.to_dict(orient='records')

def win_probability(match_id):
    match_info = matches[matches['match_id'] == match_id]
    if match_info.empty:
        return {"error": f"No match found with match_id '{match_id}'"}
        
    match_info = match_info.iloc[0]

    target = match_info.get('first_innings_score', 0)
    if pd.isna(target):
        return {"error": "Missing first innings score"}
    target += 1
    
    second_innings = deliveries[(deliveries['match_id'] == match_id) & (deliveries['innings'] == 2)].copy()

    if second_innings.empty:
        return {"error": f"No second innings data found for match_id '{match_id}'"}

    second_innings = second_innings.sort_values(['over', 'ball'])
    second_innings['cumulative_runs'] = second_innings['total_runs'].cumsum()
    second_innings['balls_bowled'] = range(1, len(second_innings) + 1)
    second_innings['overs_bowled'] = second_innings['balls_bowled'] / 6

    total_overs = match_info.get('first_innings_overs', 20)
    if pd.isna(total_overs):
        total_overs = 20
        
    total_balls = total_overs * 6

    results = []
    for _, row in second_innings.iterrows():
        runs_scored = row['cumulative_runs']
        balls_bowled = row['balls_bowled']
        balls_remaining = total_balls - balls_bowled
        runs_needed = target - runs_scored

        current_rr = runs_scored / (balls_bowled / 6) if balls_bowled > 0 else 0
        required_rr = (runs_needed / (balls_remaining / 6)) if balls_remaining > 0 else float('inf')

        if balls_remaining <= 0 or runs_needed <= 0:
            win_prob = 100 if runs_needed <= 0 else 0
        else:
            diff = current_rr - required_rr
            win_prob = max(0, min(100, 50 + diff * 5))

        results.append({
            "over": int(row['over']),
            "ball": int(row['ball']),
            "runs_scored": int(runs_scored),
            "runs_needed": int(runs_needed),
            "current_run_rate": float(round(current_rr, 2)),
            "required_run_rate": float(round(required_rr, 2)) if balls_remaining > 0 else None,
            "chasing_team_win_probability": float(round(win_prob, 1))
        })

    return results

def highest_successful_chase():
    df = matches.copy()
    chases = df[df['second_innings_score'] > df['first_innings_score']]
    if chases.empty:
        return {"error": "No successful chases found in dataset"}
    row = chases.loc[chases['second_innings_score'].idxmax()]
    return {
        "winner": str(row['winner']),
        "chased_score": int(row['second_innings_score']),
        "target": int(row['first_innings_score'] + 1),
        "match_id": str(row['match_id']),
        "season": int(row['season']),
        "venue": str(row['venue']),
        "date": str(row['date'])
    }

def closest_match():
    df = matches.copy()
    df['win_by'] = df['win_by'].fillna('')
    runs_margin = df[df['win_by'].str.lower() == 'runs'].copy()
    if runs_margin.empty:
        return {"error": "No run-margin matches found"}
    row = runs_margin.loc[runs_margin['win_margin'].idxmin()]
    return {
        "winner": str(row['winner']),
        "margin": f"{int(row['win_margin'])} runs",
        "match_id": str(row['match_id']),
        "season": int(row['season']),
        "venue": str(row['venue']),
        "date": str(row['date'])
    }

def biggest_win():
    df = matches.copy()
    df['win_by'] = df['win_by'].fillna('')
    runs_margin = df[df['win_by'].str.lower() == 'runs'].copy()
    if runs_margin.empty:
        return {"error": "No run-margin matches found"}
    row = runs_margin.loc[runs_margin['win_margin'].idxmax()]
    return {
        "winner": str(row['winner']),
        "margin": f"{int(row['win_margin'])} runs",
        "match_id": str(row['match_id']),
        "season": int(row['season']),
        "venue": str(row['venue']),
        "date": str(row['date'])
    }
