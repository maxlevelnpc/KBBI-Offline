from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Slot, QSize
from PySide6.QtGui import QIcon, Qt, QAction
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QTextEdit, QMenu, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
)

from app.widgets import SearchBar, FlowLayout, BookmarkDialog, ToastLabel

if TYPE_CHECKING:
    from app.core.bus import EventBus


log = logging.getLogger(__name__)


class MainView(QMainWindow):
    def __init__(self, bus: EventBus) -> None:
        super().__init__()
        self.bus = bus

        self.explore_words: list[QPushButton] = []
        self.history_words: list[QPushButton] = []

        self.setupUI()

    def setupUI(self) -> None:
        self.setWindowTitle("KBBI Offline")
        self.setWindowIcon(QIcon(":/app/assets/icons/main.png"))
        self.resize(600, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.toast_label = ToastLabel(self)

        # ////////////////////////////////////////////////////////////////////////////////////////////////
        
        self.option_btn = QPushButton()
        self.option_btn.setIcon(QIcon(":/app/assets/icons/menu.png"))
        self.option_btn.setIconSize(QSize(22, 22))
        self.option_btn.setObjectName("menuBtn")
        self.option_menu = QMenu()
        self.option_bookmark = QAction(QIcon(":/app/assets/icons/bookmark.png"), "Bookmark\t(Ctrl+Shift+B)")
        self.option_about = QAction(QIcon(":/app/assets/icons/information.png"), "Tentang Aplikasi")
        self.option_menu.addAction(self.option_bookmark)
        self.option_menu.addSeparator()
        self.option_menu.addAction(self.option_about)
        self.option_btn.setMenu(self.option_menu)

        self.searchbar = SearchBar()

        searchbar_layout = QHBoxLayout()
        searchbar_layout.addWidget(self.option_btn)
        searchbar_layout.addWidget(self.searchbar)

        # ---

        self.open_link = QPushButton("https://kbbi.web.id/")
        self.open_link.setIcon(QIcon(":/app/assets/icons/ext-link.png"))
        self.open_link.setIconSize(QSize(18, 18))
        self.open_link.setObjectName("openLink")
        self.open_link.setCursor(Qt.CursorShape.PointingHandCursor)

        self.add_bookmark_btn = QPushButton()
        self.add_bookmark_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_bookmark_btn.setToolTip("Tambahkan ke Bookmark (Ctrl+B)")
        self.add_bookmark_btn.setObjectName("toolBtn")

        self.copy_content = QPushButton()
        self.copy_content.setIcon(QIcon(":/app/assets/icons/copy.png"))
        self.copy_content.setIconSize(QSize(18, 18))
        self.copy_content.setFixedSize(26, 26)
        self.copy_content.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_content.setToolTip("Salin definisi (Ctrl+Shift+C)")
        self.copy_content.setObjectName("toolBtn")

        tools_layout = QHBoxLayout()
        tools_layout.addWidget(self.open_link)
        tools_layout.addWidget(self.add_bookmark_btn)
        tools_layout.addWidget(self.copy_content)

        # ---

        self.history_title = QLabel("Terakhir Dicari")
        self.history_title.setStyleSheet("font-weight: bold;")
        self.history_title.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.stats = QLabel("Pencarian sesi ini: <b>0</b>\tTotal pencarian: <b>0</b>")
        self.stats.setObjectName("stats")
        
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(self.history_title)
        stats_layout.addStretch()
        stats_layout.addWidget(self.stats)

        # ---

        history_layout = FlowLayout()
        history_layout.setSpacing(2)
        for _ in range(10):
            history_btn = QPushButton("")
            history_btn.setObjectName("historyButtons")
            history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.history_words.append(history_btn)
            history_layout.addWidget(history_btn)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)

        self.discover_title = QLabel("Kata untuk Dijelajahi")
        self.discover_title.setStyleSheet("font-weight: bold;")

        self.refresh_discover_btn = QPushButton()
        self.refresh_discover_btn.setIcon(QIcon(":/app/assets/icons/refresh.png"))
        self.refresh_discover_btn.setIconSize(QSize(18, 18))
        self.refresh_discover_btn.setFixedSize(26, 26)
        self.refresh_discover_btn.setObjectName("transIconBtn")
        self.refresh_discover_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        explore_label_layout = QHBoxLayout()
        explore_label_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        explore_label_layout.addWidget(self.discover_title)
        explore_label_layout.addWidget(self.refresh_discover_btn)

        explore_btn_layout = FlowLayout()
        explore_btn_layout.setSpacing(2)
        for _ in range(10):  # atur jumplah kata untuk dijelajahi. 10-20
            button = QPushButton("")
            button.setObjectName("discoverButtons")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            self.explore_words.append(button)
            explore_btn_layout.addWidget(button)

        # ---

        main_layout.addLayout(searchbar_layout)
        main_layout.addLayout(stats_layout)
        main_layout.addLayout(history_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(tools_layout)
        main_layout.addWidget(self.result_display)
        main_layout.addLayout(explore_label_layout)
        main_layout.addLayout(explore_btn_layout)

        # ////////////////////////////////////////////////////////////////////////////////////////////////

        self.bookmark_dialog = BookmarkDialog(self, self.bus)

    def get_search_text(self) -> str:
        return self.searchbar.text().strip().lower()
    
    def display_html(self, content: str) -> None:
        self.result_display.setHtml(content)

    def update_link_text(self, word: str) -> None:
        self.open_link.setText(f'Lihat kata "{word}" di KBBI daring.')
        self.open_link.setToolTip(f"https://kbbi.web.id/{word}")

    @Slot()
    def show_about(self) -> None:
        QMessageBox.about(
            self,
            "Tentang Aplikasi",
            """
            <h3>KBBI Offline</h3>
            <p>KBBI Luring untuk Desktop</p>

            <p>
            <b>Versi:</b> 1.0.0<br>
            <b>Pembuat:</b> misguidedash27
            </p>

            <p>
            GitHub:<br>
            <a href="https://github.com/maxlevelnpc">
            https://github.com/maxlevelnpc
            </a>
            </p>
            """
        )
