import sys
import logging
import os

from PySide6.QtWidgets import QApplication

from app.models import MainModel
from app.views import MainView
from app.presenters import MainPresenter
from app.core.services import DatabaseService, ConfigService
from app.core.utils.qt_utils import load_qss
from app.core.bus import EventBus

from app.assets import icons  # type: ignore[unusedImport]

log = logging.getLogger(__name__)

DB_PATH = os.path.join("data", "kbbi.db")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("MaxLevelNPC")
    app.setApplicationName("KBBI-Offline")

    stylesheet = load_qss(
        ":/app/assets/styles/base.css",
        ":/app/assets/styles/custom.css",
    )
    app.setStyleSheet(stylesheet)

    bus = EventBus()
    cfg_svc = ConfigService()
    db_svc = DatabaseService(DB_PATH)
    model = MainModel(cfg_svc, db_svc)
    view = MainView(bus)
    presenter = MainPresenter(view, model, bus)
    view.show()

    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
