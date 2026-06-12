from __future__ import annotations
import pandas as pd
from ingest.odds_client import OddsClient
from ingest.error_handling import logger


class SharpConsensusIngestor:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.client = OddsClient(api_key=api_key, base_url=base_url)

    # ── helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _normalize_fixture(fx: dict) -> dict:
        return {
            "match_id": str(fx.get("fixtureId") or fx.get("fixture_id") or fx.get("id") or ""),
            "home_team": fx.get("homeTeamName") or fx.get("home_team") or fx.get("home") or "",
            "away_team": fx.get("awayTeamName") or fx.get("away_team") or fx.get("away") or "",
            "league": fx.get("leagueName") or fx.get("league") or "",
            "sport": fx.get("sport") or "",
        }

    @staticmethod
    def _safe_float(value, default: float = 0.0) -> float:
        try:
            v = float(value)
            return default if pd.isna(v) else v
        except Exception:
            return default

    @staticmethod
    def _extract_prices(odds_json: dict) -> dict:
        data = odds_json.get("data", odds_json)
        if isinstance(data, list) and data:
            data = data[0]
        return {
            "open_price": SharpConsensusIngestor._safe_float(data.get("openPrice") or data.get("open_line") or 0),
            "current_price": SharpConsensusIngestor._safe_float(data.get("currentPrice") or data.get("current_line") or 0),
            "public_tickets_pct": SharpConsensusIngestor._safe_float(data.get("publicTicketsPct") or 50),
            "public_money_pct": SharpConsensusIngestor._safe_float(data.get("publicMoneyPct") or 50),
        }

    # ── public API ────────────────────────────────────────────────────

    def pull_daily(
        self,
        sport: str,
        league: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        market: str = "moneyline",
    ) -> pd.DataFrame:
        try:
            fixtures_json = self.client.fixtures(sport=sport, league=league, from_date=from_date, to_date=to_date)
            fixtures = fixtures_json.get("data", fixtures_json)
        except Exception as e:
            logger.error(f"Failed to pull fixtures: {e}")
            return pd.DataFrame()

        rows = []
        for fx in fixtures if isinstance(fixtures, list) else []:
            try:
                m = self._normalize_fixture(fx)
                if not m["match_id"]:
                    continue
                odds_json = self.client.odds(m["match_id"])
                if not odds_json:
                    continue
                prices = self._extract_prices(odds_json)
                rows.append({**m, **prices, "market": market})
            except Exception as e:
                logger.warning(f"Skipping fixture due to error: {e}")
                continue

        return pd.DataFrame(rows)
