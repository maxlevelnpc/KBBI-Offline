from __future__ import annotations
import re
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.core.services import ConfigService, DatabaseService


class MainModel:
    def __init__(self, config_service: ConfigService, db_service: DatabaseService) -> None:
        self.config_service = config_service
        self.db_service = db_service

        self.bookmarks: list[str] = []
        self.total_search: int = 0
        self.total_search_session: int = 0
        self.history: list[str] = []

        self._set_settings()
        self.db_service.initialize()

    def _set_settings(self) -> None:
        data = self.config_service.load_config_data()
        if data is not None:
            self.bookmarks = data.get("bookmarks")
            self.total_search = data.get("total_search")
            self.history = data.get("history")

    def get_definitions(self, word: str) -> tuple[bool, str]:
        """
        Ambil definisi dari kata yang diberikan dari database

        :param word: kata yang dicari
        :returns:
            (bool, str):

                True  -> query berhasil (meski hasil bisa kosong)

                False -> terjadi error database/query

                str -> HTML hasil definisi / pesan error / info "tidak ditemukan"
        """
        ok, result = self.db_service.get_text_definitions(word)

        if not ok:
            return False, f"Query gagal: {result}"

        if result:
            sep = "<hr style='border: 0; border-top: 2px solid #2C3E50; margin: 25px 0;'>"
            return True, sep.join(result)

        return (True, f"<b style='color: #d9534f;'>'{word}'</b> tidak ditemukan.")
