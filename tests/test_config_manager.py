from pathlib import Path

from src.storage.config_manager import ConfigManager, DRIVER_CATEGORIES


def test_config_manager_initializes_defaults(tmp_path: Path) -> None:
    manager = ConfigManager(tmp_path / "config.json")
    assert manager.config["reminder_interval"] == "Weekly"
    assert manager.config["start_with_windows"] is False
    assert manager.config["minimize_to_tray"] is True
    assert set(manager.config["last_checked"].keys()) == set(DRIVER_CATEGORIES)
    assert set(manager.config["last_notified"].keys()) == set(DRIVER_CATEGORIES)


def test_config_manager_migrates_corrupt_json(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    path.write_text("{bad-json", encoding="utf-8")
    manager = ConfigManager(path)
    assert manager.config["reminder_interval"] == "Weekly"


def test_mark_checked_and_notified(tmp_path: Path) -> None:
    manager = ConfigManager(tmp_path / "config.json")
    manager.mark_checked("Graphics drivers")
    manager.mark_notified("Graphics drivers")
    assert manager.config["last_checked"]["Graphics drivers"] is not None
    assert manager.config["last_notified"]["Graphics drivers"] is not None
