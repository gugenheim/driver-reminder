"""Entrypoint for DriverReminder."""

from ui.app import DriverReminderApp


def main() -> None:
    """Run the desktop application."""
    app = DriverReminderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
