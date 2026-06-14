from __future__ import annotations
from typing import TYPE_CHECKING
import logging
import webbrowser

from PySide6.QtCore import QSize, Slot
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QListWidgetItem, QApplication, QMessageBox

from app.core.types import ConfigData

if TYPE_CHECKING:
    from app.views import MainView
    from app.core.bus import EventBus
    from app.models import MainModel


log = logging.getLogger(__name__)


class MainPresenter:
    def __init__(self, ui: MainView, main_model: MainModel, bus: EventBus) -> None:
        self.ui = ui
        self.model = main_model
        self.bus = bus

        self.last_search: str = ""

        self.setupPresenter()

    def setupPresenter(self) -> None:
        self.ui.searchbar.searchRequested.connect(self.handle_search)
        self.ui.open_link.clicked.connect(self.open_external_link)
        self.ui.copy_content.clicked.connect(self.copy_definition)
        self.ui.option_bookmark.triggered.connect(self.show_bookmarks)
        self.ui.option_about.triggered.connect(self.ui.show_about)
        self.ui.add_bookmark_btn.clicked.connect(self.on_bookmark_btn_clicked)
        self.bus.bookmarkSearchRequested.connect(self.handle_search)
        self.ui.refresh_discover_btn.clicked.connect(self.set_explore_words)
        self.bus.bookmarkChanged.connect(self.set_bookmarks)
        QApplication.instance().aboutToQuit.connect(self.save_config)

        for hbtn in self.ui.history_words:
            hbtn.clicked.connect(
                lambda checked=False, b=hbtn: self.handle_search(b.text())
            )

        for dbtn in self.ui.explore_words:
            dbtn.clicked.connect(
                lambda checked=False, b=dbtn: self.handle_search(b.text())
            )

        self.set_explore_words()
        self.refresh_history()
        self.update_search_count(init=True)
        self.set_bookmark_icon("")

        self.HKEY_bookmark_word = QShortcut(QKeySequence("Ctrl+B"), self.ui)
        self.HKEY_bookmark_word.activated.connect(self.on_bookmark_btn_clicked)

        self.HKEY_open_bookmark = QShortcut(QKeySequence("Ctrl+Shift+B"), self.ui)
        self.HKEY_open_bookmark.activated.connect(self.show_bookmarks)

        self.HKEY_copy = QShortcut(QKeySequence("Ctrl+Shift+C"), self.ui)
        self.HKEY_copy.activated.connect(self.copy_definition)

        self.HKEY_search_focus = QShortcut(QKeySequence("Ctrl+L"), self.ui)
        self.HKEY_search_focus.activated.connect(self.ui.searchbar.setSearchFocus)

    @Slot()
    def handle_search(self, word: str | None = None) -> None:
        """
        Cari kata dan menampilkan hasil ke UI.

        :param word: kata yang dicari (opsional, jika None ambil dari searchbar)
        """
        word_to_find = word if word is not None else self.ui.get_search_text()
        
        if not word_to_find:
            return
        
        if word_to_find == self.last_search:
            return
        
        ok, result_html = self.model.get_definitions(word_to_find)
        
        if ok:
            self.ui.display_html(result_html)
            if not result_html.endswith("tidak ditemukan."):
                self.add_history(word_to_find)
                self.refresh_history()
                self.update_search_count()
                self.set_bookmark_icon(word_to_find)
                self.last_search = word_to_find
                self.ui.searchbar.setText(word_to_find)
                self.ui.update_link_text(word_to_find)
        else:
            log.error(result_html)
            QMessageBox.critical(
                self.ui,
                "Database Error",
                "Terjadi kesalahan saat mengambil data dari database.\n\n"
                "Silakan coba lagi. Jika masalah berlanjut, pastikan file database ada dan tidak rusak."
            )

    @Slot()
    def set_explore_words(self) -> None:
        """Set kata untuk dijelajahi"""
        words = self.model.db_service.get_random_words(limit=len(self.ui.explore_words))
        for button, word in zip(self.ui.explore_words, words):
            button.setText(word)

    def refresh_history(self) -> None:
        """Update history yang ditampilkan di UI"""
        refreshed_history = self.model.history
        for btn, history in zip(self.ui.history_words, refreshed_history):
            btn.setText(history)

    def add_history(self, word: str) -> None:
        """Tambahkan kata baru ke history list"""
        h = self.model.history
        h.remove(word) if word in h else h.pop()
        h.insert(0, word)

    def open_external_link(self) -> None:
        webbrowser.open(f"https://kbbi.web.id/{self.last_search}")

    @Slot()
    def copy_definition(self) -> None:
        text = self.ui.result_display.toPlainText().strip()
        if text:
            QApplication.clipboard().setText(text)
            self.ui.toast_label.showMessage("Definisi disalin!")
    
    def update_search_count(self, init: bool = False) -> None:
        """Update total pencarian di UI"""
        if not init:
            self.model.total_search_session += 1
            self.model.total_search += 1

        self.ui.stats.setText(
            f"Pencarian sesi ini: <b>{self.model.total_search_session}</b>\t"
            f"Total pencarian: <b>{self.model.total_search}</b>"
        )
    
    @Slot()
    def on_bookmark_btn_clicked(self) -> None:
        """Ambil kata dari searchbar;
        
        Tambahkan kata ke bookmark jika belum ada. Jika sudah ada, hapus kata dari bookmark"""
        word = self.last_search
        dialog = self.ui.bookmark_dialog

        if not word:
            return
        
        # hapus jika sudah ada
        if word in self.model.bookmarks:
            self.model.bookmarks.remove(word)
            self.set_bookmark_icon(word)
            if dialog and dialog.isVisible():
                dialog.del_bookmark(word)
                dialog.update_bookmark_count()

            self.ui.toast_label.showMessage(f"<b>{word}</b> dihapus dari Bookmarks!")
            return

        # tambahkan jika belum ada di bookmark
        self.model.bookmarks.append(word)
        self.set_bookmark_icon(word)
        if dialog and dialog.isVisible():
            dialog.add_bookmark(word)
            dialog.update_bookmark_count()

        self.ui.toast_label.showMessage(f"<b>{word}</b> ditambahkan ke Bookmark!")

    @Slot()
    def set_bookmarks(self, bookmarks: list[str], deleted_word: str) -> None:
        """Timpa list bookmark dengan bookmark baru"""
        self.model.bookmarks = bookmarks
        self.set_bookmark_icon(deleted_word)
        self.ui.toast_label.showMessage(f"<b>{deleted_word}</b> dihapus dari Bookmark!")

    def refresh_bookmarks(self) -> None:
        """Update bookmark di bookmark dialog"""
        blist = self.ui.bookmark_dialog.bookmark_list
        blist.clear()
        for word in self.model.bookmarks:
            blist.addItem(QListWidgetItem(QIcon(":/app/assets/icons/hashtag.png"), word))

    @Slot()
    def show_bookmarks(self) -> None:
        """Tampilakn bookmark dialog"""
        if self.ui.bookmark_dialog.isVisible():
            self.ui.bookmark_dialog.activateWindow()
            return
        
        self.ui.bookmark_dialog.show()
        self.ui.bookmark_dialog.raise_()
        self.ui.bookmark_dialog.activateWindow()
        
        self.refresh_bookmarks()
        bookmarks = self.ui.bookmark_dialog
        bookmarks.update_bookmark_count()

    def set_bookmark_icon(self, word: str) -> None:
        if word in self.model.bookmarks:
            self.ui.add_bookmark_btn.setIcon(QIcon(":/app/assets/icons/bm.png"))
            self.ui.add_bookmark_btn.setToolTip("Hapus dari Bookmark (Ctrl+B)")
        else:
            self.ui.add_bookmark_btn.setIcon(QIcon(":/app/assets/icons/nobm.png"))
            self.ui.add_bookmark_btn.setToolTip("Tambahkan ke Bookmark (Ctrl+B)")

        self.ui.add_bookmark_btn.setIconSize(QSize(18, 18))
        self.ui.add_bookmark_btn.setFixedSize(26, 26)

    @Slot()
    def save_config(self) -> None:
        config_data: ConfigData = {
            "bookmarks": self.model.bookmarks,
            "total_search": self.model.total_search,
            "history": self.model.history,
        }

        self.model.config_service.save_config_data(config_data)
