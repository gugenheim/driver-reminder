"""Entrypoint for DriverReminder."""

from ui.app import DriverReminderApp


if __name__ == "__main__":
    app = DriverReminderApp()
    app.mainloop()
