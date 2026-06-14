from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    bookmarkSearchRequested = Signal(str)
    bookmarkChanged = Signal(list, str)
