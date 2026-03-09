"""Latest-version lookup against safer, official-ish endpoints where practical."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import requests


class VersionDetector:
    """Lookup latest versions where reliable endpoints exist.

    For unavailable/unreliable categories, returns
    "Latest version lookup unavailable".
    """

    NVIDIA_URL = "https://gfwsl.geforce.com/services_toolkit/services/com/nvidia/services/AjaxDriverService.php?func=DriverManualLookup"

    def __init__(self, timeout_s: int = 5, cache_ttl_hours: int = 6) -> None:
        self.timeout_s = timeout_s
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._cache: dict[tuple[str, tuple[str, ...]], tuple[str, datetime]] = {}

    def lookup_latest(self, category: str, vendors: list[str]) -> str:
        key = (category, tuple(sorted(set(vendors))))
        now = datetime.now(timezone.utc)

        cached = self._cache.get(key)
        if cached and now - cached[1] < self.cache_ttl:
            return cached[0]

        result = "Latest version lookup unavailable"
        if category == "Graphics drivers":
            vset = set(vendors)
            if "NVIDIA" in vset:
                result = self._nvidia_latest()

        self._cache[key] = (result, now)
        return result

    def _nvidia_latest(self) -> str:
        payload: dict[str, Any] = {
            "psid": 101,
            "pfid": 995,
            "osID": 57,
            "languageCode": 1033,
            "beta": 0,
            "isWHQL": 1,
            "dltype": -1,
            "dch": 1,
            "sort1": 0,
            "numberOfResults": 1,
        }
        try:
            response = requests.get(self.NVIDIA_URL, params=payload, timeout=self.timeout_s)
            response.raise_for_status()
            data = response.json()
            ids = data.get("IDS") or []
            if ids and isinstance(ids, list):
                version = str(ids[0].get("downloadInfo", {}).get("Version", "")).strip()
                if version:
                    return version
        except Exception:
            return "Latest version lookup unavailable"
        return "Latest version lookup unavailable"
