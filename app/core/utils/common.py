import logging

log = logging.getLogger(__name__)


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(levelname)s] %(asctime)s | %(name)s | Ln. %(lineno)d %(funcName)s --> %(message)s"
    )

    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setLevel(logging.WARN)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    root.addHandler(file_handler)
    root.addHandler(console_handler)
