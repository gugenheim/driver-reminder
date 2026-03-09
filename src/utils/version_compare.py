"""Safe semantic-ish version comparisons."""

from __future__ import annotations

from packaging.version import InvalidVersion, Version


def compare_versions(installed: str, latest: str) -> str:
    """Return update status for installed/latest versions.

    Returns one of:
    - "Update likely available"
    - "Up to date"
    - "Installed version unavailable"
    - "Latest version lookup unavailable"
    """
    if not installed or installed == "Installed version unavailable":
        return "Installed version unavailable"
    if not latest or latest == "Latest version lookup unavailable":
        return "Latest version lookup unavailable"

    try:
        a = Version(installed)
        b = Version(latest)
    except InvalidVersion:
        return "Latest version lookup unavailable"

    return "Update likely available" if a < b else "Up to date"
