import unittest
from datetime import date

from features.calendar import build_month_grid, next_month, pre_month


class CalendarFeatureTest(unittest.TestCase):
    def test_pre_month_rolls_year(self):
        self.assertEqual(pre_month(2026, 1), (2025, 12))
        self.assertEqual(pre_month(2026, 9), (2026, 8))

    def test_next_month_rolls_year(self):
        self.assertEqual(next_month(2025, 12), (2026, 1))
        self.assertEqual(next_month(2026, 9), (2026, 10))

    def test_month_grid_marks_today_search_and_memo(self):
        today = date(2026, 9, 16)
        highlight = date(2026, 9, 1)
        grid = build_month_grid(
            2026,
            9,
            today=today,
            highlight=highlight,
            memo_dates={"2026-09-16"},
        )
        self.assertEqual(grid.year, 2026)
        self.assertEqual(grid.month, 9)
        self.assertEqual(len(grid.days), 42)
        self.assertEqual(grid.days[0].weekday, 0)

        today_cell = next(d for d in grid.days if d.date == "2026-09-16")
        self.assertTrue(today_cell.is_today)
        self.assertTrue(today_cell.has_memo)
        self.assertTrue(today_cell.in_current_month)

        highlight_cell = next(d for d in grid.days if d.date == "2026-09-01")
        self.assertTrue(highlight_cell.is_highlighted)
        self.assertEqual(grid.highlight_date, "2026-09-01")
