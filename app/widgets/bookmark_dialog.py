from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QKeySequence, QShortcut, QIcon
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QVBoxLayout, QMenu, QHBoxLayout, QListWidgetItem

if TYPE_CHECKING:
    from app.core.bus import EventBus


class BookmarkDialog(QDialog):
    def __init__(self, parent, bus: EventBus) -> None:
        super().__init__(parent)
        self.bus = bus

        self.setWindowTitle("Bookmark")
        self.resize(350, 450)

        main_layout = QVBoxLayout(self)

        label_layout = QHBoxLayout()
        self.info_label = QLabel("• Klik dua kali kata untuk mencari.\n• Klik kanan untuk menampilkan opsi.")
        self.info_label.setStyleSheet("font-size: 12px;")
        self.bookmark_count = QLabel()
        self.bookmark_count.setStyleSheet("font-weight: bold;")
        label_layout.addWidget(self.info_label)
        label_layout.addStretch()
        label_layout.addWidget(self.bookmark_count)

        self.bookmark_list = QListWidget()
        self.bookmark_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        main_layout.addLayout(label_layout)
        main_layout.addWidget(self.bookmark_list)
        
        # ////////////////////////////////////////////////////////////////////////////////////

        self.bookmark_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.bookmark_list.customContextMenuRequested.connect(self.show_context_menu)

        self.HKEY_close_wd = QShortcut(QKeySequence("Ctrl+Shift+B"), self)
        self.HKEY_close_wd.activated.connect(self.accept)

    def add_bookmark(self, word: str) -> None:
        self.bookmark_list.addItem(QListWidgetItem(QIcon(":/app/assets/icons/hashtag.png"), word))

    def get_bookmarks(self) -> list[str]:
        """Returns list of item texts"""
        return [
            self.bookmark_list.item(i).text()
            for i in range(self.bookmark_list.count())
        ]

    def del_bookmark(self, word: str) -> bool:
        for i in range(self.bookmark_list.count()):
            item = self.bookmark_list.item(i)
            if item.text() == word:
                self.bookmark_list.takeItem(i)
                return True
        return False

    def del_selected_bookmark(self) -> tuple[bool, str | None]:
        """Delete currently selected bookmark"""
        item = self.bookmark_list.currentItem()
        if item:
            row = self.bookmark_list.row(item)
            self.bookmark_list.takeItem(row)
            return True, item.text()
        return False, None

    def on_del_bookmark(self) -> None:
        ok, text = self.del_selected_bookmark()
        if not ok:
            return
        
        bookmarks = self.get_bookmarks()
        self.update_bookmark_count()
        self.bus.bookmarkChanged.emit(bookmarks, text)

    @Slot()
    def on_item_double_clicked(self, item) -> None:
        self.bus.bookmarkSearchRequested.emit(item.text())

    def update_bookmark_count(self) -> None:
        bookmarks = self.get_bookmarks()
        self.bookmark_count.setText(f"({len(bookmarks)})")

    @Slot()
    def show_context_menu(self, pos) -> None:
        item = self.bookmark_list.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)

        delete_action = menu.addAction("Hapus")
        delete_action.triggered.connect(self.on_del_bookmark)

        menu.exec(self.bookmark_list.viewport().mapToGlobal(pos))
