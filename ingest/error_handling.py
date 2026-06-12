from __future__ import annotations
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger("multisport_ingest")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)


def build_retry_session(
    total_retries: int = 5,
    backoff_factor: float = 0.75,
    status_forcelist=(429, 500, 502, 503, 504),
) -> requests.Session:
    """Build a requests.Session with automatic retry/backoff.""" # Docstring is kept as it was in the original file.
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        connect=total_retries,
        read=total_retries,
        status=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=frozenset(["HEAD", "GET", "OPTIONS"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def retry_on_exception(max_retries: int = 3, backoff_seconds: float = 1.0):
    """Decorator: retry a function on any exception with exponential backoff."""
    def decorator(fn: Callable):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(1, max_retries + 1):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    logger.warning(f"{fn.__name__} failed on attempt {attempt}/{max_retries}: {e}")
                    if attempt < max_retries:
                        time.sleep(backoff_seconds * (2 ** (attempt - 1)))
            raise last_err
        return wrapper
    return decorator


def safe_read_csv(path: str, **kwargs) -> pd.DataFrame:
    """Read CSV with graceful fallback to empty DataFrame on error."""
    try:
        return pd.read_csv(path, **kwargs)
    except pd.errors.EmptyDataError:
        logger.warning(f"CSV empty: {path}")
        return pd.DataFrame()
    except pd.errors.ParserError as e:
        logger.error(f"CSV parse error for {path}: {e}")
        return pd.DataFrame()
    except FileNotFoundError:
        logger.warning(f"CSV not found: {path}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Unexpected CSV read error for {path}: {e}")
        return pd.DataFrame()


def safe_to_csv(df: pd.DataFrame, path: str) -> bool:
    """Write DataFrame to CSV; return True on success."""
    try:
        df.to_csv(path, index=False)
        return True
    except Exception as e:
        logger.error(f"Failed writing CSV {path}: {e}")
        return False


def safe_json(obj: Any, default: Optional[dict] = None) -> dict:
    """Safely coerce an object to dict."""
    try:
        if isinstance(obj, dict):
            return obj
        return default or {}
    except Exception:
        return default or {}
