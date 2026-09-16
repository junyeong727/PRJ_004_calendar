from datetime import date, timedelta

from objects.calendar import CalendarMonth
from objects.day import DayCell


def sunday_first_weekday(d: date) -> int:
    """0=Sunday ... 6=Saturday."""
    return (d.weekday() + 1) % 7


def shift_month(year: int, month: int, delta: int) -> tuple[int, int]:
    total = year * 12 + (month - 1) + delta
    return total // 12, total % 12 + 1


def pre_month(year: int, month: int) -> tuple[int, int]:
    return shift_month(year, month, -1)


def next_month(year: int, month: int) -> tuple[int, int]:
    return shift_month(year, month, 1)


def parse_ymd(year: int, month: int, day: int | None = None) -> date:
    if day is None:
        return date(year, month, 1)
    return date(year, month, day)


def build_month_grid(
    year: int,
    month: int,
    *,
    today: date | None = None,
    highlight: date | None = None,
    memo_dates: set[str] | None = None,
) -> CalendarMonth:
    today = today or date.today()
    memo_dates = memo_dates or set()
    first = date(year, month, 1)
    leading = sunday_first_weekday(first)
    grid_start = first - timedelta(days=leading)
    days: list[DayCell] = []

    for i in range(42):
        d = grid_start + timedelta(days=i)
        iso = d.isoformat()
        days.append(
            DayCell(
                year=d.year,
                month=d.month,
                day=d.day,
                weekday=sunday_first_weekday(d),
                in_current_month=d.month == month and d.year == year,
                is_today=d == today,
                is_highlighted=highlight is not None and d == highlight,
                has_memo=iso in memo_dates,
            )
        )

    return CalendarMonth(
        year=year,
        month=month,
        today=today.isoformat(),
        highlight_date=highlight.isoformat() if highlight else None,
        days=days,
    )
