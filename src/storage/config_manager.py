"""Configuration management for DriverReminder."""

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
}


class ConfigManager:
    """Read and write persistent app configuration."""

    def __init__(self, config_path: str | Path = "config.json") -> None:
        self.config_path = Path(config_path)
        self.config = self._load_or_create_config()

    def _load_or_create_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            config = deepcopy(DEFAULT_CONFIG)
            self._write(config)
            return config

        try:
            with self.config_path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)
        except (OSError, json.JSONDecodeError):
            loaded = deepcopy(DEFAULT_CONFIG)

        merged = self._merge_with_defaults(loaded)
        self._write(merged)
        return merged

    def _merge_with_defaults(self, loaded: dict[str, Any]) -> dict[str, Any]:
        merged = deepcopy(DEFAULT_CONFIG)
        merged["reminder_interval"] = loaded.get("reminder_interval", "Weekly")

        loaded_last_checked = loaded.get("last_checked", {})
        if isinstance(loaded_last_checked, dict):
            for category in DRIVER_CATEGORIES:
                merged["last_checked"][category] = loaded_last_checked.get(category)

        return merged

    def _write(self, data: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)

    def save(self) -> None:
        self._write(self.config)

    def set_interval(self, interval: str) -> None:
        if interval not in {"Daily", "Weekly", "Monthly"}:
            raise ValueError("Interval must be Daily, Weekly, or Monthly")
        self.config["reminder_interval"] = interval
        self.save()

    def mark_checked(self, category: str, when: datetime | None = None) -> None:
        if category not in self.config["last_checked"]:
            return
        timestamp = (when or datetime.now(timezone.utc)).isoformat()
        self.config["last_checked"][category] = timestamp
        self.save()

    def mark_all_checked(self) -> None:
        now = datetime.now(timezone.utc)
        for category in self.config["last_checked"]:
            self.config["last_checked"][category] = now.isoformat()
        self.save()
