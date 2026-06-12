"""
Odds API Client for MultiSportPredict
======================================
Client for fetching odds, fixtures, and sports data from the configured
odds provider. Imports API keys and base URLs from config.py.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import requests
from requests import Response

from config import (
    ODDS_API_KEY_ENV_VAR,
    ODDS_API_BASE_URL_ENV_VAR,
    ODDS_API_DEFAULT_BASE_URL,
    HTTP_TIMEOUT_SECONDS,
)
from ingest.error_handling import build_retry_session, logger


class OddsClient:
    """HTTP client for the odds provider API with retry/backoff."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv(ODDS_API_KEY_ENV_VAR, "")
        self.base_url = (
            base_url
            or os.getenv(ODDS_API_BASE_URL_ENV_VAR, ODDS_API_DEFAULT_BASE_URL)
        ).rstrip("/")
        self.session = build_retry_session()
        self.headers = {"User-Agent": "Mozilla/5.0"}

    # ── internal helpers ──────────────────────────────────────────────

    def _get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Perform a GET request with error handling."""
        params = params or {}
        params["api_key"] = self.api_key
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            r = self.session.get(url, params=params, headers=self.headers, timeout=(10, 30))
            r.raise_for_status()
            return r.json()
        except requests.Timeout:
            logger.error(f"Timeout fetching {url}")
            return {}
        except requests.HTTPError as e:
            logger.error(f"HTTP error fetching {url}: {e}")
            return {}
        except ValueError:
            logger.error(f"Invalid JSON response from {url}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return {}

    # ── public endpoints ──────────────────────────────────────────────

    def sports(self) -> List[Dict[str, Any]]:
        """List available sports/leagues."""
        data = self._get("sports")
        return data.get("data", data) if isinstance(data, dict) else data

    def fixtures(
        self,
        sport: str,
        league: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch fixtures for a given sport."""
        params: dict = {"sport": sport}
        if league:
            params["league"] = league
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        data = self._get("fixtures", params=params)
        return data.get("data", data) if isinstance(data, dict) else data

    def odds(self, fixture_id: str) -> dict:
        data = self._get("odds", params={"fixture_id": fixture_id})
        return data.get("data", data) if isinstance(data, dict) else data
