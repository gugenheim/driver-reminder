from src.utils.version_compare import compare_versions


def test_compare_update_available() -> None:
    assert compare_versions("1.0.0", "1.1.0") == "Update likely available"


def test_compare_up_to_date() -> None:
    assert compare_versions("2.0.0", "2.0.0") == "Up to date"


def test_compare_handles_missing_values() -> None:
    assert compare_versions("Installed version unavailable", "2.0.0") == "Installed version unavailable"
    assert compare_versions("1.0.0", "Latest version lookup unavailable") == "Latest version lookup unavailable"
