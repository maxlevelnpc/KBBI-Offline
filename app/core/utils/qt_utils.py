import logging

from PySide6.QtCore import QFile, QTextStream

log = logging.getLogger(__name__)


def load_qss(*resource_paths: str) -> str:
    stylesheet = ""

    try:
        for path in resource_paths:
            file = QFile(path)
            if file.exists() and file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
                stream = QTextStream(file)
                stylesheet += stream.readAll() + "\n"
                file.close()
    except Exception as e:
        log.error(f"Failed to load QSS: {e}")

    return stylesheet
