"""
database.py
------------
Module 3 of the pipeline: persists every detection event to a local
SQLite database and provides the query/export functions used by the
`report` CLI command. SQLite was chosen over a file-only log so
detections can be filtered by date and exported without re-parsing
text files (see docs/DESIGN.md for the schema/ER diagram).
"""

import csv
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src.config import DB_PATH
from src.logger_config import get_logger

logger = get_logger("database")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS detections (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    plate_text      TEXT NOT NULL,
    confidence      REAL NOT NULL,
    source_file     TEXT NOT NULL,
    detected_at     TEXT NOT NULL
);
"""


@dataclass
class DetectionRecord:
    id: Optional[int]
    plate_text: str
    confidence: float
    source_file: str
    detected_at: str


class Database:
    """Small wrapper around sqlite3 for the detections table."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_schema()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self):
        with self._connect() as conn:
            conn.execute(_SCHEMA)
        logger.info("Database ready at %s", self.db_path)

    def insert_detection(self, plate_text: str, confidence: float, source_file: str) -> int:
        detected_at = datetime.now().isoformat(timespec="seconds")
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO detections (plate_text, confidence, source_file, detected_at) "
                "VALUES (?, ?, ?, ?)",
                (plate_text, confidence, source_file, detected_at),
            )
            record_id = cursor.lastrowid
        logger.info("Stored detection #%d: %s", record_id, plate_text)
        return record_id

    def query_between(self, date_from: str, date_to: str) -> List[DetectionRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, plate_text, confidence, source_file, detected_at "
                "FROM detections WHERE date(detected_at) BETWEEN date(?) AND date(?) "
                "ORDER BY detected_at",
                (date_from, date_to),
            ).fetchall()
        return [DetectionRecord(*row) for row in rows]

    def all_records(self) -> List[DetectionRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, plate_text, confidence, source_file, detected_at "
                "FROM detections ORDER BY detected_at"
            ).fetchall()
        return [DetectionRecord(*row) for row in rows]

    @staticmethod
    def export_to_csv(records: List[DetectionRecord], csv_path: str) -> None:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "plate_text", "confidence", "source_file", "detected_at"])
            for r in records:
                writer.writerow([r.id, r.plate_text, r.confidence, r.source_file, r.detected_at])
        logger.info("Exported %d record(s) to %s", len(records), csv_path)
