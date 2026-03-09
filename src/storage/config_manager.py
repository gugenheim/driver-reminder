"""Persistent configuration handling for DriverReminder."""

from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DRIVER_CATEGORIES = [
    "BIOS / UEFI firmware",
    "Graphics drivers",
    "CPU chipset drivers",
    "WiFi drivers",
    "Bluetooth drivers",
    "Audio drivers",
    "Storage / NVMe drivers",
    "System firmware / motherboard drivers",
]

DEFAULT_CONFIG: dict[str, Any] = {
    "reminder_interval": "Weekly",
    "last_checked": {category: None for category in DRIVER_CATEGORIES},
    "last_notified": {category: None for category in DRIVER_CATEGORIES},
    "start_with_windows": False,
    "minimize_to_tray": True,
    "reminders_paused": False,
    "scan_cache": {},
}


class ConfigManager:
    """Load, validate, and persist app configuration in JSON."""

    def __init__(self, config_path: str | Path = "config.json") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_or_create_config()

    def _load_or_create_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            config = deepcopy(DEFAULT_CONFIG)
            self._write(config)
            return config

        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            loaded = {}

        merged = self._merge_with_defaults(loaded if isinstance(loaded, dict) else {})
        self._write(merged)
        return merged

    def _merge_with_defaults(self, loaded: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(DEFAULT_CONFIG)
        merged["reminder_interval"] = loaded.get("reminder_interval", "Weekly")
        merged["start_with_windows"] = bool(loaded.get("start_with_windows", False))
        merged["minimize_to_tray"] = bool(loaded.get("minimize_to_tray", True))
        merged["reminders_paused"] = bool(loaded.get("reminders_paused", False))
        merged["scan_cache"] = loaded.get("scan_cache", {}) if isinstance(loaded.get("scan_cache"), dict) else {}

        for key in ("last_checked", "last_notified"):
            source = loaded.get(key, {})
            if isinstance(source, dict):
                for category in DRIVER_CATEGORIES:
                    merged[key][category] = source.get(category)

        if merged["reminder_interval"] not in {"Daily", "Weekly", "Monthly"}:
            merged["reminder_interval"] = "Weekly"

        return merged

    def _write(self, data: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def save(self) -> None:
        self._write(self.config)

    def set_interval(self, interval: str) -> None:
        if interval not in {"Daily", "Weekly", "Monthly"}:
            raise ValueError("Interval must be Daily, Weekly, or Monthly")
        self.config["reminder_interval"] = interval
        self.save()

    def set_startup(self, enabled: bool) -> None:
        self.config["start_with_windows"] = bool(enabled)
        self.save()

    def set_paused(self, paused: bool) -> None:
        self.config["reminders_paused"] = bool(paused)
        self.save()

    def set_minimize_to_tray(self, enabled: bool) -> None:
        self.config["minimize_to_tray"] = bool(enabled)
        self.save()

    def set_scan_cache(self, cache: dict[str, Any]) -> None:
        self.config["scan_cache"] = cache
        self.save()

    def mark_checked(self, category: str, when: datetime | None = None) -> None:
        if category not in self.config["last_checked"]:
            return
        self.config["last_checked"][category] = (when or datetime.now(timezone.utc)).isoformat()
        self.save()

    def mark_all_checked(self) -> None:
        now = datetime.now(timezone.utc).isoformat()
        for category in DRIVER_CATEGORIES:
            self.config["last_checked"][category] = now
        self.save()

    def mark_notified(self, category: str, when: datetime | None = None) -> None:
        if category not in self.config["last_notified"]:
            return
        self.config["last_notified"][category] = (when or datetime.now(timezone.utc)).isoformat()
        self.save()
