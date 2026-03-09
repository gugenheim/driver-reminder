"""Background reminder scheduler with anti-spam behavior."""

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
    """Checks overdue categories in the background and emits notifications."""

    def __init__(self, config_getter: Callable[[], dict], on_notified: Callable[[str], None]) -> None:
        self._config_getter = config_getter
        self._on_notified = on_notified
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._scheduler = schedule.Scheduler()

    def start(self) -> None:
        self._stop_event.clear()
        self._scheduler.clear()
        self._scheduler.every(15).minutes.do(self.check_overdue)
        if self._thread is None or not self._thread.is_alive():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._scheduler.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            time.sleep(1)

    def check_overdue(self) -> None:
        config = self._config_getter()
        if config.get("reminders_paused", False):
            return

        interval_days = INTERVAL_DAYS.get(config.get("reminder_interval", "Weekly"), 7)
        now = datetime.now(timezone.utc)

        for category in DRIVER_CATEGORIES:
            last_checked = self._parse_dt(config.get("last_checked", {}).get(category))
            last_notified = self._parse_dt(config.get("last_notified", {}).get(category))

            is_overdue = last_checked is None or (now - last_checked >= timedelta(days=interval_days))
            can_notify = last_notified is None or (now - last_notified >= timedelta(days=1))

            if is_overdue and can_notify:
                elapsed = interval_days if last_checked is None else max(1, (now - last_checked).days)
                send_notification(
                    "DriverReminder",
                    f"It's been {elapsed} days since you checked {category}.",
                )
                self._on_notified(category)

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
