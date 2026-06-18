import logging
import json
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from app.core.types import ConfigData

log = logging.getLogger(__name__)


class ConfigService:
    def __init__(self) -> None:
        config_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation))
        config_dir.mkdir(parents=True, exist_ok=True)

        self.cfg_path = config_dir / "settings.json"

    def load_config_data(self) -> ConfigData | None:
        if not self.cfg_path.exists():
            return None

        try:
            with self.cfg_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception as e:
            log.error(f"Failed to load settings: {e}")
            return None

    def save_config_data(self, config_data: dict) -> None:
        try:
            with self.cfg_path.open("w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            log.error(f"Failed to save settings: {e}")
