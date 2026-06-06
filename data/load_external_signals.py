#!/usr/bin/env python
"""
Module to load external data from CSV/JSON files.

This module contains functions responsible for loading external data from the
external_data/ directory into Python objects (e.g., Pandas DataFrames or lists
of custom dataclasses). It handles reading CSV or JSON files.
"""

import pandas as pd
from typing import Dict
from models.referee_features import RefereeStats, SoccerRefStats, ConsensusSignal


def load_basketball_ref_data(path: str) -> Dict[str, RefereeStats]:
    """
    Load basketball referee data from a CSV file.
    
    Args:
        path: Path to the basketball referee CSV file.
        
    Returns:
        Dictionary mapping ref_id to RefereeStats objects.
    """
    df = pd.read_csv(path)
    ref_map = {}
    for _, row in df.iterrows():
        ref = RefereeStats(
            ref_id=row["ref_id"],
            league=row["league"],
            season=row["season"],
            games=row["games"],
            avg_total_fouls=row["avg_total_fouls"],
            home_foul_diff=row["home_foul_diff"],
            tech_fouls_per_game=row["tech_fouls_per_game"],
            over_rate_totals=row["over_rate_totals"],
            playoff_flag=bool(row.get("playoff_flag", False))
        )
        ref_map[ref.ref_id] = ref
    return ref_map


def load_soccer_ref_data(path: str) -> Dict[str, SoccerRefStats]:
    """
    Load soccer referee data from a CSV file.
    
    Args:
        path: Path to the soccer referee CSV file.
        
    Returns:
        Dictionary mapping ref_id to SoccerRefStats objects.
    """
    df = pd.read_csv(path)
    ref_map = {}
    for _, row in df.iterrows():
        ref = SoccerRefStats(
            ref_id=row["ref_id"],
            league=row["league"],
            season=row["season"],
            games=row["games"],
            yellows_per_game=row["yellows_per_game"],
            reds_per_game=row["reds_per_game"],
            pens_per_game=row["pens_per_game"],
            home_card_diff=row["home_card_diff"],
        )
        ref_map[ref.ref_id] = ref
    return ref_map


def load_consensus_data(path: str) -> Dict[str, ConsensusSignal]:
    """
    Load sharp bettor consensus data from a CSV file.
    
    Args:
        path: Path to the consensus signals CSV file.
        
    Returns:
        Dictionary mapping match_id to ConsensusSignal objects.
    """
    df = pd.read_csv(path)
    cons_map = {}
    for _, row in df.iterrows():
        match_id = row["match_id"]
        cons_map[match_id] = ConsensusSignal(
            match_id=match_id,
            sport=row["sport"],
            home_team=row["home_team"],
            away_team=row["away_team"],
            public_pct_home=row["public_pct_home"],
            public_pct_over=row["public_pct_over"],
            sharp_side=row.get("sharp_side"),
            expert_consensus_score=row["expert_consensus_score"],
        )
    return cons_map


def load_basketball_ref_data_from_json(path: str) -> Dict[str, RefereeStats]:
    """
    Load basketball referee data from a JSON file.
    
    Args:
        path: Path to the basketball referee JSON file.
        
    Returns:
        Dictionary mapping ref_id to RefereeStats objects.
    """
    df = pd.read_json(path)
    return load_basketball_ref_data_from_dataframe(df)


def load_soccer_ref_data_from_json(path: str) -> Dict[str, SoccerRefStats]:
    """
    Load soccer referee data from a JSON file.
    
    Args:
        path: Path to the soccer referee JSON file.
        
    Returns:
        Dictionary mapping ref_id to SoccerRefStats objects.
    """
    df = pd.read_json(path)
    return load_soccer_ref_data_from_dataframe(df)


def load_consensus_data_from_json(path: str) -> Dict[str, ConsensusSignal]:
    """
    Load consensus data from a JSON file.
    
    Args:
        path: Path to the consensus signals JSON file.
        
    Returns:
        Dictionary mapping match_id to ConsensusSignal objects.
    """
    df = pd.read_json(path)
    return load_consensus_data_from_dataframe(df)


def load_basketball_ref_data_from_dataframe(df: pd.DataFrame) -> Dict[str, RefereeStats]:
    """
    Load basketball referee data from a DataFrame.
    
    Args:
        df: Pandas DataFrame with referee data.
        
    Returns:
        Dictionary mapping ref_id to RefereeStats objects.
    """
    ref_map = {}
    for _, row in df.iterrows():
        ref = RefereeStats(
            ref_id=row["ref_id"],
            league=row["league"],
            season=row["season"],
            games=row["games"],
            avg_total_fouls=row["avg_total_fouls"],
            home_foul_diff=row["home_foul_diff"],
            tech_fouls_per_game=row["tech_fouls_per_game"],
            over_rate_totals=row["over_rate_totals"],
            playoff_flag=bool(row.get("playoff_flag", False))
        )
        ref_map[ref.ref_id] = ref
    return ref_map


def load_soccer_ref_data_from_dataframe(df: pd.DataFrame) -> Dict[str, SoccerRefStats]:
    """
    Load soccer referee data from a DataFrame.
    
    Args:
        df: Pandas DataFrame with referee data.
        
    Returns:
        Dictionary mapping ref_id to SoccerRefStats objects.
    """
    ref_map = {}
    for _, row in df.iterrows():
        ref = SoccerRefStats(
            ref_id=row["ref_id"],
            league=row["league"],
            season=row["season"],
            games=row["games"],
            yellows_per_game=row["yellows_per_game"],
            reds_per_game=row["reds_per_game"],
            pens_per_game=row["pens_per_game"],
            home_card_diff=row["home_card_diff"],
        )
        ref_map[ref.ref_id] = ref
    return ref_map


def load_consensus_data_from_dataframe(df: pd.DataFrame) -> Dict[str, ConsensusSignal]:
    """
    Load consensus data from a DataFrame.
    
    Args:
        df: Pandas DataFrame with consensus data.
        
    Returns:
        Dictionary mapping match_id to ConsensusSignal objects.
    """
    cons_map = {}
    for _, row in df.iterrows():
        match_id = row["match_id"]
        cons_map[match_id] = ConsensusSignal(
            match_id=match_id,
            sport=row["sport"],
            home_team=row["home_team"],
            away_team=row["away_team"],
            public_pct_home=row["public_pct_home"],
            public_pct_over=row["public_pct_over"],
            sharp_side=row.get("sharp_side"),
            expert_consensus_score=row["expert_consensus_score"],
        )
    return cons_map