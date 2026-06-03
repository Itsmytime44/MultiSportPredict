<<<<<<< HEAD
# Multi-Sport Predictor

## Overview
A machine learning model for predicting basketball and soccer match outcomes using data analysis and predictive modeling.

## Project Structure

MultiSportPredict/
├── data/
│ └── (raw and processed data files)
├── models/
│ └── (saved trained models)
├── src/
│ ├── preprocessing.py
│ ├── model.py
│ └── predictions.py
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
└── SETUP_GUIDE.md

## Getting Started

### Prerequisites
- Python 3.8+
- pip
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ItsMytime44/MultiSportPredict.git
   cd MultiSportPredict
=======
# MultiSportPredict
overview
This file implements a self‑contained “handicapping” and projection model for European basketball (EuroLeague) games, focused on evaluating a single matchup and producing betting‑oriented outputs (win probabilities, spreads, totals, and recommendations). It also analyzes soccer matches and handicaps for the project goals total and corners total with recommendations as well as pass.

At a high level it:

Scrapes advanced EuroLeague team stats from RealGM.
Defines basic data structures for holding team stats and matchup context.
Provides utility functions for:
Generic math (clamp, sigmoid).
Interaction (console prompts).
Logging model runs to CSV.
Implements a set of basketball‑specific scoring functions to quantify:
Offensive/defensive efficiency and net rating gaps.
Pace differences.
Rest and travel fatigue.
Home/away splits.
Context (rotation depth, injuries, coaching, motivation).
Market alignment between model edge and betting line.
Aggregates these factors into a single “model edge” and converts it into win probabilities and betting recommendations.
Adds a separate first‑quarter (Q1) projection model.
Exposes a run_master_analysis() function that ties everything together and runs an end‑to‑end analysis, including printing results and logging to CSV.
Provides a __main__ block to run the full analysis as a script.
The file serves as the main modeling/analysis engine rather than a reusable library: it mixes business logic (modeling) with I/O (scraping, console prompts, printing, CSV logging) in one module.

key_components
Web scraping
scrape_realgm_euroleague_team_stats(season=2026)
Fetches EuroLeague advanced stats from RealGM for a given season.
Uses requests and pandas.read_html to parse the stats table.
Falls back to BeautifulSoup + read_html on the first table if automatic detection fails.
Returns a DataFrame with team stats.
Used both by run_master_analysis and load_euroleague_stats.
This is the module’s bridge to live data, though the master analysis currently uses hard‑coded team values rather than directly mapping this DataFrame into TeamStats or the modeling inputs.

Data structures
@dataclass TeamStats

Represents per‑team season stats: basic box score stats plus advanced metrics (pace, offensive/defensive/net rating).
Intended as a structured container but isn’t fully wired into the main analysis (the master analysis uses simple dicts instead).
@dataclass MatchupInput

Holds matchup‑specific context: home_team, away_team (TeamStats), rest days, neutral court, playoff flag, arena elevation.
Provides a high‑level abstraction for a game but is currently not used in run_master_analysis(). It’s more of a future‑proof/structural design element.
These classes signal an intent to evolve toward a more object‑oriented, reusable model API.

Utility functions
clamp(x, lo=0.0, hi=1.0)

Bounds a number between lo and hi.
Used in probability conversion routines.
sigmoid(x)

Standard logistic function, central to mapping “scores” into probabilities.
log_run_to_csv(log_row, filename=None)

Appends a single model run (dict) as a row to a CSV file.
Defaults to an output/euroleague_model_log.csv path relative to the script.
Ensures the output directory exists and handles first‑time creation vs append.
This makes model runs auditable and downstream‑friendly (e.g., for backtesting or analysis).

Interactive input helpers
prompt_float(text, default=None)

prompt_choice(text)

prompt_bool(text)

color_score(x)

Provide generic console prompts for numeric, categorical (green/yellow/red), and boolean inputs, plus a mapping from color to numeric score.
These are used in read_team but the main analysis currently uses hard‑coded values instead of prompting.
read_team(label, stats_df=None)

An interactive helper that gathers a full set of modeling inputs for a team: ratings, pace, rest/travel, context, and market lines.
Returns a dictionary of parameters with a consistent schema.
Not used by the default run_master_analysis, but useful if you want to turn the script into a fully interactive tool.
Basketball efficiency and scoring functions
These functions convert domain concepts into numbers that can be combined into an overall edge:

team_net_rating(ortg, drtg)

Simple ortg - drtg.
efficiency_gap(home_ortg, home_drtg, away_ortg, away_drtg)

Difference in net rating between home and away.
historical_efficiency_gap(current_gap, baseline_gap, recent_gap)

Blends current, baseline, and recent gaps to capture trend vs long‑term strength.
pace_edge(home_pace, away_pace)

Pace difference; used as a small weighted factor in the final edge.
rest_travel_score(rest_days, travel_km, back_to_back, three_games_six_days)

Penalizes travel and compressed schedules, rewards extra rest.
Produces a scalar “rest/travel” score, later differenced between teams.
home_away_score(home_split_edge, away_split_edge)

Encodes home/away performance differences as an advantage for the home team.
context_score(rotation_depth, injury_status, coach_stability, motivation)

Translates four green/yellow/red indicators into a numeric context score.
Heavier weights for rotation and injuries (±2), lighter for coach/motivation.
market_filter(open_line, current_line, model_edge)

Compares model edge to market movement and absolute line size.
Returns:
score: positive when model and market are reasonably aligned, negative when they diverge strongly or the line is large.
message: a descriptive string about line moves.
Integrates market information into the final recommendation to avoid going against strong line moves.
score_to_prob(score)

Converts a “total score” to a win probability using a shifted/scaled sigmoid and then clamps to [0,1].
Together these form the core of the “handicapping logic”: each domain component (efficiency, pace, rest, context, market) yields a numeric contribution; the weighted sum drives probabilities and betting leans.

Core analysis engine
run_master_analysis()
The main orchestration function.
Steps:
Prints headers/title.
Attempts to load RealGM data via scrape_realgm_euroleague_team_stats; if successful, prints a sample of the stats for context.
Defines two sample teams with hard‑coded parameters:
Home: “Orange Walk Running Rebels”
Away: “San Pedro Tiger Sharks” Each with ORTG, DRTG, baseline and recent net ratings, pace, rest, travel, context flags, and opening/current lines.
Computes:
Efficiency gap (current_gap), baseline and recent gaps, blended historical gap (hist_gap).
Pace gap (pace_gap).
Rest/travel scores for each team and their difference (rest_gap).
Home/away split gap (split_gap).
Context scores for each team and their difference (ctx_gap).
Aggregates these into model_edge using specific weights (e.g., historical gap weighted heavily, pace lightly).
Applies market_filter to get market_score; combines with model_edge into total_score.
Converts total_score to a home win probability (prob_home).
Derives a high‑level “lean”:
Strongly favor home if prob_home ≥ 0.60 and market filter is not negative.
Strongly favor away if prob_home ≤ 0.40 and market filter is not negative.
Otherwise “Pass”.
Calls project_first_quarter to compute Q1 projections.
Prints a comprehensive report:
Component gaps, market info, total score, probabilities, recommendation.
Q1 projected scores, spread, total, win probabilities, and context/pace factors.
Logs all results (including Q1 projections) to a CSV via log_run_to_csv.
Prints a final log confirmation.
This function is the entry point for running a complete model evaluation and is what __main__ invokes.

First‑quarter projections
project_first_quarter(home, away, home_team_name, away_team_name)
Builds a Q1‑specific projection model based on the same input schema used for the full‑game model.
Key logic:
Assumes typical Q1 possessions (avg_q1_possessions ~20 per team).
Scales offensive ratings down by 7% to reflect slower starts.
Adjusts expected Q1 points with opponent defensive ratings.
Applies pace factor based on average team pace vs a league baseline (70).
Adds a 5% home‑court boost specific to Q1.
Computes context scores and uses their difference as an additional Q1 adjustment (because starters/rotation matter more early).
Derives:
Home and away Q1 points.
Q1 spread and total.
Q1 win probability for the home team via a softer (higher variance) logistic transformation.
Q1 moneyline‑style probability accounting for a fixed tie chance (~8%).
Returns a dict with rounded projections and intermediate factors (pace factor, context adjustment).
This supplements the full‑game evaluation with an explicitly modeled first‑quarter market.

Data loading convenience
load_euroleague_stats(season=2026)
Wrapper around scrape_realgm_euroleague_team_stats with logging.
Returns the DataFrame or None on failure.
Intended for reuse when integrating the model into a larger system or preprocessing pipeline.
Script entry point
if __name__ == "__main__":
Executes run_master_analysis() when the file is run directly.
Catches and reports:
KeyboardInterrupt for graceful cancellation.
Generic exceptions, printing a stack trace for debugging.
This block makes the module runnable as a standalone CLI analysis tool while also allowing its components to be imported into other Python code.
