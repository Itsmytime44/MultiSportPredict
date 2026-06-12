"""
KBO Feature Builder
===================
Transforms raw KBO match CSV data into the feature matrix expected
by models.kbo_model.KBOModel.  Output CSV contains
KBO_FEATURE_COLS + id columns + target column.
"""

from __future__ import annotations

import pandas as pd

from config import (
    KBO_FEATURE_COLS,
    KBO_RAW_CSV,
    KBO_FEATURES_CSV,
    KBO_TARGET_COL,
)
from ingest.error_handling import safe_read_csv, safe_to_csv, logger


def build_kbo_features(
    raw_path: str | None = None,
    out_path: str | None = None,
) -> pd.DataFrame:
    """
    Read raw KBO matches, engineer feature columns, write to disk.

    Expected raw CSV columns (at minimum):
        home_team, away_team,
        home_woba, away_woba, home_wrc_plus, away_wrc_plus,
        home_fip, away_fip, home_whip, away_whip,
        home_bullpen_fip, away_bullpen_fip,
        sharp_score, reverse_line_movement, money_ticket_gap,
        public_tickets_pct, public_money_pct, total_runs
    """
    raw = safe_read_csv(str(raw_path or KBO_RAW_CSV))
    if raw.empty:
        logger.warning("No KBO raw data to build features from.")
        return raw

    df = raw.copy()

    # Ensure all FEATURE_COLS exist (fill missing with 0)
    for col in KBO_FEATURE_COLS:
        if col not in df.columns:
            df[col] = 0.0

    id_cols = ["home_team", "away_team"]
    keep_cols = id_cols + KBO_FEATURE_COLS
    if KBO_TARGET_COL in df.columns:
        keep_cols = keep_cols + [KBO_TARGET_COL]

    out_df = df[keep_cols].copy()

    safe_to_csv(out_df, str(out_path or KBO_FEATURES_CSV))
    logger.info(
        "Wrote %d KBO feature rows to %s",
        len(out_df),
        out_path or KBO_FEATURES_CSV,
    )
    return out_df


if __name__ == "__main__":
    build_kbo_features()
