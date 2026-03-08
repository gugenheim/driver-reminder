"""Background reminder scheduler."""

from __future__ import annotations

import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Callable

import schedule

from reminders.notifier import send_notification
from storage.config_manager import DRIVER_CATEGORIES

INTERVAL_DAYS = {"Daily": 1, "Weekly": 7, "Monthly": 30}


class ReminderScheduler:
    """Runs periodic overdue checks and emits desktop notifications."""

    def __init__(self, config_getter: Callable[[], dict], daemon: bool = True) -> None:
        self._config_getter = config_getter
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=daemon)

    def start(self) -> None:
        schedule.clear("driver-reminder")
        schedule.every(4).hours.do(self.check_overdue).tag("driver-reminder")
        if not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        schedule.clear("driver-reminder")

    def _run(self) -> None:
        while not self._stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    def check_overdue(self) -> None:
        config = self._config_getter()
        interval_name = config.get("reminder_interval", "Weekly")
        threshold_days = INTERVAL_DAYS.get(interval_name, 7)
        now = datetime.now(timezone.utc)

        for category in DRIVER_CATEGORIES:
            last_checked = config.get("last_checked", {}).get(category)
            if not last_checked:
                self._notify_due(category, threshold_days)
                continue

            try:
                checked_time = datetime.fromisoformat(last_checked)
            except ValueError:
                self._notify_due(category, threshold_days)
                continue

            if now - checked_time >= timedelta(days=threshold_days):
                days_elapsed = (now - checked_time).days
                self._notify_due(category, days_elapsed)

    @staticmethod
    def _notify_due(category: str, elapsed_days: int) -> None:
        send_notification(
            title="DriverReminder",
            message=f"It's been {elapsed_days} days since you checked {category}.",
        )
