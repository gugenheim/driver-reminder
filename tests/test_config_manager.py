from pathlib import Path

from src.storage.config_manager import ConfigManager, DRIVER_CATEGORIES


def test_config_manager_initializes_defaults(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    manager = ConfigManager(config_file)

    assert manager.config["reminder_interval"] == "Weekly"
    assert set(manager.config["last_checked"].keys()) == set(DRIVER_CATEGORIES)


def test_mark_checked_updates_timestamp(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    manager = ConfigManager(config_file)

    manager.mark_checked("Graphics drivers")

    assert manager.config["last_checked"]["Graphics drivers"] is not None
