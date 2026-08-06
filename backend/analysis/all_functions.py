import pandas as pd
import numpy as np
from utils.data_loader import matches, deliveries
try:
    from utils.data_loader import seasons
except ImportError:
    seasons = pd.DataFrame()

class Dummy:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None
sns = Dummy()
plt = Dummy()

# team_total_matches(team)-> return total number of matches played by give team
def team_total_matches(team):
  a=matches['team1'].value_counts().get(team, 0)+matches['team2'].value_counts().get(team, 0)
  print(a)
  return a


#team_total_wins(team)-> return total number of match win by the given team over all ipl matches
def team_total_wins(team):
  a=matches['winner'].value_counts().get(team, 0)
  print(a)
  return a


#team_win_percentage(team)-> return wining percentage of theam
def team_win_percentage(team):
  a=matches['team1'].value_counts().get(team, 0) + matches['team2'].value_counts().get(team, 0)
  b=matches['winner'].value_counts().get(team, 0)
  percentage = (b / a * 100) if a > 0 else 0
  return {"win_percentage": round(percentage, 3)}

#team_highest_score(team)
def team_highest_score(team,opponent=None):

    scores=deliveries.groupby(
        ["match_id","innings","batting_team"]
    )["total_runs"].sum().reset_index(name="score")

    team_df=scores[scores["batting_team"]==team]

    if opponent!=None:
        ids=matches[
            ((matches["team1"]==team)&(matches["team2"]==opponent))|
            ((matches["team1"]==opponent)&(matches["team2"]==team))
        ]["match_id"]

        team_df=team_df[team_df["match_id"].isin(ids)]

    highest=team_df.loc[team_df["score"].idxmax()]

    match=matches[matches["match_id"]==highest["match_id"]].iloc[0]

    opp=match["team2"] if match["team1"]==team else match["team1"]

    return{
        "score":int(highest["score"]),
        "opponent":opp,
        "season":int(match["season"]),
        "venue":match["venue"],
        "winner":match["winner"]
    }

#team_lowest_score(team)
def team_lowest_score(team,opponent=None):

    scores=deliveries.groupby(
        ["match_id","innings","batting_team"]
    )["total_runs"].sum().reset_index(name="score")

    team_df=scores[scores["batting_team"]==team]

    if opponent!=None:
        ids=matches[
            ((matches["team1"]==team)&(matches["team2"]==opponent))|
            ((matches["team1"]==opponent)&(matches["team2"]==team))
        ]["match_id"]

        team_df=team_df[team_df["match_id"].isin(ids)]

    lowest=team_df.loc[team_df["score"].idxmin()]

    match=matches[matches["match_id"]==lowest["match_id"]].iloc[0]

    opp=match["team2"] if match["team1"]==team else match["team1"]

    return{
        "score":int(lowest["score"]),
        "opponent":opp,
        "season":int(match["season"]),
        "venue":match["venue"],
        "winner":match["winner"]
    }

#team_average_score(team)-> return avarage score of all matched played
def team_average_score(team):
  a=deliveries.groupby('batting_team')['batsman_runs'].sum().get(team, 0)
  b=matches['team1'].value_counts().get(team, 0)+matches['team2'].value_counts().get(team, 0)
  if b == 0:
      return 0
  highest=team_highest_score(team)["score"]
  lowest=team_lowest_score(team)["score"]
  sns.barplot(x=['average','highest','lowest'],y=[a/b,highest,lowest])
  print(f"{a/b:.3f}")
  return a/b


#team_head_to_head(team1, team2)
def team_head_to_head(team_a, team_b):
  h2h=matches[((matches['team1']==team_a) & (matches['team2']==team_b)) | ((matches['team1']==team_b) & (matches['team2']==team_a))]
  total_matches = len(h2h)
  wins_a = len(h2h[h2h['winner']==team_a])
  wins_b = len(h2h[h2h['winner']==team_b])
  no_result = len(h2h[h2h['winner'].isna()])
  highest_a=team_highest_score(team_a,team_b)["score"]
  highest_b=team_highest_score(team_b,team_a)["score"]
  lowest_a=team_lowest_score(team_a,team_b)
  lowest_b=team_lowest_score(team_b,team_a)
  season_graph=h2h.groupby(["season","winner"]).size().reset_index(name="wins")
  plt.figure(figsize=(10,5))
  sns.lineplot(
    data=season_graph,
    x="season",
    y="wins",
    hue="winner",
    marker="o",
    linewidth=3
  )
  match_history=h2h.sort_values(by=["season","match_number"],ascending=False)[
    [
        "season",
        "match_number",
        "team1",
        "team2",
        "winner",
        "result",
        "venue",
        "toss_winner",
        "player_of_match"
    ]
].reset_index(drop=True)
  return {
        "matches": total_matches,
        "team1_wins": wins_a,
        "team2_wins": wins_b,
        "no_result": no_result,
        "highest_team1": highest_a,
        "highest_team2": highest_b,
        "lowest_team1":lowest_a,
        "lowest_team2":lowest_b,
        "match_history": match_history
    }

#top_run_scorers(top_n)->return Top n batsmen with total runs, matches, innings, average, strike rate.
a=deliveries.merge(matches,on='match_id')
def top_run_scorers(top_n=10, s=None):
    df_filtered = a if (s is None or s == '') else a[a['season'] == s]
    balls = df_filtered[df_filtered['extra_type'] != 'wides'].groupby('striker').size().rename('balls')
    runs = df_filtered.groupby('striker')['batsman_runs'].sum().rename('runs')
    strike_rate = ((runs / balls) * 100).round(2).rename('strike_rate')
    stats = pd.concat([runs, balls, strike_rate], axis=1).reset_index()
    top_run = stats.sort_values('runs', ascending=False).head(top_n)
    return top_run

#player_total_runs(player)->return total run by any player
def player_total_runs(player):
  return deliveries[deliveries['striker']==player]['batsman_runs'].sum()

#player_average(player)->return average score of a player
def player_average(player):
  played=matches_played = deliveries[deliveries['striker']==player]['match_id'].nunique()
  return player_total_runs(player)/played

#player_highest_score(player)
def player_highest_score(player):
  return deliveries[deliveries['striker']==player].groupby('match_id').sum()['batsman_runs'].max()


#player_centuries(player) return Number of innings where player scored 100+ runs.
def player_centuries(player):
    runs = (
        deliveries[deliveries['striker'] == player]
        .groupby(['match_id', 'innings'])['batsman_runs']
        .sum()
    )

    return (runs >= 100).sum()

def player_half_centuries(player):
    runs = (
        deliveries[deliveries['striker'] == player]
        .groupby(['match_id', 'innings'])['batsman_runs']
        .sum()
    )

    return ((runs >= 50) & (runs < 100)).sum()

#player_sixes(player) Total number of boundaries (6s) hit.
def player_sixes(player):
  a=deliveries[deliveries['striker']==player]
  return a[a['batsman_runs']==6].shape[0]

#player_fours(player) Total number of boundaries (4s) hit.
def player_fours(player):
  a=deliveries[deliveries['striker']==player]
  return a[a['batsman_runs']==4].shape[0]

#player_runs_by_season(player) return ->Season-wise runs (Year, Runs)
def player_runs_by_season(player):
  return deliveries[deliveries['striker']==player].groupby('season')['batsman_runs'].sum()


# #player_runs_against_team(player, team) return ->Stats against a specific team: Matches, Innings, Runs, Average, Strike Rate, Highest Score.
# def player_runs_against_team(player, team):
#   a=deliveries[(deliveries['bowling_team']==team) & (deliveries['striker']==player)]
#   a=a.groupby('match_id')['batsman_runs'].sum().reset_index().assign(Player=player,Against_Team=team)
#   a=a[['Player','Against_Team','match_id','batsman_runs']]
#   matches=len(a)
#   return a


# player_runs_against_team(player, team) -> Stats against a specific team: Matches, Innings, Runs, Average, Strike Rate, Highest Score.
def player_runs_against_team(player, team):
    a = deliveries[(deliveries['bowling_team'] == team) & (deliveries['striker'] == player)]
    innings_data =a.groupby(['match_id', 'innings'])['batsman_runs'].sum().reset_index()
    matches = innings_data['match_id'].nunique()
    innings_count = len(innings_data)
    runs = innings_data['batsman_runs'].sum()
    highest_score = innings_data['batsman_runs'].max()
    balls = a[(a['extra_type'] != 'wides')].shape[0]
    strike_rate = (runs / balls * 100) if balls > 0 else 0
    dismissals = deliveries[(deliveries['dismissed_player'] == player) &(deliveries['bowling_team'] == team)].shape[0]
    average = runs / dismissals if dismissals > 0 else runs
    result = pd.DataFrame({
        'Player': [player],
        'Against_Team': [team],
        'Matches': [matches],
        'Innings': [innings_count],
        'Runs': [runs],
        'Average': [round(average, 2)],
        'Strike_Rate': [round(strike_rate, 2)],
        'Highest_Score': [highest_score]
    })

    return result

#player_runs_at_venue(player, venue) -> Stats at a venue: Matches, Innings, Runs, Average, Strike Rate, Highest Score.
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
    highest_score = (a.groupby(['match_id', 'innings'])['batsman_runs'].sum().max())

    result = pd.DataFrame({
        'Player': [player],
        'Venue': [venue],
        'Matches': [total_matches],
        'Innings': [innings_count],
        'Runs': [runs],
        'Average': [round(average, 2)],
        'Strike_Rate': [round(strike_rate, 2)],
        'Highest_Score': [highest_score]
    })

    return result

#top_wicket_takers(top_n=10)->DataFrame with Player, Wickets, Matches, Innings
def top_wicket_takers(top_n=10):
    wickets = deliveries.groupby('bowler')['is_wicket'].sum()
    matches = deliveries.groupby('bowler')['match_id'].nunique()
    result = pd.DataFrame({
        'Player': wickets.index,
        'Wickets': wickets.values,
        'Matches': matches.values
    })
    return result.sort_values('Wickets', ascending=False).head(top_n).reset_index(drop=True)


#player_total_wickets(player)->total wickets by any bowler
def player_total_wickets(player):
  return deliveries[deliveries['bowler']==player]['is_wicket'].sum()

#player_economy(player)->return economy_rate=total_runs_conceded/total_overs_bowled
def player_economy(player):
  run=deliveries.groupby('bowler')['total_runs'].sum().get(player, 0)
  overs=len(deliveries[deliveries['bowler']==player])/6
  return round(run/overs,2)

#player_bowling_average(player) -> return total_run/wicket
def player_bowling_average(player):
    b_df = deliveries[deliveries['bowler'] == player]
    if b_df.empty:
        return 0.0
    run = b_df['total_runs'].sum()
    wicket = b_df['is_wicket'].sum()
    return round(float(run / wicket), 2) if wicket > 0 else 0.0

#player_bowling_strike_rate(player) ->return Bowling_Strike_Rate=Balls_Bowled/Wickets_Taken
def player_bowling_strike_rate(player):
    b_df = deliveries[deliveries['bowler'] == player]
    if b_df.empty:
        return 0.0
    balls = b_df[~b_df['extra_type'].isin(['wides', 'noballs'])].shape[0]
    w_types = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    wicket = b_df[(b_df['is_wicket'] == 1) & (b_df['dismissal_type'].isin(w_types))].shape[0]
    return round(float(balls / wicket), 2) if wicket > 0 else 0.0


#player_best_figures(player) ->return Dictionary or tuple containing {wickets, runs}. Example: {"wickets":5,"runs":19}
def player_best_figures(player):
  a=deliveries[deliveries['bowler']==player].groupby('total_runs').sum()
  b=deliveries[deliveries['bowler']==player].groupby('match_id')['is_wicket'].sum()
  return {"wickets":b,"runs":a}


#player_wickets_by_season(player)
def player_wickets_by_season(player):
  a=matches.merge(deliveries,on='match_id')
  a=a[a['bowler']==player].groupby('season')['is_wicket'].sum().reset_index()
  return a

#player_wickets_against_team(player, team)->
def player_wickets_against_team(player, team):
  return deliveries[(deliveries['batting_team']==team) & (deliveries['bowler']==player)]['is_wicket'].sum()

#player_dot_ball_percentage(player) -> percentage of dot balls
def player_dot_ball_percentage(player):
  b=deliveries[(deliveries['bowler']==player)].shape[0]
  a=deliveries[(deliveries['bowler']==player) & (deliveries['total_runs']==0)].shape[0]
  return a/b*100

# #bowler_vs_batsman(bowler, batsman) -> Dictionary or one-row DataFrame containing:
# • Balls Faced
# • Runs Scored
# • Wickets
# • Dot Balls
# • Strike Rate
# • Boundaries (4s, 6s)
def bowler_vs_batsman(bowler, batsman):
    df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['batter'] == batsman)]
    balls_faced = df.shape[0]
    runs_scored = df['batsman_runs'].sum()
    wickets = df['is_wicket'].sum()
    dot_balls = (df['batsman_runs'] == 0).sum()
    strike_rate = (runs_scored / balls_faced * 100) if balls_faced > 0 else 0
    boundaries_4 = (df['batsman_runs'] == 4).sum()
    boundaries_6 = (df['batsman_runs'] == 6).sum()
    return {
        "Balls Faced": balls_faced,
        "Runs Scored": runs_scored,
        "Wickets": wickets,
        "Dot Balls": dot_balls,
        "Strike Rate": round(strike_rate, 2),
        "Boundaries": {
            "4s": boundaries_4,
            "6s": boundaries_6
        }
    }

#1. venue_total_matches(venue)->return number of match in this venue
def venue_total_matches(venue):
  return matches[matches['venue']==venue].shape[0]


# venue_average_score(venue) -> return average first innings score at that venue
def venue_average_score(venue):
    venue_matches = matches[matches['venue'] == venue]

    return {
        "venue": venue,
        "average_score": round(venue_matches['first_innings_score'].mean(), 1)
    }

def highest_team_total_at_venue(venue):
    df = matches[matches['venue'] == venue]

    highest_score = -1
    team = against = season = None

    for _, row in df.iterrows():
        # Check first innings
        if row['first_innings_score'] > highest_score:
            highest_score = row['first_innings_score']
            team = row['team1']
            against = row['team2']
            season = row['season']

        # Check second innings
        if row['second_innings_score'] > highest_score:
            highest_score = row['second_innings_score']
            team = row['team2']
            against = row['team1']
            season = row['season']

    return {
        "score": highest_score,
        "team": team,
        "against": against,
        "season": season
    }

# lowest_team_total_at_venue(venue) -> lowest team total at the venue
def lowest_team_total_at_venue(venue):
    venue_matches = matches[matches['venue'] == venue]

    lowest_score = float('inf')
    team = against = season = None

    for _, row in venue_matches.iterrows():
        # First innings
        if row['first_innings_score'] < lowest_score:
            lowest_score = row['first_innings_score']
            team = row['team1']
            against = row['team2']
            season = row['season']

        # Second innings
        if row['second_innings_score'] < lowest_score:
            lowest_score = row['second_innings_score']
            team = row['team2']
            against = row['team1']
            season = row['season']

    return {
        "score": lowest_score,
        "team": team,
        "against": against,
        "season": season
    }

#venue_batting_first_win_percentage(venue)->Percentage of matches won by the team batting first.
def venue_batting_first_win_percentage(venue):
    venue_matches = matches[matches['venue'] == venue]
    if len(venue_matches) == 0:
        return 0.0
    if 'win_by' in venue_matches.columns:
        batting_first_wins = venue_matches[venue_matches['win_by'] == 'runs'].shape[0]
    else:
        batting_first_wins = venue_matches[venue_matches['winner'] == venue_matches['team1']].shape[0]
    percentage = (batting_first_wins / len(venue_matches)) * 100
    return round(float(percentage), 2)

def season_summary(season):
    a = seasons[seasons['season'] == season]

    if len(a) == 0:
        return "Season not found"

    row = a.iloc[0]

    return {
        "season": row['season'],
        "total_matches": row['total_matches'],
        "total_runs": row['total_runs_scored'],
        "average_score": row['avg_first_innings_score'],
        "highest_score": row['highest_team_total'],
        "lowest_score": row['lowest_team_total'],
        "champion": row['champion'],
        "runner_up": row['runner_up'],
        "most_sixes": row['total_sixes'],
        "most_fours": row['total_fours']
    }

def _team_innings_totals():
    """Helper: total runs scored by each team per match per innings."""
    totals = deliveries.groupby(['match_id', 'innings', 'batting_team'])['total_runs'].sum().reset_index()
    totals = totals.merge(matches[['match_id', 'season', 'venue', 'city', 'date']], on='match_id', how='left')
    return totals


def highest_team_total():
    totals = _team_innings_totals()
    row = totals.loc[totals['total_runs'].idxmax()]
    return {
        "team": row['batting_team'],
        "total_runs": row['total_runs'],
        "match_id": row['match_id'],
        "season": row['season'],
        "venue": row['venue'],
        "date": row['date']
    }


def lowest_team_total():
    totals = _team_innings_totals()
    row = totals.loc[totals['total_runs'].idxmin()]
    return {
        "team": row['batting_team'],
        "total_runs": row['total_runs'],
        "match_id": row['match_id'],
        "season": row['season'],
        "venue": row['venue'],
        "date": row['date']
    }


def highest_successful_chase():
    # A successful chase = team batting 2nd (innings 2) won the match
    df = matches.copy()
    chases = df[df['second_innings_score'] > df['first_innings_score']]
    if chases.empty:
        raise ValueError("No successful chases found in dataset")
    row = chases.loc[chases['second_innings_score'].idxmax()]
    return {
        "winner": row['winner'],
        "chased_score": row['second_innings_score'],
        "target": row['first_innings_score'] + 1,
        "match_id": row['match_id'],
        "season": row['season'],
        "venue": row['venue'],
        "date": row['date']
    }


def closest_match():
    df = matches.copy()
    # runs-based margins only (win_by likely indicates 'runs' or 'wickets')
    runs_margin = df[df['win_by'].str.lower() == 'runs'].copy()
    if runs_margin.empty:
        raise ValueError("No run-margin matches found; check 'win_by' values")
    row = runs_margin.loc[runs_margin['win_margin'].idxmin()]
    return {
        "winner": row['winner'],
        "margin": f"{row['win_margin']} runs",
        "match_id": row['match_id'],
        "season": row['season'],
        "venue": row['venue'],
        "date": row['date']
    }


def biggest_win():
    df = matches.copy()
    runs_margin = df[df['win_by'].str.lower() == 'runs'].copy()
    if runs_margin.empty:
        raise ValueError("No run-margin matches found; check 'win_by' values")
    row = runs_margin.loc[runs_margin['win_margin'].idxmax()]
    return {
        "winner": row['winner'],
        "margin": f"{row['win_margin']} runs",
        "match_id": row['match_id'],
        "season": row['season'],
        "venue": row['venue'],
        "date": row['date']
    }

def partnership_analysis(team):
    """
    Analyze partnerships (runs scored between two consecutive wicket falls)
    for a given team across all matches.
    """
    team_deliveries = deliveries[deliveries['batting_team'] == team].copy()
    if team_deliveries.empty:
        raise ValueError(f"No data found for team '{team}'")

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
                        "batsmen": current_pair,
                        "runs": partnership_runs,
                        "balls": balls_faced
                    })
                    current_pair = pair
                    partnership_runs = 0
                    balls_faced = 0

                partnership_runs += ball['total_runs']
                balls_faced += 1

            # append last partnership of the innings
            partnerships.append({
                "match_id": match_id,
                "innings": innings,
                "batsmen": current_pair,
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

    best = summary.iloc[0]

    return {
        "team": team,
        "best_partnership_pair": best['batsmen'],
        "total_runs": best['total_runs'],
        "partnerships_count": int(best['partnerships_count']),
        "avg_runs": round(best['avg_runs'], 2),
        "all_partnerships": summary
    }


def boundary_percentage(player):
    """
    Percentage of a player's total runs that came from boundaries (4s and 6s).
    """
    player_df = deliveries[deliveries['striker'] == player]
    if player_df.empty:
        raise ValueError(f"No data found for player '{player}'")

    total_runs = player_df['batsman_runs'].sum()

    fours = player_df[player_df['batsman_runs'] == 4].shape[0]
    sixes = player_df[player_df['batsman_runs'] == 6].shape[0]

    boundary_runs = (fours * 4) + (sixes * 6)
    percentage = (boundary_runs / total_runs * 100) if total_runs > 0 else 0

    return {
        "player": player,
        "total_runs": total_runs,
        "fours": fours,
        "sixes": sixes,
        "boundary_runs": boundary_runs,
        "boundary_percentage": round(percentage, 2)
    }


def run_rate_by_over(match_id):
    """
    Runs scored per over, per innings, for a given match.
    """
    match_df = deliveries[deliveries['match_id'] == match_id]
    if match_df.empty:
        raise ValueError(f"No data found for match_id '{match_id}'")

    over_runs = (
        match_df.groupby(['innings', 'over'])['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'runs_in_over'})
    )

    over_runs['run_rate'] = over_runs['runs_in_over']  # runs per over IS the run rate for that over
    over_runs['cumulative_runs'] = over_runs.groupby('innings')['runs_in_over'].cumsum()
    over_runs['overs_completed'] = over_runs.groupby('innings').cumcount() + 1
    over_runs['cumulative_run_rate'] = round(over_runs['cumulative_runs'] / over_runs['overs_completed'], 2)

    return over_runs


def win_probability(match_id):
    """
    Simple win probability estimate for the chasing team at each stage of the 2nd innings,
    based on required run rate vs current run rate.
    Note: this is a basic heuristic, not a trained model.
    """
    match_info = matches[matches['match_id'] == match_id]
    if match_info.empty:
        raise ValueError(f"No match found with match_id '{match_id}'")
    match_info = match_info.iloc[0]

    target = match_info['first_innings_score'] + 1
    second_innings = deliveries[(deliveries['match_id'] == match_id) & (deliveries['innings'] == 2)].copy()

    if second_innings.empty:
        raise ValueError(f"No second innings data found for match_id '{match_id}'")

    second_innings = second_innings.sort_values(['over', 'ball'])
    second_innings['cumulative_runs'] = second_innings['total_runs'].cumsum()
    second_innings['balls_bowled'] = range(1, len(second_innings) + 1)
    second_innings['overs_bowled'] = second_innings['balls_bowled'] / 6

    total_overs = match_info['first_innings_overs']  # assume same match length
    total_balls = total_overs * 6

    results = []
    for _, row in second_innings.iterrows():
        runs_scored = row['cumulative_runs']
        balls_bowled = row['balls_bowled']
        balls_remaining = total_balls - balls_bowled
        runs_needed = target - runs_scored

        current_rr = runs_scored / (balls_bowled / 6) if balls_bowled > 0 else 0
        required_rr = (runs_needed / (balls_remaining / 6)) if balls_remaining > 0 else float('inf')

        # crude heuristic: compare current vs required run rate
        if balls_remaining <= 0 or runs_needed <= 0:
            win_prob = 100 if runs_needed <= 0 else 0
        else:
            diff = current_rr - required_rr
            win_prob = max(0, min(100, 50 + diff * 5))  # scaled heuristic

        results.append({
            "over": row['over'],
            "ball": row['ball'],
            "runs_scored": runs_scored,
            "runs_needed": runs_needed,
            "current_run_rate": round(current_rr, 2),
            "required_run_rate": round(required_rr, 2) if balls_remaining > 0 else None,
            "chasing_team_win_probability": round(win_prob, 1)
        })

    return pd.DataFrame(results)

#Comparison
def compare_batsmen(player1, player2):
    def stats(player):
        df = deliveries[deliveries['striker'] == player]
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
            "total_runs": total_runs,
            "balls_faced": balls,
            "matches_played": matches_played,
            "average": average,
            "strike_rate": strike_rate,
            "fours": fours,
            "sixes": sixes,
            "fifties": fifties,
            "centuries": centuries
        }
    return {"player1": stats(player1), "player2": stats(player2)}


def compare_bowlers(player1, player2):
    def stats(player):
        df = deliveries[deliveries['bowler'] == player]
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
            "matches_played": matches_played,
            "balls_bowled": balls,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "economy": economy,
            "average": average,
            "strike_rate": strike_rate
        }
    return {"player1": stats(player1), "player2": stats(player2)}


def compare_teams(team1, team2):
    def stats(team):
        matches_played = matches[(matches['team1'] == team) | (matches['team2'] == team)]
        total_matches = matches_played.shape[0]
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
            "matches_played": total_matches,
            "wins": wins,
            "losses": losses,
            "win_percentage": win_pct,
            "highest_total": highest_total,
            "lowest_total": lowest_total,
            "average_total": avg_total
        }
    return {"team1": stats(team1), "team2": stats(team2)}


def compare_venues(venue1, venue2):
    def stats(venue):
        venue_matches = matches[matches['venue'] == venue]
        total_matches = venue_matches.shape[0]
        avg_first_innings = round(venue_matches['first_innings_score'].mean(), 2) if total_matches > 0 else 0
        avg_second_innings = round(venue_matches['second_innings_score'].mean(), 2) if total_matches > 0 else 0
        bat_first_wins = venue_matches[venue_matches['winner'] == venue_matches['team1']].shape[0]
        chase_wins = venue_matches[venue_matches['winner'] == venue_matches['team2']].shape[0]
        highest_total = max(venue_matches['first_innings_score'].max(), venue_matches['second_innings_score'].max()) if total_matches > 0 else 0
        return {
            "venue": venue,
            "matches_played": total_matches,
            "avg_first_innings_score": avg_first_innings,
            "avg_second_innings_score": avg_second_innings,
            "bat_first_wins": bat_first_wins,
            "chase_wins": chase_wins,
            "highest_total": highest_total
        }
    return {"venue1": stats(venue1), "venue2": stats(venue2)}


def compare_seasons(season1, season2):
    def stats(season):
        season_matches = matches[matches['season'] == season]
        total_matches = season_matches.shape[0]
        season_deliveries = deliveries[deliveries['match_id'].isin(season_matches['match_id'])]
        total_runs = season_deliveries['total_runs'].sum()
        total_wickets = season_deliveries[season_deliveries['is_wicket'] == 1].shape[0]
        totals = season_deliveries.groupby(['match_id', 'innings'])['total_runs'].sum()
        highest_total = totals.max() if not totals.empty else 0
        avg_runs_per_match = round(total_runs / total_matches, 2) if total_matches > 0 else 0
        return {
            "season": season,
            "matches_played": total_matches,
            "total_runs": total_runs,
            "total_wickets": total_wickets,
            "highest_total": highest_total,
            "avg_runs_per_match": avg_runs_per_match
        }
    return {"season1": stats(season1), "season2": stats(season2)}

def get_all_player_names():
    """
    Returns a list of all unique player names in the dataset.
    """
    return players['player_name'].dropna().unique().tolist()


def get_all_team_names():
    """
    Returns a list of all unique team names in the dataset.
    """
    all_teams = pd.concat([matches['team1'], matches['team2'], matches['winner'], deliveries['batting_team'], deliveries['bowling_team']]).dropna().unique()
    return sorted(list(set(all_teams)))


def get_all_venue_names():
    """
    Returns a list of all unique venue names in the dataset.
    """
    return matches['venue'].dropna().unique().tolist()


def get_all_season_years():
    """
    Returns a list of all unique season years in the dataset.
    """
    return sorted(matches['season'].dropna().unique().tolist())


def get_top_n_teams_by_win_percentage(n=5):
    """
    Returns the top N teams based on their overall win percentage.
    """
    team_wins = matches['winner'].value_counts().reset_index()
    team_wins.columns = ['team', 'wins']

    team_matches_played = pd.concat([matches['team1'], matches['team2']]).value_counts().reset_index()
    team_matches_played.columns = ['team', 'matches_played']

    team_stats = pd.merge(team_matches_played, team_wins, on='team', how='left').fillna(0)
    team_stats['win_percentage'] = (team_stats['wins'] / team_stats['matches_played']) * 100

    return team_stats.sort_values(by='win_percentage', ascending=False).head(n).round(2).to_dict(orient='records')


def team_toss_win_match_win_percentage(team):
    """
    Calculates the percentage of matches a team won after winning the toss.
    """
    team_toss_wins = matches[(matches['toss_winner'] == team)]
    if team_toss_wins.empty:
        return {"team": team, "message": "Team never won the toss."}

    matches_won_after_toss_win = team_toss_wins[team_toss_wins['winner'] == team].shape[0]
    total_toss_wins = team_toss_wins.shape[0]

    win_percentage = round((matches_won_after_toss_win / total_toss_wins) * 100, 2) if total_toss_wins > 0 else 0
    return {"team": team, "toss_win_match_win_percentage": win_percentage}


def team_win_percentage_batting_first(team):
    """
    Calculates the win percentage of a team when they bat first.
    """
    team_bat_first_matches = matches[
        ((matches['team1'] == team) & (matches['toss_decision'] == 'bat')) |
        ((matches['team2'] == team) & (matches['toss_decision'] == 'field'))
    ]
    if team_bat_first_matches.empty:
        return {"team": team, "message": "Team never batted first."}

    wins_bat_first = team_bat_first_matches[team_bat_first_matches['winner'] == team].shape[0]
    total_bat_first_matches = team_bat_first_matches.shape[0]

    win_percentage = round((wins_bat_first / total_bat_first_matches) * 100, 2) if total_bat_first_matches > 0 else 0
    return {"team": team, "win_percentage_batting_first": win_percentage}


def team_win_percentage_chasing(team):
    """
    Calculates the win percentage of a team when they are chasing (batting second).
    """
    team_chasing_matches = matches[
        ((matches['team1'] == team) & (matches['toss_decision'] == 'field')) |
        ((matches['team2'] == team) & (matches['toss_decision'] == 'bat'))
    ]
    if team_chasing_matches.empty:
        return {"team": team, "message": "Team never chased."}

    wins_chasing = team_chasing_matches[team_chasing_matches['winner'] == team].shape[0]
    total_chasing_matches = team_chasing_matches.shape[0]

    win_percentage = round((wins_chasing / total_chasing_matches) * 100, 2) if total_chasing_matches > 0 else 0
    return {"team": team, "win_percentage_chasing": win_percentage}


def match_highest_individual_score_details(match_id):
    """
    Returns the highest individual score in a given match, along with the player and team.
    """
    match_deliveries = deliveries[deliveries['match_id'] == match_id]
    if match_deliveries.empty:
        return {"match_id": match_id, "message": "Match not found."}

    runs_per_batsman_innings = match_deliveries.groupby(['striker', 'innings'])['batsman_runs'].sum().reset_index()
    if runs_per_batsman_innings.empty:
        return {"match_id": match_id, "message": "No runs scored in this match."}

    highest_score_row = runs_per_batsman_innings.loc[runs_per_batsman_innings['batsman_runs'].idxmax()]

    # Get the batting team for the innings
    batting_team = match_deliveries[
        (match_deliveries['striker'] == highest_score_row['striker']) &
        (match_deliveries['innings'] == highest_score_row['innings'])
    ]['batting_team'].iloc[0]

    return {
        "match_id": match_id,
        "player": highest_score_row['striker'],
        "team": batting_team,
        "innings": int(highest_score_row['innings']),
        "highest_score": int(highest_score_row['batsman_runs'])
    }


def match_best_bowling_figures_details(match_id):
    """
    Returns the best bowling figures (wickets and runs) in a given match, along with the bowler and team.
    """
    match_deliveries = deliveries[deliveries['match_id'] == match_id]
    if match_deliveries.empty:
        return {"match_id": match_id, "message": "Match not found."}

    bowler_stats = match_deliveries.groupby('bowler').agg(
        wickets=('is_wicket', 'sum'),
        runs_conceded=('total_runs', 'sum')
    ).reset_index()

    if bowler_stats.empty:
        return {"match_id": match_id, "message": "No bowling data for this match."}

    # Sort by wickets (descending) and then runs conceded (ascending)
    best_bowler_row = bowler_stats.sort_values(by=['wickets', 'runs_conceded'], ascending=[False, True]).iloc[0]

    # Get the bowling team for the bowler in this match
    bowling_team = match_deliveries[match_deliveries['bowler'] == best_bowler_row['bowler']]['bowling_team'].iloc[0]

    return {
        "match_id": match_id,
        "bowler": best_bowler_row['bowler'],
        "team": bowling_team,
        "wickets": int(best_bowler_row['wickets']),
        "runs_conceded": int(best_bowler_row['runs_conceded'])
    }


def match_total_extras(match_id):
    """
    Calculates the total extra runs conceded in a given match.
    """
    match_deliveries = deliveries[deliveries['match_id'] == match_id]
    if match_deliveries.empty:
        return {"match_id": match_id, "message": "Match not found."}

    total_extras = match_deliveries['extra_runs'].sum()
    return {"match_id": match_id, "total_extras": int(total_extras)}


def team_most_common_dismissal_type_conceded(team):
    """
    Identifies the most common dismissal type for wickets lost by a specific team.
    """
    team_dismissals = deliveries[
        (deliveries['batting_team'] == team) &
        (deliveries['is_wicket'] == 1) &
        (deliveries['dismissal_type'].notna()) # Exclude run-outs if not attributed to bowler
    ]
    if team_dismissals.empty:
        return {"team": team, "message": "No wickets lost by this team or no data."}

    most_common = team_dismissals['dismissal_type'].mode().iloc[0] # .mode() returns a Series, take first if multiple modes
    count = team_dismissals['dismissal_type'].value_counts().max()

    return {"team": team, "most_common_dismissal_type_conceded": most_common, "count": int(count)}


def team_most_common_wicket_taking_dismissal_type(team):
    """
    Identifies the most common dismissal type used by a specific team to take wickets.
    """
    team_wickets = deliveries[
        (deliveries['bowling_team'] == team) &
        (deliveries['is_wicket'] == 1) &
        (deliveries['dismissal_type'].notna())
    ]
    if team_wickets.empty:
        return {"team": team, "message": "No wickets taken by this team or no data."}

    most_common = team_wickets['dismissal_type'].mode().iloc[0]
    count = team_wickets['dismissal_type'].value_counts().max()

    return {"team": team, "most_common_wicket_taking_dismissal_type": most_common, "count": int(count)}


def venue_toss_decision_win_advantage(venue, toss_decision):
    """
    Calculates the win percentage for teams that chose a specific toss decision (bat/field)
    at a given venue.
    """
    venue_matches = matches[(matches['venue'] == venue) & (matches['toss_decision'] == toss_decision)]
    if venue_matches.empty:
        return {"venue": venue, "toss_decision": toss_decision, "message": "No matches found for this venue with this toss decision."}

    wins_with_decision = venue_matches[venue_matches['winner'] == venue_matches['toss_winner']].shape[0]
    total_matches_with_decision = venue_matches.shape[0]

    win_percentage = round((wins_with_decision / total_matches_with_decision) * 100, 2) if total_matches_with_decision > 0 else 0
    return {"venue": venue, "toss_decision": toss_decision, "win_percentage_for_toss_winner": win_percentage}


def season_most_player_of_match_award_winner(season):
    """
    Returns the player with the most Player of the Match awards in a specific season.
    """
    season_matches = matches[matches['season'] == season]
    if season_matches.empty:
        return {"season": season, "message": "No matches found for this season."}

    if 'player_of_match' not in season_matches.columns:
        return {"season": season, "message": "'player_of_match' column not found."}

    mom_counts = season_matches['player_of_match'].value_counts()
    if mom_counts.empty:
        return {"season": season, "message": "No Player of the Match awards recorded for this season."}

    most_mom_player = mom_counts.index[0]
    count = mom_counts.iloc[0]

    return {"season": season, "player": most_mom_player, "awards_count": int(count)}


def team_wins_by_toss_decision(team):
    """
    Analyzes a team's win percentage based on their toss decision (batting first or chasing).
    """
    team_matches = matches[(matches['toss_winner'] == team)]

    if team_matches.empty:
        return {"team": team, "message": "No matches found for this team as toss winner."}

    wins_bat_first = team_matches[(team_matches['toss_decision'] == 'bat') & (team_matches['winner'] == team)].shape[0]
    total_bat_first = team_matches[team_matches['toss_decision'] == 'bat'].shape[0]

    wins_bowl_first = team_matches[(team_matches['toss_decision'] == 'field') & (team_matches['winner'] == team)].shape[0]
    total_bowl_first = team_matches[team_matches['toss_decision'] == 'field'].shape[0]

    bat_first_win_pct = round((wins_bat_first / total_bat_first) * 100, 2) if total_bat_first > 0 else 0
    bowl_first_win_pct = round((wins_bowl_first / total_bowl_first) * 100, 2) if total_bowl_first > 0 else 0

    return {
        "team": team,
        "total_toss_wins": team_matches.shape[0],
        "bat_first_wins": wins_bat_first,
        "total_bat_first": total_bat_first,
        "bat_first_win_percentage": bat_first_win_pct,
        "bowl_first_wins": wins_bowl_first,
        "total_bowl_first": total_bowl_first,
        "bowl_first_win_percentage": bowl_first_win_pct
    }

def player_dismissal_types(player):
    """
    Returns the breakdown of dismissal types for a given player.
    """
    player_dismissals = deliveries[deliveries['dismissed_player'] == player]
    if player_dismissals.empty:
        return {"player": player, "message": "Player not dismissed in the dataset or not found."}

    dismissal_counts = player_dismissals['dismissal_type'].value_counts().to_dict()
    return {"player": player, "dismissal_types": dismissal_counts}

def venue_toss_decision_impact(venue):
    """
    Analyzes the impact of toss decision (batting/fielding first) on match outcomes at a specific venue.
    """
    venue_matches = matches[matches['venue'] == venue]
    if venue_matches.empty:
        return {"venue": venue, "message": "No matches found for this venue."}

    total_matches = len(venue_matches)

    # Team batting first won
    bat_first_wins = venue_matches[(venue_matches['toss_decision'] == 'bat') & (venue_matches['winner'] == venue_matches['toss_winner'])].shape[0]
    # Team fielding first won
    field_first_wins = venue_matches[(venue_matches['toss_decision'] == 'field') & (venue_matches['winner'] == venue_matches['toss_winner'])].shape[0]

    bat_first_win_percentage = round((bat_first_wins / total_matches) * 100, 2) if total_matches > 0 else 0
    field_first_win_percentage = round((field_first_wins / total_matches) * 100, 2) if total_matches > 0 else 0

    return {
        "venue": venue,
        "total_matches": total_matches,
        "toss_winner_bat_first_wins": bat_first_wins,
        "toss_winner_field_first_wins": field_first_wins,
        "win_pct_toss_winner_bat_first": bat_first_win_percentage,
        "win_pct_toss_winner_field_first": field_first_win_percentage
    }

def player_overall_strike_rate(player):
    """
    Calculates the overall strike rate for a given player.
    """
    player_df = deliveries[deliveries['striker'] == player]
    total_runs = player_df['batsman_runs'].sum()
    balls_faced = player_df[player_df['extra_type'] != 'wides'].shape[0]
    return round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0

def player_overall_average_runs(player):
    """
    Calculates the overall batting average for a given player.
    """
    player_df = deliveries[deliveries['striker'] == player]
    total_runs = player_df['batsman_runs'].sum()
    dismissals = player_df[player_df['dismissed_player'] == player].shape[0]
    return round(total_runs / dismissals, 2) if dismissals > 0 else total_runs

def player_runs_in_powerplay(player):
    """
    Calculates runs scored by a batsman in the powerplay overs (1-6).
    """
    powerplay_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] <= 6)]
    return powerplay_df['batsman_runs'].sum()

def player_runs_in_middle_overs(player):
    """
    Calculates runs scored by a batsman in middle overs (7-15).
    """
    middle_overs_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] > 6) & (deliveries['over'] <= 15)]
    return middle_overs_df['batsman_runs'].sum()

def player_runs_in_death_overs(player):
    """
    Calculates runs scored by a batsman in death overs (16-20).
    """
    death_overs_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] > 15)]
    return death_overs_df['batsman_runs'].sum()

def player_not_out_count(player):
    """
    Counts the number of times a player remained not out.
    """
    player_innings = deliveries[(deliveries['striker'] == player)].groupby(['match_id', 'innings'])
    # Get the last ball of each player's innings
    last_balls = player_innings.tail(1)
    # Count where the player was not dismissed
    not_outs = last_balls[last_balls['dismissed_player'] != player].shape[0]
    return not_outs

def player_duck_count(player):
    """
    Counts the number of times a player scored 0 runs and was dismissed.
    """
    player_innings_runs = deliveries[deliveries['striker'] == player].groupby(['match_id', 'innings'])['batsman_runs'].sum()
    player_dismissals = deliveries[(deliveries['striker'] == player) & (deliveries['dismissed_player'] == player)]

    duck_innings = 0
    for (match, inn), runs in player_innings_runs.items():
        if runs == 0 and not player_dismissals[(player_dismissals['match_id'] == match) & (player_dismissals['innings'] == inn)].empty:
            duck_innings += 1
    return duck_innings

def player_match_winning_runs(player):
    """
    Calculates total runs scored by a player in matches where their team won.
    """
    player_runs_in_matches = deliveries[deliveries['striker'] == player].groupby('match_id')['batsman_runs'].sum().reset_index()
    winning_matches = matches[matches['winner'] == matches['team1']]['match_id'].tolist() + matches[matches['winner'] == matches['team2']]['match_id'].tolist()

    winning_runs_df = player_runs_in_matches[player_runs_in_matches['match_id'].isin(winning_matches)]
    return winning_runs_df['batsman_runs'].sum()

def player_highest_partnership(player):
    """
    Identifies the highest partnership a player has been part of.
    Note: This is a simplified calculation focusing on runs scored while two specific players are at the crease.
    """
    player_deliveries = deliveries[deliveries['striker'] == player]

    # Group by match, innings, and non-striker to identify partnerships
    partnerships = player_deliveries.groupby(['match_id', 'innings', 'non_striker'])['batsman_runs'].sum().reset_index()

    if partnerships.empty:
        return {"player": player, "message": "No partnerships found for this player."}

    highest_partnership_row = partnerships.loc[partnerships['batsman_runs'].idxmax()]

    return {
        "player": player,
        "partner": highest_partnership_row['non_striker'],
        "runs": int(highest_partnership_row['batsman_runs']),
        "match_id": highest_partnership_row['match_id'],
        "innings": highest_partnership_row['innings']
    }

def player_boundaries_per_innings(player):
    """
    Calculates the average number of 4s and 6s per innings for a player.
    """
    player_df = deliveries[deliveries['striker'] == player]
    innings_count = player_df.groupby(['match_id', 'innings']).ngroups

    if innings_count == 0:
        return {"player": player, "message": "No innings played by this player."}

    fours = player_df[player_df['batsman_runs'] == 4].shape[0]
    sixes = player_df[player_df['batsman_runs'] == 6].shape[0]
    total_boundaries = fours + sixes

    return {
        "player": player,
        "total_innings": innings_count,
        "total_fours": fours,
        "total_sixes": sixes,
        "avg_boundaries_per_innings": round(total_boundaries / innings_count, 2)
    }

def batsman_dismissed_by_bowler_count(batsman, bowler):
    """
    Counts the number of times a specific batsman was dismissed by a specific bowler.
    """
    dismissals = deliveries[
        (deliveries['striker'] == batsman) &
        (deliveries['bowler'] == bowler) &
        (deliveries['is_wicket'] == 1)
    ]
    return {"batsman": batsman, "bowler": bowler, "dismissal_count": len(dismissals)}


def batsman_strike_rate_in_successful_chases(player):
    """
    Calculates the strike rate of a player in matches where their team successfully chased a target.
    """
    # Get matches where the second batting team won (successful chase)
    successful_chase_matches = matches[
        (matches['result'] == 'wickets') | (matches['win_by'] == 'wickets')
    ]
    successful_chase_match_ids = successful_chase_matches['match_id'].unique()

    # Filter deliveries for the player in these successful chase matches
    player_chase_deliveries = deliveries[
        (deliveries['striker'] == player) &
        (deliveries['match_id'].isin(successful_chase_match_ids)) &
        (deliveries['innings'] == 2) # Assuming chasing happens in 2nd innings
    ]

    if player_chase_deliveries.empty:
        return {"player": player, "message": "No data for player in successful chases."}

    total_runs = player_chase_deliveries['batsman_runs'].sum()
    balls_faced = player_chase_deliveries[player_chase_deliveries['extra_type'] != 'wides'].shape[0]

    strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0
    return {"player": player, "strike_rate_in_successful_chases": strike_rate}


def batsman_average_against_bowling_style(player_name, bowling_style_category):
    """
    Calculates a batsman's average against a specific bowling style category (e.g., 'Pace', 'Spin').
    Requires 'players' DataFrame to have 'bowling_style'.
    """
    # Map specific bowling styles to categories
    pace_styles = ['Right-arm fast', 'Right-arm fast-medium', 'Left-arm fast', 'Left-arm fast-medium']
    spin_styles = ['Legbreak', 'Offbreak', 'Slow left-arm orthodox', 'Right-arm medium', 'Left-arm chinaman']

    # Get bowlers matching the style category
    target_bowlers_df = pd.DataFrame()
    if bowling_style_category.lower() == 'pace':
        target_bowlers_df = players[players['bowling_style'].isin(pace_styles)]
    elif bowling_style_category.lower() == 'spin':
        target_bowlers_df = players[players['bowling_style'].isin(spin_styles)]
    else:
        return {"player": player_name, "category": bowling_style_category, "message": "Invalid bowling style category. Use 'Pace' or 'Spin'."}

    if target_bowlers_df.empty:
        return {"player": player_name, "category": bowling_style_category, "message": f"No bowlers found for category '{bowling_style_category}'."}

    target_bowlers_names = target_bowlers_df['player_name'].unique()

    # Filter deliveries where the batsman faced these bowlers
    batting_vs_style_df = deliveries[
        (deliveries['striker'] == player_name) &
        (deliveries['bowler'].isin(target_bowlers_names))
    ]

    if batting_vs_style_df.empty:
        return {"player": player_name, "category": bowling_style_category, "message": "No data for this batsman against this bowling style."}

    total_runs = batting_vs_style_df['batsman_runs'].sum()
    dismissals = batting_vs_style_df[
        (batting_vs_style_df['dismissed_player'] == player_name) &
        (batting_vs_style_df['bowler'].isin(target_bowlers_names))
    ].shape[0]

    average = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs

    return {"player": player_name, "bowling_style_category": bowling_style_category, "average": average}


def batsman_runs_per_match_average(player):
    """
    Calculates the average runs scored by a player per match they played.
    """
    player_matches = deliveries[deliveries['striker'] == player]['match_id'].nunique()
    if player_matches == 0:
        return {"player": player, "message": "Player has not played any matches."}

    total_runs = deliveries[deliveries['striker'] == player]['batsman_runs'].sum()

    return {"player": player, "average_runs_per_match": round(total_runs / player_matches, 2)}


def batsman_balls_per_dismissal(player):
    """
    Calculates the average number of balls a batsman faces before being dismissed.
    """
    player_df = deliveries[deliveries['striker'] == player]
    balls_faced = player_df[player_df['extra_type'] != 'wides'].shape[0]
    dismissals = player_df[player_df['dismissed_player'] == player].shape[0]

    balls_per_dismissal = round(balls_faced / dismissals, 2) if dismissals > 0 else float('inf')

    return {"player": player, "balls_faced": balls_faced, "dismissals": dismissals, "balls_per_dismissal": balls_per_dismissal}


def batsman_runs_in_innings_phase(player, phase):
    """
    Calculates runs scored by a batsman in a specific phase of the innings ('powerplay', 'middle', 'death').
    - Powerplay: overs 1-6
    - Middle overs: overs 7-15
    - Death overs: overs 16-20
    """
    if phase.lower() == 'powerplay':
        phase_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] <= 6)]
    elif phase.lower() == 'middle':
        phase_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] > 6) & (deliveries['over'] <= 15)]
    elif phase.lower() == 'death':
        phase_df = deliveries[(deliveries['striker'] == player) & (deliveries['over'] > 15)]
    else:
        return {"player": player, "message": "Invalid phase. Use 'powerplay', 'middle', or 'death'."}

    return {"player": player, "phase": phase, "runs": phase_df['batsman_runs'].sum()}


def batsman_performance_against_team(player, opposing_team):
    """
    Provides comprehensive stats (runs, avg, SR, 100s, 50s) for a batsman against a specific team.
    """
    player_vs_team_df = deliveries[
        (deliveries['striker'] == player) &
        (deliveries['bowling_team'] == opposing_team)
    ]

    if player_vs_team_df.empty:
        return {"player": player, "opposing_team": opposing_team, "message": "No data found for this matchup."}

    innings_data = player_vs_team_df.groupby(['match_id', 'innings'])['batsman_runs'].sum().reset_index()

    total_runs = innings_data['batsman_runs'].sum()
    balls_faced = player_vs_team_df[player_vs_team_df['extra_type'] != 'wides'].shape[0]
    dismissals = player_vs_team_df[player_vs_team_df['dismissed_player'] == player].shape[0]
    innings_played = innings_data.shape[0]

    average = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
    strike_rate = round((total_runs / balls_faced) * 100, 2) if balls_faced > 0 else 0
    centuries = (innings_data['batsman_runs'] >= 100).sum()
    half_centuries = ((innings_data['batsman_runs'] >= 50) & (innings_data['batsman_runs'] < 100)).sum()

    return {
        "player": player,
        "opposing_team": opposing_team,
        "innings_played": innings_played,
        "total_runs": total_runs,
        "balls_faced": balls_faced,
        "average": average,
        "strike_rate": strike_rate,
        "centuries": centuries,
        "half_centuries": half_centuries
    }

def batsman_season_highest_score(player, season):
    """
    Returns the highest score by a player in a specific season.
    """
    season_matches_ids = matches[matches['season'] == season]['match_id']
    player_season_df = deliveries[
        (deliveries['striker'] == player) &
        (deliveries['match_id'].isin(season_matches_ids))
    ]

    if player_season_df.empty:
        return {"player": player, "season": season, "message": "No data found for player in this season."}

    runs_per_innings = player_season_df.groupby(['match_id', 'innings'])['batsman_runs'].sum()
    if runs_per_innings.empty:
        return {"player": player, "season": season, "highest_score": 0}

    return {"player": player, "season": season, "highest_score": int(runs_per_innings.max())}

def batsman_most_runs_in_an_over(player):
    """
    Returns the highest runs scored by a batsman in a single over.
    """
    player_df = deliveries[deliveries['striker'] == player]
    if player_df.empty:
        return {"player": player, "message": "No data found for this player."}

    runs_per_over = player_df.groupby(['match_id', 'innings', 'over'])['batsman_runs'].sum()
    if runs_per_over.empty:
        return {"player": player, "most_runs_in_over": 0}

    max_runs_over = runs_per_over.max()
    return {"player": player, "most_runs_in_over": int(max_runs_over)}

def batsman_innings_with_most_fours(player):
    """
    Returns the match and innings where a batsman hit the most fours.
    """
    player_fours = deliveries[(deliveries['striker'] == player) & (deliveries['batsman_runs'] == 4)]
    if player_fours.empty:
        return {"player": player, "message": "No fours found for this player."}

    fours_per_innings = player_fours.groupby(['match_id', 'innings']).size().reset_index(name='fours_count')
    if fours_per_innings.empty:
        return {"player": player, "message": "No innings with fours found."}

    best_innings = fours_per_innings.loc[fours_per_innings['fours_count'].idxmax()]
    return {
        "player": player,
        "match_id": best_innings['match_id'],
        "innings": best_innings['innings'],
        "fours_count": int(best_innings['fours_count'])
    }

def batsman_innings_with_most_sixes(player):
    """
    Returns the match and innings where a batsman hit the most sixes.
    """
    player_sixes = deliveries[(deliveries['striker'] == player) & (deliveries['batsman_runs'] == 6)]
    if player_sixes.empty:
        return {"player": player, "message": "No sixes found for this player."}

    sixes_per_innings = player_sixes.groupby(['match_id', 'innings']).size().reset_index(name='sixes_count')
    if sixes_per_innings.empty:
        return {"player": player, "message": "No innings with sixes found."}

    best_innings = sixes_per_innings.loc[sixes_per_innings['sixes_count'].idxmax()]
    return {
        "player": player,
        "match_id": best_innings['match_id'],
        "innings": best_innings['innings'],
        "sixes_count": int(best_innings['sixes_count'])
    }

def batsman_fastest_strike_rate_innings(player, min_balls=10):
    """
    Returns the innings with the highest strike rate for a batsman (minimum balls faced).
    """
    player_innings = deliveries[deliveries['striker'] == player].groupby(['match_id', 'innings'])

    innings_stats = []
    for (match_id, innings), df in player_innings:
        total_runs = df['batsman_runs'].sum()
        balls_faced = df[df['extra_type'] != 'wides'].shape[0]
        if balls_faced >= min_balls:
            strike_rate = round((total_runs / balls_faced) * 100, 2)
            innings_stats.append({
                'match_id': match_id,
                'innings': innings,
                'runs': total_runs,
                'balls_faced': balls_faced,
                'strike_rate': strike_rate
            })

    innings_stats_df = pd.DataFrame(innings_stats)
    if innings_stats_df.empty:
        return {"player": player, "message": f"No innings found with at least {min_balls} balls faced."}

    fastest_innings = innings_stats_df.loc[innings_stats_df['strike_rate'].idxmax()]
    return fastest_innings.to_dict()

def batsman_slowest_strike_rate_innings(player, min_balls=10):
    """
    Returns the innings with the lowest strike rate for a batsman (minimum balls faced).
    """
    player_innings = deliveries[deliveries['striker'] == player].groupby(['match_id', 'innings'])

    innings_stats = []
    for (match_id, innings), df in player_innings:
        total_runs = df['batsman_runs'].sum()
        balls_faced = df[df['extra_type'] != 'wides'].shape[0]
        if balls_faced >= min_balls:
            strike_rate = round((total_runs / balls_faced) * 100, 2)
            innings_stats.append({
                'match_id': match_id,
                'innings': innings,
                'runs': total_runs,
                'balls_faced': balls_faced,
                'strike_rate': strike_rate
            })

    innings_stats_df = pd.DataFrame(innings_stats)
    if innings_stats_df.empty:
        return {"player": player, "message": f"No innings found with at least {min_balls} balls faced."}

    slowest_innings = innings_stats_df.loc[innings_stats_df['strike_rate'].idxmin()]
    return slowest_innings.to_dict()

def batsman_total_dismissals(player):
    """
    Calculates the total number of times a batsman was dismissed.
    """
    total_dismissals = deliveries[deliveries['dismissed_player'] == player].shape[0]
    return {"player": player, "total_dismissals": total_dismissals}

def batsman_balls_per_boundary(player):
    """
    Calculates the average number of balls a batsman faces per boundary (4s or 6s).
    """
    player_df = deliveries[deliveries['striker'] == player]
    balls_faced = player_df[player_df['extra_type'] != 'wides'].shape[0]
    boundaries = player_df[(player_df['batsman_runs'] == 4) | (player_df['batsman_runs'] == 6)].shape[0]

    balls_per_boundary = round(balls_faced / boundaries, 2) if boundaries > 0 else float('inf')

    return {"player": player, "balls_faced": balls_faced, "total_boundaries": boundaries, "balls_per_boundary": balls_per_boundary}

def batsman_mom_awards_count(player):
    """
    Counts the number of Player of the Match awards for a batsman.
    """
    mom_awards = matches[matches['player_of_match'] == player].shape[0]
    return {"player": player, "player_of_match_awards": mom_awards}

def bowler_wickets_against_batting_style(bowler_name, batting_style_category):
    """
    Calculates wickets taken by a bowler against a specific batting style (e.g., 'Right-hand bat', 'Left-hand bat').
    Requires 'players' DataFrame to have 'batting_style'.
    """
    # Get batsmen matching the style category
    target_batsmen_df = players[players['batting_style'] == batting_style_category]

    if target_batsmen_df.empty:
        return {"bowler": bowler_name, "category": batting_style_category, "message": f"No batsmen found for category '{batting_style_category}'."}

    target_batsmen_names = target_batsmen_df['player_name'].unique()

    # Filter deliveries where the bowler bowled to these batsmen and took a wicket
    bowling_vs_style_df = deliveries[
        (deliveries['bowler'] == bowler_name) &
        (deliveries['striker'].isin(target_batsmen_names)) &
        (deliveries['is_wicket'] == 1)
    ]

    return {"bowler": bowler_name, "batting_style_category": batting_style_category, "wickets": bowling_vs_style_df.shape[0]}


def bowler_economy_in_death_overs_average(bowler):
    """
    Calculates the average economy rate of a bowler in death overs (16-20).
    """
    death_overs_df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['over'] > 15)]
    if death_overs_df.empty:
        return {"bowler": bowler, "message": "No death over data for this bowler."}

    total_runs_conceded = death_overs_df['total_runs'].sum()
    balls_bowled = death_overs_df[death_overs_df['extra_type'] != 'wides'].shape[0]
    overs_bowled = balls_bowled / 6

    economy = round(total_runs_conceded / overs_bowled, 2) if overs_bowled > 0 else float('inf')
    return {"bowler": bowler, "death_overs_economy": economy}


def bowler_average_balls_per_wicket(bowler):
    """
    Calculates the average number of balls a bowler bowls per wicket (strike rate in terms of balls).
    """
    bowler_df = deliveries[deliveries['bowler'] == bowler]
    balls_bowled = bowler_df[bowler_df['extra_type'] != 'wides'].shape[0]
    wickets = bowler_df['is_wicket'].sum()

    balls_per_wicket = round(balls_bowled / wickets, 2) if wickets > 0 else float('inf')
    return {"bowler": bowler, "balls_bowled": balls_bowled, "wickets": wickets, "balls_per_wicket": balls_per_wicket}


def bowler_runs_conceded_per_match_average(bowler):
    """
    Calculates the average runs conceded by a bowler per match they bowled in.
    """
    bowler_matches = deliveries[deliveries['bowler'] == bowler]['match_id'].nunique()
    if bowler_matches == 0:
        return {"bowler": bowler, "message": "Bowler has not bowled in any matches."}

    total_runs_conceded = deliveries[deliveries['bowler'] == bowler]['total_runs'].sum()

    return {"bowler": bowler, "average_runs_conceded_per_match": round(total_runs_conceded / bowler_matches, 2)}


def bowler_dot_ball_percentage_in_phase(bowler, phase):
    """
    Calculates the percentage of dot balls bowled by a bowler in a specific innings phase.
    - Powerplay: overs 1-6
    - Middle overs: overs 7-15
    - Death overs: overs 16-20
    """
    if phase.lower() == 'powerplay':
        phase_df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['over'] <= 6)]
    elif phase.lower() == 'middle':
        phase_df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['over'] > 6) & (deliveries['over'] <= 15)]
    elif phase.lower() == 'death':
        phase_df = deliveries[(deliveries['bowler'] == bowler) & (deliveries['over'] > 15)]
    else:
        return {"bowler": bowler, "message": "Invalid phase. Use 'powerplay', 'middle', or 'death'."}

    if phase_df.empty:
        return {"bowler": bowler, "phase": phase, "message": "No bowling data for this phase."}

    total_balls = phase_df[phase_df['extra_type'] != 'wides'].shape[0]
    dot_balls = phase_df[(phase_df['total_runs'] == 0) & (phase_df['extra_type'].isna())].shape[0]

    dot_ball_pct = round((dot_balls / total_balls) * 100, 2) if total_balls > 0 else 0
    return {"bowler": bowler, "phase": phase, "dot_ball_percentage": dot_ball_pct}


def bowler_wickets_per_match_average(bowler):
    """
    Calculates the average wickets taken by a bowler per match they bowled in.
    """
    bowler_matches = deliveries[deliveries['bowler'] == bowler]['match_id'].nunique()
    if bowler_matches == 0:
        return {"bowler": bowler, "message": "Bowler has not bowled in any matches."}

    total_wickets = deliveries[deliveries['bowler'] == bowler]['is_wicket'].sum()

    return {"bowler": bowler, "average_wickets_per_match": round(total_wickets / bowler_matches, 2)}


def bowler_performance_against_team(player, opposing_team):
    """
    Provides comprehensive stats (wickets, economy, avg, SR) for a bowler against a specific team.
    """
    bowler_vs_team_df = deliveries[
        (deliveries['bowler'] == player) &
        (deliveries['batting_team'] == opposing_team)
    ]

    if bowler_vs_team_df.empty:
        return {"player": player, "opposing_team": opposing_team, "message": "No data found for this matchup."}

    total_runs_conceded = bowler_vs_team_df['total_runs'].sum()
    balls_bowled = bowler_vs_team_df[bowler_vs_team_df['extra_type'] != 'wides'].shape[0]
    wickets = bowler_vs_team_df['is_wicket'].sum()
    overs_bowled = balls_bowled / 6

    economy = round(total_runs_conceded / overs_bowled, 2) if overs_bowled > 0 else float('inf')
    average = round(total_runs_conceded / wickets, 2) if wickets > 0 else float('inf')
    strike_rate = round(balls_bowled / wickets, 2) if wickets > 0 else float('inf')

    return {
        "player": player,
        "opposing_team": opposing_team,
        "total_runs_conceded": total_runs_conceded,
        "balls_bowled": balls_bowled,
        "wickets": wickets,
        "economy": economy,
        "average": average,
        "strike_rate": strike_rate
    }

def bowler_season_most_wickets(player, season):
    """
    Returns the total wickets taken by a bowler in a specific season.
    """
    season_matches_ids = matches[matches['season'] == season]['match_id']
    player_season_df = deliveries[
        (deliveries['bowler'] == player) &
        (deliveries['match_id'].isin(season_matches_ids))
    ]

    if player_season_df.empty:
        return {"player": player, "season": season, "message": "No data found for bowler in this season."}

    total_wickets = player_season_df['is_wicket'].sum()
    return {"player": player, "season": season, "total_wickets": int(total_wickets)}

def bowler_most_runs_conceded_in_an_over(player):
    """
    Returns the highest runs conceded by a bowler in a single over.
    """
    player_df = deliveries[deliveries['bowler'] == player]
    if player_df.empty:
        return {"player": player, "message": "No data found for this player."}

    runs_per_over = player_df.groupby(['match_id', 'innings', 'over'])['total_runs'].sum()
    if runs_per_over.empty:
        return {"player": player, "most_runs_conceded_in_over": 0}

    max_runs_over = runs_per_over.max()
    return {"player": player, "most_runs_conceded_in_over": int(max_runs_over)}

def bowler_best_economy_innings(player, min_overs=2):
    """
    Returns the innings with the best economy for a bowler (minimum overs bowled).
    """
    player_innings = deliveries[deliveries['bowler'] == player].groupby(['match_id', 'innings'])

    innings_stats = []
    for (match_id, innings), df in player_innings:
        total_runs_conceded = df['total_runs'].sum()
        balls_bowled = df[df['extra_type'] != 'wides'].shape[0]
        overs_bowled = balls_bowled / 6

        if overs_bowled >= min_overs:
            economy = round(total_runs_conceded / overs_bowled, 2) if overs_bowled > 0 else float('inf')
            innings_stats.append({
                'match_id': match_id,
                'innings': innings,
                'runs_conceded': total_runs_conceded,
                'overs_bowled': round(overs_bowled, 1),
                'economy': economy
            })

    innings_stats_df = pd.DataFrame(innings_stats)
    if innings_stats_df.empty:
        return {"player": player, "message": f"No innings found with at least {min_overs} overs bowled."}

    best_economy_innings = innings_stats_df.loc[innings_stats_df['economy'].idxmin()]
    return best_economy_innings.to_dict()

def bowler_worst_economy_innings(player, min_overs=2):
    """
    Returns the innings with the worst economy for a bowler (minimum overs bowled).
    """
    player_innings = deliveries[deliveries['bowler'] == player].groupby(['match_id', 'innings'])

    innings_stats = []
    for (match_id, innings), df in player_innings:
        total_runs_conceded = df['total_runs'].sum()
        balls_bowled = df[df['extra_type'] != 'wides'].shape[0]
        overs_bowled = balls_bowled / 6

        if overs_bowled >= min_overs:
            economy = round(total_runs_conceded / overs_bowled, 2) if overs_bowled > 0 else float('inf')
            innings_stats.append({
                'match_id': match_id,
                'innings': innings,
                'runs_conceded': total_runs_conceded,
                'overs_bowled': round(overs_bowled, 1),
                'economy': economy
            })

    innings_stats_df = pd.DataFrame(innings_stats)
    if innings_stats_df.empty:
        return {"player": player, "message": f"No innings found with at least {min_overs} overs bowled."}

    worst_economy_innings = innings_stats_df.loc[innings_stats_df['economy'].idxmax()]
    return worst_economy_innings.to_dict()

def bowler_most_maiden_overs_in_match(player):
    """
    Returns the match and count of most maiden overs bowled by a player in a single match.
    """
    player_bowling = deliveries[deliveries['bowler'] == player]
    if player_bowling.empty:
        return {"player": player, "message": "No bowling data found for this player."}

    # Calculate runs conceded per over
    runs_per_over = player_bowling.groupby(['match_id', 'innings', 'over'])['total_runs'].sum()
    # Identify maiden overs (0 runs conceded)
    maiden_overs = runs_per_over[runs_per_over == 0]

    if maiden_overs.empty:
        return {"player": player, "most_maidens_in_match": 0}

    # Count maidens per match
    maidens_per_match = maiden_overs.groupby('match_id').size().reset_index(name='maiden_count')

    if maidens_per_match.empty:
        return {"player": player, "most_maidens_in_match": 0}

    best_match = maidens_per_match.loc[maidens_per_match['maiden_count'].idxmax()]
    return {"player": player, "match_id": best_match['match_id'], "most_maidens_in_match": int(best_match['maiden_count'])}

def bowler_most_dot_balls_in_match(player):
    """
    Returns the match and count of most dot balls bowled by a player in a single match.
    """
    player_dots = deliveries[
        (deliveries['bowler'] == player) &
        (deliveries['total_runs'] == 0) &
        (deliveries['extra_type'].isna()) # Ensure it's a legal delivery
    ]

    if player_dots.empty:
        return {"player": player, "message": "No dot balls found for this player."}

    dot_balls_per_match = player_dots.groupby('match_id').size().reset_index(name='dot_ball_count')
    if dot_balls_per_match.empty:
        return {"player": player, "most_dot_balls_in_match": 0}

    best_match = dot_balls_per_match.loc[dot_balls_per_match['dot_ball_count'].idxmax()]
    return {"player": player, "match_id": best_match['match_id'], "most_dot_balls_in_match": int(best_match['dot_ball_count'])}

def bowler_wickets_caught(player):
    """
    Calculates total wickets taken by a bowler via 'caught' dismissal type.
    """
    caught_wickets = deliveries[
        (deliveries['bowler'] == player) &
        (deliveries['dismissal_type'] == 'caught')
    ].shape[0]
    return {"player": player, "caught_wickets": caught_wickets}

def bowler_total_balls_bowled(player):
    """
    Calculates the total number of legal balls bowled by a player.
    """
    total_balls = deliveries[
        (deliveries['bowler'] == player) &
        (deliveries['extra_type'] != 'wides') &
        (deliveries['extra_type'] != 'noballs')
    ].shape[0]
    return {"player": player, "total_legal_balls_bowled": total_balls}

def bowler_match_winning_wickets(player):
    """
    Calculates total wickets taken by a bowler in matches where their team won.
    """
    # Merge deliveries with matches to get winner information for each ball
    bowler_data = deliveries[deliveries['bowler'] == player].merge(
        matches[['match_id', 'winner', 'team1', 'team2']], on='match_id', how='left'
    )

    # Determine the bowling team for each delivery
    bowler_data['bowling_team'] = bowler_data.apply(
        lambda row: row['team1'] if row['innings'] in [1, 3] else row['team2'], axis=1 # Assuming innings 1/3 for team1, 2/4 for team2
    )

    # Filter for wickets taken when the bowling team is the winner
    winning_wickets = bowler_data[
        (bowler_data['is_wicket'] == 1) &
        (bowler_data['winner'] == bowler_data['bowling_team'])
    ].shape[0]

    return {"player": player, "match_winning_wickets": winning_wickets}

def bowler_maidens(player):
    """
    Calculates the total number of maiden overs bowled by a bowler.
    """
    player_bowling = deliveries[deliveries['bowler'] == player]
    if player_bowling.empty:
        return 0

    overs_bowled = player_bowling.groupby(['match_id', 'innings', 'over'])['total_runs'].sum()
    maidens = (overs_bowled == 0).sum()
    return maidens

def bowler_wickets_in_powerplay(player):
    """
    Calculates wickets taken by a bowler in the powerplay overs (1-6).
    """
    powerplay_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] <= 6)]
    return powerplay_df['is_wicket'].sum()

def bowler_wickets_in_middle_overs(player):
    """
    Calculates wickets taken by a bowler in middle overs (7-15).
    """
    middle_overs_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] > 6) & (deliveries['over'] <= 15)]
    return middle_overs_df['is_wicket'].sum()

def bowler_wickets_in_death_overs(player):
    """
    Calculates wickets taken by a bowler in death overs (16-20).
    """
    death_overs_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] > 15)]
    return death_overs_df['is_wicket'].sum()

def bowler_runs_conceded_in_powerplay(player):
    """
    Calculates runs conceded by a bowler in powerplay overs (1-6).
    """
    powerplay_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] <= 6)]
    return powerplay_df['total_runs'].sum()

def bowler_runs_conceded_in_death_overs(player):
    """
    Calculates runs conceded by a bowler in death overs (16-20).
    """
    death_overs_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] > 15)]
    return death_overs_df['total_runs'].sum()

def bowler_best_figures_match(player):
    """
    Returns the best bowling figures (wickets and runs) in a single match for a bowler.
    """
    player_bowling = deliveries[deliveries['bowler'] == player]
    if player_bowling.empty:
        return {"player": player, "message": "No bowling data found for this player."}

    match_stats = player_bowling.groupby('match_id').agg(
        wickets=('is_wicket', 'sum'),
        runs=('total_runs', 'sum')
    ).reset_index()

    if match_stats.empty:
        return {"player": player, "message": "No wickets taken or runs conceded."}

    # Sort by wickets (descending), then by runs (ascending)
    best_figure = match_stats.sort_values(by=['wickets', 'runs'], ascending=[False, True]).iloc[0]

    return {
        "player": player,
        "best_wickets": int(best_figure['wickets']),
        "best_runs": int(best_figure['runs']),
        "match_id": best_figure['match_id']
    }

def bowler_wickets_in_wins(player):
    """
    Calculates total wickets taken by a bowler in matches where their team won.
    """
    player_bowling_matches = deliveries[deliveries['bowler'] == player].merge(matches, on='match_id', how='left')
    winning_wickets_df = player_bowling_matches[player_bowling_matches['winner'] == player_bowling_matches['bowling_team']]
    return winning_wickets_df['is_wicket'].sum()

def bowler_dismissal_types_breakdown(player):
    """
    Returns the breakdown of dismissal types for a bowler's wickets.
    """
    bowler_wickets = deliveries[(deliveries['bowler'] == player) & (deliveries['is_wicket'] == 1)]
    if bowler_wickets.empty:
        return {"player": player, "message": "No wickets taken by this bowler or no data."}

    dismissal_counts = bowler_wickets['dismissal_type'].value_counts().to_dict()
    return {"player": player, "dismissal_types": dismissal_counts}

def bowler_strike_rate_by_season(player):
    """
    Calculates season-wise bowling strike rate for a bowler.
    """
    player_bowling_season = deliveries[deliveries['bowler'] == player].merge(matches[['match_id', 'season']], on='match_id', how='left')
    if player_bowling_season.empty:
        return {"player": player, "message": "No bowling data found for this player."}

    season_stats = player_bowling_season.groupby('season').agg(
        balls_bowled=('ball', 'count'), # Counting 'ball' to represent balls bowled
        wickets=('is_wicket', 'sum')
    ).reset_index()

    season_stats['strike_rate'] = season_stats.apply(
        lambda row: round(row['balls_bowled'] / row['wickets'], 2) if row['wickets'] > 0 else float('inf'), axis=1
    )
    return season_stats[['season', 'strike_rate']]


# --- QUESTIONS 21-40 QA IMPLEMENTATIONS & ALIASES ---

def player_fifties(player):
    """Q21: How many half-centuries (50-99 runs) has a player scored?"""
    p_df = deliveries[deliveries['striker'] == player]
    if p_df.empty:
        return {"player": player, "fifties": 0}
    inn_runs = p_df.groupby(['match_id', 'innings'])['batsman_runs'].sum()
    fifties = int(((inn_runs >= 50) & (inn_runs < 100)).sum())
    return {"player": player, "fifties": fifties}

def player_fours(player):
    """Q22: How many fours has a player hit?"""
    fours = int(deliveries[(deliveries['striker'] == player) & (deliveries['batsman_runs'] == 4)].shape[0])
    return {"player": player, "fours": fours}

def player_runs_by_season(player):
    """Q23: What are a player's runs scored season-wise?"""
    merged = matches[['match_id', 'season']].merge(deliveries[deliveries['striker'] == player], on='match_id', how='inner')
    if merged.empty:
        return []
    season_runs = merged.groupby('season')['batsman_runs'].sum().reset_index()
    season_runs.columns = ['season', 'runs']
    return season_runs.to_dict(orient='records')

def player_stats_against_team(player, team):
    """Q24: What are a player's stats against a specific team?"""
    merged = matches[['match_id', 'team1', 'team2']].merge(deliveries[(deliveries['striker'] == player) & (deliveries['bowling_team'] == team)], on='match_id', how='inner')
    if merged.empty:
        return {"player": player, "against_team": team, "matches": 0, "innings": 0, "runs": 0, "average": 0.0, "strike_rate": 0.0, "highest_score": 0}
    total_matches = merged['match_id'].nunique()
    inn_grouped = merged.groupby(['match_id', 'innings'])['batsman_runs'].sum()
    innings_count = len(inn_grouped)
    runs = int(merged['batsman_runs'].sum())
    highest_score = int(inn_grouped.max()) if not inn_grouped.empty else 0
    legal_balls = merged[~merged['extra_type'].isin(['wides'])].shape[0]
    strike_rate = round(float((runs / legal_balls) * 100), 2) if legal_balls > 0 else 0.0
    dismissals = merged[merged['dismissed_player'] == player].shape[0]
    average = round(float(runs / dismissals), 2) if dismissals > 0 else float(runs)
    return {
        "player": player,
        "against_team": team,
        "matches": total_matches,
        "innings": innings_count,
        "runs": runs,
        "average": average,
        "strike_rate": strike_rate,
        "highest_score": highest_score
    }

def player_stats_at_venue(player, venue):
    """Q25: What are a player's stats at a specific venue?"""
    merged = matches[['match_id', 'venue']].merge(deliveries[deliveries['striker'] == player], on='match_id', how='inner')
    venue_matches = merged[merged['venue'].str.contains(venue, case=False, na=False)]
    if venue_matches.empty:
        return {"player": player, "venue": venue, "matches": 0, "innings": 0, "runs": 0, "average": 0.0, "strike_rate": 0.0, "highest_score": 0}
    total_matches = venue_matches['match_id'].nunique()
    inn_grouped = venue_matches.groupby(['match_id', 'innings'])['batsman_runs'].sum()
    innings_count = len(inn_grouped)
    runs = int(venue_matches['batsman_runs'].sum())
    highest_score = int(inn_grouped.max()) if not inn_grouped.empty else 0
    legal_balls = venue_matches[~venue_matches['extra_type'].isin(['wides'])].shape[0]
    strike_rate = round(float((runs / legal_balls) * 100), 2) if legal_balls > 0 else 0.0
    dismissals = venue_matches[venue_matches['dismissed_player'] == player].shape[0]
    average = round(float(runs / dismissals), 2) if dismissals > 0 else float(runs)
    return {
        "player": player,
        "venue": venue,
        "matches": total_matches,
        "innings": innings_count,
        "runs": runs,
        "average": average,
        "strike_rate": strike_rate,
        "highest_score": highest_score
    }

def top_wicket_takers(top_n=5):
    """Q26: Who are the top N wicket-takers overall?"""
    w_types = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    w_df = deliveries[(deliveries['is_wicket'] == 1) & (deliveries['dismissal_type'].isin(w_types))]
    w_counts = w_df.groupby('bowler')['is_wicket'].sum()
    m_counts = deliveries.groupby('bowler')['match_id'].nunique()
    res = pd.DataFrame({
        'player': w_counts.index,
        'wickets': w_counts.values,
        'matches': m_counts.reindex(w_counts.index).values
    }).sort_values('wickets', ascending=False).head(top_n)
    return res.to_dict(orient='records')

def player_wickets_by_season(player):
    """Q28: What are a bowler's wickets by season?"""
    merged = matches[['match_id', 'season']].merge(deliveries[deliveries['bowler'] == player], on='match_id', how='inner')
    w_types = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    if merged.empty:
        return []
    s_df = merged.groupby('season').apply(lambda df: (df['is_wicket'] == 1) & (df['dismissal_type'].isin(w_types))).reset_index()
    s_wickets = merged.groupby('season').apply(lambda df: ((df['is_wicket'] == 1) & (df['dismissal_type'].isin(w_types))).sum()).reset_index()
    s_wickets.columns = ['season', 'wickets']
    return s_wickets.to_dict(orient='records')

def player_wickets_against_team(player, team):
    """Q29: Wickets taken by a bowler against a specific team"""
    w_types = ['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']
    w_df = deliveries[(deliveries['bowler'] == player) & (deliveries['batting_team'] == team) & (deliveries['is_wicket'] == 1) & (deliveries['dismissal_type'].isin(w_types))]
    wickets = int(w_df.shape[0])
    return {"player": player, "against_team": team, "wickets": wickets}

def player_dot_ball_percentage(player):
    """Q30: Dot ball percentage of a bowler"""
    b_df = deliveries[deliveries['bowler'] == player]
    if b_df.empty:
        return {"player": player, "dot_ball_percentage": 0.0}
    dots = b_df[b_df['total_runs'] == 0].shape[0]
    total_balls = b_df.shape[0]
    pct = round(float(dots / total_balls * 100), 2) if total_balls > 0 else 0.0
    return {"player": player, "dot_ball_percentage": pct}

def head_to_head(team1, team2):
    """Q31: Head to head record between two teams"""
    m = matches[((matches['team1'] == team1) & (matches['team2'] == team2)) | ((matches['team1'] == team2) & (matches['team2'] == team1))]
    total = len(m)
    t1_wins = int((m['winner'] == team1).sum())
    t2_wins = int((m['winner'] == team2).sum())
    ties = int((m['result'] == 'tie').sum())
    no_results = int((m['result'] == 'no result').sum())
    return {
        "team1": team1,
        "team2": team2,
        "total_matches": total,
        "team1_wins": t1_wins,
        "team2_wins": t2_wins,
        "ties": ties,
        "no_results": no_results
    }

def highest_successful_chase():
    """Q32: Highest successful chase in IPL history"""
    chases = matches[matches['second_innings_score'] > matches['first_innings_score']]
    if chases.empty:
        return {"error": "No successful chases found"}
    best = chases.loc[chases['second_innings_score'].idxmax()]
    return {
        "winner": str(best['winner']),
        "chased_score": int(best['second_innings_score']),
        "target": int(best['first_innings_score'] + 1),
        "against": str(best['team1'] if best['winner'] == best['team2'] else best['team2']),
        "match_id": str(best['match_id']),
        "season": int(best['season']),
        "venue": str(best['venue']),
        "date": str(best['date'])
    }

def closest_margin_match():
    """Q33: Match with the closest margin in terms of runs"""
    margin_matches = matches[(matches['win_by'] == 'runs') & (matches['win_margin'] > 0)]
    if margin_matches.empty:
        return {"error": "No run margin matches found"}
    closest = margin_matches.loc[margin_matches['win_margin'].idxmin()]
    return {
        "winner": str(closest['winner']),
        "margin": int(closest['win_margin']),
        "against": str(closest['team2'] if closest['winner'] == closest['team1'] else closest['team1']),
        "match_id": str(closest['match_id']),
        "season": int(closest['season']),
        "venue": str(closest['venue']),
        "date": str(closest['date'])
    }

def closest_win_by_runs():
    return closest_margin_match()

def biggest_win_by_runs():
    """Q34: Match with the biggest win in terms of runs"""
    margin_matches = matches[matches['win_by'] == 'runs']
    if margin_matches.empty:
        return {"error": "No run margin matches found"}
    biggest = margin_matches.loc[margin_matches['win_margin'].idxmax()]
    return {
        "winner": str(biggest['winner']),
        "margin": int(biggest['win_margin']),
        "against": str(biggest['team2'] if biggest['winner'] == biggest['team1'] else biggest['team1']),
        "match_id": str(biggest['match_id']),
        "season": int(biggest['season']),
        "venue": str(biggest['venue']),
        "date": str(biggest['date'])
    }

def unique_teams():
    """Q35: All unique team names in the dataset"""
    t1 = set(matches['team1'].dropna().unique())
    t2 = set(matches['team2'].dropna().unique())
    teams = sorted(list(t1.union(t2)))
    return teams

def all_teams():
    return unique_teams()

def top_teams_by_win_percentage(top_n=3):
    """Q36: Top N teams by win percentage (min 10 matches)"""
    teams = unique_teams()
    res = []
    for t in teams:
        tot_m = matches[(matches['team1'] == t) | (matches['team2'] == t)].shape[0]
        if tot_m < 10:
            continue
        wins = matches[matches['winner'] == t].shape[0]
        win_pct = round(float(wins / tot_m * 100), 2)
        res.append({"team": t, "win_percentage": win_pct, "matches": tot_m, "wins": wins})
    res.sort(key=lambda x: x['win_percentage'], reverse=True)
    return res[:top_n]

def team_win_percentage_after_winning_toss(team):
    """Q37: Team win percentage after winning toss"""
    toss_df = matches[matches['toss_winner'] == team]
    if toss_df.empty:
        return {"team": team, "win_percentage": 0.0, "tosses_won": 0, "matches_won": 0}
    tosses_won = len(toss_df)
    matches_won = int((toss_df['winner'] == team).sum())
    pct = round(float(matches_won / tosses_won * 100), 2)
    return {"team": team, "win_percentage": pct, "tosses_won": tosses_won, "matches_won": matches_won}

def player_strike_rate_in_successful_chases(player):
    """Q38: Player strike rate in successful chases"""
    merged = matches[['match_id', 'winner']].merge(deliveries[(deliveries['striker'] == player) & (deliveries['innings'] == 2)], on='match_id', how='inner')
    succ_chase = merged[merged['winner'] == merged['batting_team']]
    if succ_chase.empty:
        return {"player": player, "strike_rate": 0.0}
    runs = succ_chase['batsman_runs'].sum()
    balls = succ_chase[~succ_chase['extra_type'].isin(['wides'])].shape[0]
    sr = round(float(runs / balls * 100), 2) if balls > 0 else 0.0
    return {"player": player, "strike_rate": sr}

def player_strike_rate_in_chases(player):
    return player_strike_rate_in_successful_chases(player)

def player_economy_death_overs(player):
    """Q39: Average economy rate of bowler in death overs (16-20)"""
    d_df = deliveries[(deliveries['bowler'] == player) & (deliveries['over'] >= 16)]
    if d_df.empty:
        return {"player": player, "death_overs_economy": 0.0}
    runs = d_df['total_runs'].sum()
    legal_balls = d_df[~d_df['extra_type'].isin(['wides', 'noballs'])].shape[0]
    overs = legal_balls / 6
    eco = round(float(runs / overs), 2) if overs > 0 else 0.0
    return {"player": player, "death_overs_economy": eco}

def player_strike_rate(player):
    """Q40: Player overall strike rate"""
    p_df = deliveries[deliveries['striker'] == player]
    if p_df.empty:
        return {"player": player, "strike_rate": 0.0}
    runs = p_df['batsman_runs'].sum()
    balls = p_df[~p_df['extra_type'].isin(['wides'])].shape[0]
    sr = round(float(runs / balls * 100), 2) if balls > 0 else 0.0
    return {"player": player, "strike_rate": sr}