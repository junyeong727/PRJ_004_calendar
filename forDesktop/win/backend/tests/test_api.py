import tempfile
import unittest
from datetime import date
from pathlib import Path

from features import api
from features.memos import MemoStore
from objects.errors import ApiError


class ApiFeatureTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        api.store = MemoStore(Path(self._tmpdir.name) / "memos.db")

    def tearDown(self):
        api.store.close()
        self._tmpdir.cleanup()

    def test_calendar_default_is_current_month(self):
        body = api.get_calendar({})
        self.assertEqual(date.today().year, body["year"])
        self.assertEqual(date.today().month, body["month"])
        self.assertEqual(len(body["days"]), 42)
        self.assertTrue(any(day["is_today"] for day in body["days"]))

    def test_pre_and_next_month(self):
        prev = api.get_pre_month({"year": ["2026"], "month": ["1"]})
        nxt = api.get_next_month({"year": ["2025"], "month": ["12"]})
        self.assertEqual((prev["year"], prev["month"]), (2025, 12))
        self.assertEqual((nxt["year"], nxt["month"]), (2026, 1))

    def test_search_highlights_day(self):
        body = api.search_date({"year": ["2026"], "month": ["2"], "day": ["28"]})
        self.assertEqual(body["highlight_date"], "2026-02-28")
        target = next(d for d in body["days"] if d["date"] == "2026-02-28")
        self.assertTrue(target["is_highlighted"])

    def test_search_rejects_invalid_date(self):
        with self.assertRaises(ApiError) as ctx:
            api.search_date({"year": ["2026"], "month": ["2"], "day": ["30"]})
        self.assertEqual(ctx.exception.status, 400)

    def test_memo_crud_and_calendar_flag(self):
        created = api.create_memo({"date": "2026-09-16", "content": "면접 준비"})
        memo_id = created["id"]

        listed = api.list_memos({"date": ["2026-09-16"]})
        self.assertEqual(listed[0]["content"], "면접 준비")

        cal = api.get_calendar({"year": ["2026"], "month": ["9"]})
        cell = next(d for d in cal["days"] if d["date"] == "2026-09-16")
        self.assertTrue(cell["has_memo"])

        updated = api.update_memo(memo_id, {"content": "이력서 수정"})
        self.assertEqual(updated["content"], "이력서 수정")

        api.delete_memo(memo_id)
        after = api.get_calendar({"year": ["2026"], "month": ["9"]})
        cell = next(d for d in after["days"] if d["date"] == "2026-09-16")
        self.assertFalse(cell["has_memo"])
