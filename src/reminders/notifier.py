"""Desktop notification utilities."""

from __future__ import annotations

from plyer import notification


def send_notification(title: str, message: str) -> None:
    """Send a native desktop notification."""
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="DriverReminder",
            timeout=10,
        )
    except Exception:
        # Notification failures should not crash the scheduler/UI.
        pass
