"""Windows startup registration via HKCU Run key."""

from __future__ import annotations

import os
import sys

try:
    import winreg
except ImportError:  # pragma: no cover
    winreg = None

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "DriverReminder"


def _startup_command() -> str:
    script = os.path.abspath(sys.argv[0])
    python_exe = sys.executable
    return f'"{python_exe}" "{script}"'


def is_startup_enabled() -> bool:
    if winreg is None:
        return False
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
        return bool(value)
    except OSError:
        return False


def set_startup_enabled(enabled: bool) -> bool:
    """Enable/disable startup for current user. Returns False on failure."""
    if winreg is None:
        return False
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            if enabled:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _startup_command())
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except OSError:
                    pass
        return True
    except OSError:
        return False
