import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from objects.memo import Memo

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "memos.db"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _row_to_memo(row: sqlite3.Row) -> Memo:
    return Memo(
        id=row["id"],
        date=row["date"],
        content=row["content"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class MemoStore:
    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS memos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self._conn.execute("CREATE INDEX IF NOT EXISTS idx_memos_date ON memos(date)")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def list_by_date(self, date_iso: str) -> list[Memo]:
        rows = self._conn.execute(
            "SELECT * FROM memos WHERE date = ? ORDER BY id",
            (date_iso,),
        ).fetchall()
        return [_row_to_memo(r) for r in rows]

    def list_by_month(self, year: int, month: int) -> list[Memo]:
        prefix = f"{year:04d}-{month:02d}-"
        rows = self._conn.execute(
            "SELECT * FROM memos WHERE date LIKE ? ORDER BY date, id",
            (prefix + "%",),
        ).fetchall()
        return [_row_to_memo(r) for r in rows]

    def dates_in_range(self, start_iso: str, end_iso: str) -> set[str]:
        rows = self._conn.execute(
            "SELECT DISTINCT date FROM memos WHERE date >= ? AND date <= ?",
            (start_iso, end_iso),
        ).fetchall()
        return {r["date"] for r in rows}

    def create(self, date_iso: str, content: str) -> Memo:
        now = _utc_now()
        cur = self._conn.execute(
            """
            INSERT INTO memos (date, content, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            (date_iso, content, now, now),
        )
        self._conn.commit()
        memo = self.get(cur.lastrowid)
        assert memo is not None
        return memo

    def get(self, memo_id: int) -> Memo | None:
        row = self._conn.execute("SELECT * FROM memos WHERE id = ?", (memo_id,)).fetchone()
        return _row_to_memo(row) if row else None

    def update(self, memo_id: int, content: str) -> Memo | None:
        if self.get(memo_id) is None:
            return None
        now = _utc_now()
        self._conn.execute(
            "UPDATE memos SET content = ?, updated_at = ? WHERE id = ?",
            (content, now, memo_id),
        )
        self._conn.commit()
        return self.get(memo_id)

    def delete(self, memo_id: int) -> bool:
        cur = self._conn.execute("DELETE FROM memos WHERE id = ?", (memo_id,))
        self._conn.commit()
        return cur.rowcount > 0
