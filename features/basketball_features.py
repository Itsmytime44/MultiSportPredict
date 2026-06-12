"""
Basketball Feature Builder
==========================
Transforms raw basketball match CSV data into the feature matrix expected
by models.basketball_model.BasketballModel.  The output CSV contains
BASKETBALL_FEATURE_COLS + id columns + target column.

This module is the only place feature-engineering logic lives for hoops.
"""

from __future__ import annotations

import pandas as pd

from config import (
    BASKETBALL_FEATURE_COLS,
    BASKETBALL_RAW_CSV,
    BASKETBALL_FEATURES_CSV,
    BASKETBALL_TARGET_COL,
)
from ingest.error_handling import safe_read_csv, safe_to_csv, logger


def build_basketball_features(
    raw_path: str | None = None,
    out_path: str | None = None,
) -> pd.DataFrame:
    """
    Read raw basketball matches, engineer feature columns, write to disk.

    Expected raw CSV columns (at minimum):
        home_team, away_team, home_ortg, away_ortg, home_drtg, away_drtg,
        home_pace, away_pace, home_rest_days, away_rest_days,
        sharp_score, reverse_line_movement, money_ticket_gap,
        public_tickets_pct, public_money_pct, total_points

    Parameters
    ----------
    raw_path : str or None
        Path to the raw CSV. Defaults to BASKETBALL_RAW_CSV.
    out_path : str or None
        Where to write the feature CSV. Defaults to BASKETBALL_FEATURES_CSV.

    Returns
    -------
    pd.DataFrame
        The engineered feature DataFrame.
    """
    raw = safe_read_csv(str(raw_path or BASKETBALL_RAW_CSV))
    if raw.empty:
        logger.warning("No basketball raw data to build features from.")
        return raw

    df = raw.copy()

    # ── derived columns ────────────────────────────────────────────────
    # Rest differential (positive = home better-rested)
    if "home_rest_days" in df.columns and "away_rest_days" in df.columns:
        df["rest_diff"] = df["home_rest_days"] - df["away_rest_days"]
    else:
        df["rest_diff"] = 0

    # Ensure all FEATURE_COLS exist (fill missing with 0)
    for col in BASKETBALL_FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0.0

    # ── preserve identity columns ─────────────────────────────────────
    id_cols = ["home_team", "away_team"]
    keep_cols = id_cols + BASKETBALL_FEATURE_COLS
    if BASKETBALL_TARGET_COL in df.columns:
        keep_cols = keep_cols + [BASKETBALL_TARGET_COL]

    out_df = df[keep_cols].copy()

    safe_to_csv(out_df, str(out_path or BASKETBALL_FEATURES_CSV))
    logger.info(
        "Wrote %d basketball feature rows to %s",
        len(out_df),
        out_path or BASKETBALL_FEATURES_CSV,
    )
    return out_df


if __name__ == "__main__":
    build_basketball_features()
