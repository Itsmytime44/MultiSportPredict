#!/usr/bin/env python
"""
predict.py
==========
Simplified CLI for running predictions automatically without manual data entry.

Examples:
  python predict.py mexico "South Africa"          # Predict Mexico vs South Africa (soccer)
  python predict.py --sport basketball lakers heat  # Basketball prediction
  python predict.py --upcoming --league epl         # Predict all upcoming EPL matches
  python predict.py --batch                         # Batch predict all sports

No CSV files or manual parameters needed!
"""

import sys
import argparse
from models.auto_dispatcher import AutoDispatcher, SOCCER_LEAGUES

def main():
    parser = argparse.ArgumentParser(
        description="Run predictions automatically without manual CSV entry"
    )
    
    # Positional args for quick matches
    parser.add_argument("home", nargs="?", help="Home team (space-separated if needed)")
    parser.add_argument("away", nargs="?", help="Away team")
    
    parser.add_argument(
        "--sport", "-s",
        default="soccer",
        choices=["soccer", "basketball", "kbo"],
        help="Sport (default: soccer)"
    )
    parser.add_argument(
        "--upcoming", "-u",
        action="store_true",
        help="Predict all upcoming matches in league"
    )
    parser.add_argument(
        "--league", "-l",
        default="epl",
        help=f"League (soccer only). Options: {', '.join(SOCCER_LEAGUES.keys())}"
    )
    parser.add_argument(
        "--batch", "-b",
        action="store_true",
        help="Batch mode: predict all upcoming matches for all sports"
    )
    parser.add_argument(
        "--api-key", "-k",
        help="The-Odds-API key (or set ODDS_API_KEY env var)"
    )

    args = parser.parse_args()
    
    dispatcher = AutoDispatcher(api_key=args.api_key)

    if args.batch:
        print("[*] Batch predicting all upcoming matches...\n")
        for sport in ["soccer", "basketball", "kbo"]:
            print(f"[{sport.upper()}]")
            if sport == "soccer":
                league_key = SOCCER_LEAGUES.get(args.league, "soccer_epl")
                dispatcher.predict_upcoming_league(league_key)
            print()

    elif args.upcoming:
        print(f"[*] Fetching upcoming {args.league.upper()} matches...\n")
        league_key = SOCCER_LEAGUES.get(args.league)
        if league_key:
            dispatcher.predict_upcoming_league(league_key)
        else:
            print(f"[ERROR] Unknown league: {args.league}")
            return 1

    elif args.home and args.away:
        print(f"[PREDICT] {args.sport.upper()} - {args.home} vs {args.away}\n")
        success = dispatcher.predict_match(args.sport, args.home, args.away)
        return 0 if success else 1

    else:
        parser.print_help()
        print("\n📚 QUICK EXAMPLES:")
        print("  python predict.py mexico 'south africa'")
        print("  python predict.py --sport basketball lakers heat")
        print("  python predict.py --upcoming --league champions_league")
        print("  python predict.py --batch")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
