#!/usr/bin/env python
"""
Data models for referee and consensus data.

This module defines Python dataclass objects to represent structured external data.
This provides clear data schemas and improves code readability and maintainability.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RefereeStats:
    """Basketball referee statistics data model."""
    ref_id: str
    league: str
    season: str
    games: int
    avg_total_fouls: float
    home_foul_diff: float
    tech_fouls_per_game: float
    over_rate_totals: float
    playoff_flag: bool = False


@dataclass
class SoccerRefStats:
    """Soccer referee statistics data model."""
    ref_id: str
    league: str
    season: str
    games: int
    yellows_per_game: float
    reds_per_game: float
    pens_per_game: float
    home_card_diff: float


@dataclass
class ConsensusSignal:
    """Sharp bettor/handicapper consensus data model."""
    match_id: str
    sport: str
    home_team: str
    away_team: str
    public_pct_home: float
    public_pct_over: float
    sharp_side: Optional[str]  # 'home', 'away', 'over', 'under', or None
    expert_consensus_score: float  # e.g. 0–1 scaled