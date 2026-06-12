from __future__ import annotations
import pandas as pd
from ingest.error_handling import safe_read_csv, safe_to_csv, logger


def load_upcoming_matches(csv_path="data/raw/upcoming_matches.csv"):
    df = safe_read_csv(csv_path)
    if df.empty:
        logger.warning("No upcoming matches loaded.")
    return df


def save_matches(df, out_path="data/processed/upcoming_matches.csv"):
    ok = safe_to_csv(df, out_path)
    if not ok:
        logger.error("Failed to save matches.")
    return ok
