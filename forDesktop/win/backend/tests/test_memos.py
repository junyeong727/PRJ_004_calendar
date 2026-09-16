import tempfile
import unittest
from pathlib import Path

from features.memos import MemoStore


class MemoStoreTest(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.store = MemoStore(Path(self._tmpdir.name) / "memos.db")

    def tearDown(self):
        self.store.close()
        self._tmpdir.cleanup()

    def test_create_list_update_delete(self):
        created = self.store.create("2026-09-16", "면접 준비")
        self.assertEqual(created.content, "면접 준비")

        listed = self.store.list_by_date("2026-09-16")
        self.assertEqual(len(listed), 1)

        month_list = self.store.list_by_month(2026, 9)
        self.assertEqual(month_list[0].id, created.id)

        updated = self.store.update(created.id, "이력서 수정")
        self.assertEqual(updated.content, "이력서 수정")

        self.assertTrue(self.store.delete(created.id))
        self.assertEqual(self.store.list_by_date("2026-09-16"), [])
