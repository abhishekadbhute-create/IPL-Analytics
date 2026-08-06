import pandas as pd
import os
from config import Config

def load_data():
    matches_path = os.path.join(Config.DATA_DIR, 'matches.csv')
    deliveries_path = os.path.join(Config.DATA_DIR, 'deliveries.csv')
    players_path = os.path.join(Config.DATA_DIR, 'players.csv')
    seasons_path = os.path.join(Config.DATA_DIR, 'seasons.csv')

    matches = pd.read_csv(matches_path) if os.path.exists(matches_path) else pd.DataFrame()
    deliveries = pd.read_csv(deliveries_path) if os.path.exists(deliveries_path) else pd.DataFrame()
    players = pd.read_csv(players_path) if os.path.exists(players_path) else pd.DataFrame()
    seasons = pd.read_csv(seasons_path) if os.path.exists(seasons_path) else pd.DataFrame()

    return matches, deliveries, players, seasons

# Load globally to be accessed by other modules
matches, deliveries, players, seasons = load_data()
