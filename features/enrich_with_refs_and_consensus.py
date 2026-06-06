#!/usr/bin/env python
"""
Module to merge external features into the main match DataFrame.

This module houses functions to merge loaded external data into the main
match-level DataFrame used by the prediction model. It creates new features
based on the external data.
"""

import pandas as pd
from typing import Dict
from models.referee_features import RefereeStats, SoccerRefStats, ConsensusSignal


def attach_basketball_ref_features(
    matches_df: pd.DataFrame,
    ref_map: Dict[str, RefereeStats]
) -> pd.DataFrame:
    """
    Attach basketball referee features to the matches DataFrame.
    
    Args:
        matches_df: DataFrame containing match information with 'ref_id' column.
        ref_map: Dictionary mapping ref_id to RefereeStats objects.
        
    Returns:
        DataFrame with additional referee feature columns.
    """
    def _map_ref(row):
        ref = ref_map.get(row.get("ref_id"))
        if not ref:
            return pd.Series({
                "ref_avg_total_fouls": None,
                "ref_home_foul_diff": None,
                "ref_tech_fouls_per_game": None,
                "ref_over_rate_totals": None,
                "ref_playoff_flag": None,
            })
        return pd.Series({
            "ref_avg_total_fouls": ref.avg_total_fouls,
            "ref_home_foul_diff": ref.home_foul_diff,
            "ref_tech_fouls_per_game": ref.tech_fouls_per_game,
            "ref_over_rate_totals": ref.over_rate_totals,
            "ref_playoff_flag": ref.playoff_flag,
        })

    ref_features = matches_df.apply(_map_ref, axis=1)
    return pd.concat([matches_df, ref_features], axis=1)


def attach_soccer_ref_features(
    matches_df: pd.DataFrame,
    ref_map: Dict[str, SoccerRefStats]
) -> pd.DataFrame:
    """
    Attach soccer referee features to the matches DataFrame.
    
    Args:
        matches_df: DataFrame containing match information with 'ref_id' column.
        ref_map: Dictionary mapping ref_id to SoccerRefStats objects.
        
    Returns:
        DataFrame with additional referee feature columns.
    """
    def _map_ref(row):
        ref = ref_map.get(row.get("ref_id"))
        if not ref:
            return pd.Series({
                "ref_yellows_per_game": None,
                "ref_reds_per_game": None,
                "ref_pens_per_game": None,
                "ref_home_card_diff": None,
            })
        return pd.Series({
            "ref_yellows_per_game": ref.yellows_per_game,
            "ref_reds_per_game": ref.reds_per_game,
            "ref_pens_per_game": ref.pens_per_game,
            "ref_home_card_diff": ref.home_card_diff,
        })

    ref_features = matches_df.apply(_map_ref, axis=1)
    return pd.concat([matches_df, ref_features], axis=1)


def attach_consensus_features(
    matches_df: pd.DataFrame,
    cons_map: Dict[str, ConsensusSignal]
) -> pd.DataFrame:
    """
    Attach sharp bettor consensus features to the matches DataFrame.
    
    Args:
        matches_df: DataFrame containing match information with 'match_id' column.
        cons_map: Dictionary mapping match_id to ConsensusSignal objects.
        
    Returns:
        DataFrame with additional consensus feature columns.
    """
    def _map_cons(row):
        cons = cons_map.get(row.get("match_id"))
        if not cons:
            return pd.Series({
                "public_pct_home": None,
                "public_pct_over": None,
                "sharp_side_home": 0,
                "sharp_side_away": 0,
                "sharp_side_over": 0,
                "sharp_side_under": 0,
                "expert_consensus_score": None,
            })
        sharp_side_flags = {
            "sharp_side_home": 1 if cons.sharp_side == "home" else 0,
            "sharp_side_away": 1 if cons.sharp_side == "away" else 0,
            "sharp_side_over": 1 if cons.sharp_side == "over" else 0,
            "sharp_side_under": 1 if cons.sharp_side == "under" else 0,
        }
        return pd.Series({
            "public_pct_home": cons.public_pct_home,
            "public_pct_over": cons.public_pct_over,
            "expert_consensus_score": cons.expert_consensus_score,
            **sharp_side_flags,
        })

    cons_features = matches_df.apply(_map_cons, axis=1)
    return pd.concat([matches_df, cons_features], axis=1)


def enrich_basketball_matches(
    matches_df: pd.DataFrame,
    ref_map: Dict[str, RefereeStats],
    cons_map: Dict[str, ConsensusSignal]
) -> pd.DataFrame:
    """
    Enrich basketball matches with all external features.
    
    Args:
        matches_df: DataFrame containing basketball match information.
        ref_map: Dictionary mapping ref_id to RefereeStats objects.
        cons_map: Dictionary mapping match_id to ConsensusSignal objects.
        
    Returns:
        DataFrame with all external features attached.
    """
    df = matches_df.copy()
    df = attach_basketball_ref_features(df, ref_map)
    df = attach_consensus_features(df, cons_map)
    return df


def enrich_soccer_matches(
    matches_df: pd.DataFrame,
    ref_map: Dict[str, SoccerRefStats],
    cons_map: Dict[str, ConsensusSignal]
) -> pd.DataFrame:
    """
    Enrich soccer matches with all external features.
    
    Args:
        matches_df: DataFrame containing soccer match information.
        ref_map: Dictionary mapping ref_id to SoccerRefStats objects.
        cons_map: Dictionary mapping match_id to ConsensusSignal objects.
        
    Returns:
        DataFrame with all external features attached.
    """
    df = matches_df.copy()
    df = attach_soccer_ref_features(df, ref_map)
    df = attach_consensus_features(df, cons_map)
    return df