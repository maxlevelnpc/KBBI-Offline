import os
import html
import sys
import logging

from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtWidgets import QMessageBox


log = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_path: str) -> None:
        self.db_name = db_path
        self.db = None

    def initialize(self) -> QSqlDatabase | None:
        """hubungkan db ke aplikasi."""
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(self.db_name)

        if not self.db.open():
            QMessageBox.critical(
                None,
                "Database Error",
                f"Gagal membuka database {os.path.basename(self.db_name)}.\n\n"
                "Pastikan file database tersedia di folder 'data' "
                "yang berada di direktori yang sama dengan file aplikasi (exe)."
            )
            print(self.db_name)
            sys.exit(1)
        
        log.debug(f"[DB] Berhasil terhubung ke {self.db_name}")
        return self.db

    def close(self) -> None:
        if self.db and self.db.isOpen():
            connection_name = self.db.connectionName()
            self.db.close()
            self.db = None
            QSqlDatabase.removeDatabase(connection_name)
            log.debug("[DB] Koneksi database ditutup.")

    def get_random_words(self, limit: int = 10) -> list[str]:
        """:returns: kata random dalam list"""
        query = QSqlQuery()

        query.prepare(f"""
            SELECT word
            FROM dictionary
            ORDER BY RANDOM()
            LIMIT {limit}
        """)

        if not query.exec():
            print(f"Query gagal: {query.lastError().text()}")
            return []

        words = []

        while query.next():
            word = str(query.value(0)).strip().split()[0]
            words.append(word)

        return words

    def get_text_definitions(self, word: str) -> tuple[bool, list[str] | str]:
        """:returns: definisi (format kasar) dari teks yang diberikan"""
        word_clean = word.strip().lower()

        query = QSqlQuery()
        query.prepare(
            "SELECT arti FROM dictionary WHERE TRIM(word) = :word"
        )
        query.bindValue(":word", word_clean)

        if not query.exec():
            return False, query.lastError().text()

        definitions = []

        while query.next():
            definitions.append(
                html.unescape(str(query.value(0)))
            )

        return True, definitions
