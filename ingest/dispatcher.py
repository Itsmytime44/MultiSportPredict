# predict/dispatcher.py
import sys
from predict.basketball_predict import run_basketball_game
from predict.soccer_predict import run_soccer_game
from predict.kbo_predict import run_kbo_game

SPORTS = {
    "basketball": run_basketball_game,
    "soccer": run_soccer_game,
    "kbo": run_kbo_game,
}

def dispatch(sport: str, home_team: str, away_team: str):
    sport = sport.lower().strip()
    if sport not in SPORTS:
        raise ValueError(f"Unsupported sport: {sport}")
    return SPORTS[sport](home_team, away_team)

def main():
    if len(sys.argv) < 4:
        print("Usage: python -m predict.dispatcher <sport> <home_team> <away_team>")
        sys.exit(1)

    sport = sys.argv[1]
    home_team = sys.argv[2]
    away_team = sys.argv[3]
    dispatch(sport, home_team, away_team)

if __name__ == "__main__":
    main()