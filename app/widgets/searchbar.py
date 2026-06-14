from PySide6.QtWidgets import QFrame, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtGui import QIcon, Qt
from PySide6.QtCore import Signal


class SearchBar(QFrame):
    searchRequested = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("searchbar")
 
        # //////////////////////////////////////////////////////////////////////////////////////////

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Ketik kata yang ingin dicari...")
        
        search_icon = QIcon(":/app/assets/icons/search.png")
        self.search_input.addAction(search_icon, QLineEdit.ActionPosition.LeadingPosition)

        self.search_btn = QPushButton("Cari")
        self.search_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.search_input)
        layout.addWidget(self.search_btn)

        self.search_btn.clicked.connect(self._on_search_triggered)
        self.search_input.returnPressed.connect(self._on_search_triggered)

    def _on_search_triggered(self) -> None:
        text = self.text()
        self.searchRequested.emit(text)

    def text(self) -> str:
        return self.search_input.text().strip()

    def setText(self, text: str) -> None:
        self.search_input.setText(text)

    def setSearchFocus(self) -> None:
        self.search_input.setFocus()
