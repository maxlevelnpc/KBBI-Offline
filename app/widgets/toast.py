from PySide6.QtCore import QPropertyAnimation, QTimer, QEasingCurve
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect


class ToastLabel(QLabel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.setObjectName("toast")

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity", self)
        self.fade_animation.finished.connect(self.hide)

        self.hide()

    def showMessage(self, msg: str, dur: int = 3000, fade_dur: int = 500) -> None:
        self.fade_animation.stop()

        self.setText(msg)
        self.adjustSize()

        parent = self.parentWidget()
        x = (parent.width() - self.width()) // 2
        y = parent.height() - self.height() - 20
        self.move(x, y)

        self.opacity_effect.setOpacity(1.0)

        self.show()
        self.raise_()

        QTimer.singleShot(dur, lambda: self._fade_out(fade_dur))

    def _fade_out(self, dur: int) -> None:
        self.fade_animation.setDuration(dur)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.fade_animation.start()
