"""
Soccer Feature Builder
======================
Transforms raw soccer match CSV data into the feature matrix expected
by models.soccer_model.SoccerModel.  Output CSV contains
SOCCER_FEATURE_COLS + id columns + target column.
"""

from __future__ import annotations

import pandas as pd

from config import (
    SOCCER_FEATURE_COLS,
    SOCCER_RAW_CSV,
    SOCCER_FEATURES_CSV,
    SOCCER_TARGET_COL,
)
from ingest.error_handling import safe_read_csv, safe_to_csv, logger


def build_soccer_features(
    raw_path: str | None = None,
    out_path: str | None = None,
) -> pd.DataFrame:
    """
    Read raw soccer matches, engineer feature columns, write to disk.

    Expected raw CSV columns (at minimum):
        home_team, away_team,
        home_xg, away_xg, home_xga, away_xga,
        home_shots, away_shots, home_corners, away_corners,
        home_form, away_form,
        sharp_score, reverse_line_movement, money_ticket_gap,
        public_tickets_pct, public_money_pct, total_goals
    """
    raw = safe_read_csv(str(raw_path or SOCCER_RAW_CSV))
    if raw.empty:
        logger.warning("No soccer raw data to build features from.")
        return raw

    df = raw.copy()

    # Ensure all FEATURE_COLS exist (fill missing with 0)
    for col in SOCCER_FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0.0

    # Preserve identity + target columns
    id_cols = ["home_team", "away_team"]
    keep_cols = id_cols + SOCCER_FEATURE_COLS
    if SOCCER_TARGET_COL in df.columns:
        keep_cols = keep_cols + [SOCCER_TARGET_COL]

    out_df = df[keep_cols].copy()

    safe_to_csv(out_df, str(out_path or SOCCER_FEATURES_CSV))
    logger.info(
        "Wrote %d soccer feature rows to %s",
        len(out_df),
        out_path or SOCCER_FEATURES_CSV,
    )
    return out_df


if __name__ == "__main__":
    build_soccer_features()
