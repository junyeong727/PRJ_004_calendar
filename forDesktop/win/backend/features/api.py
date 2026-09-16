from datetime import date
from typing import Any
from urllib.parse import parse_qs

from features.calendar import build_month_grid, next_month, parse_ymd, pre_month
from features.memos import MemoStore
from objects.calendar import CalendarMonth
from objects.errors import ApiError

store = MemoStore()


def parse_query(raw_query: str) -> dict[str, list[str]]:
    return parse_qs(raw_query, keep_blank_values=True)


def _query_int(qs: dict[str, list[str]], key: str, default: int | None = None) -> int | None:
    values = qs.get(key)
    if not values or values[0] == "":
        return default
    try:
        return int(values[0])
    except ValueError as exc:
        raise ApiError(400, f"Invalid {key}") from exc


def _query_str(qs: dict[str, list[str]], key: str) -> str | None:
    values = qs.get(key)
    if not values or values[0] == "":
        return None
    return values[0]


def _require_year_month(year: int | None, month: int | None) -> tuple[int, int]:
    if year is None or month is None:
        raise ApiError(400, "year and month are required")
    if not (1 <= year <= 9999 and 1 <= month <= 12):
        raise ApiError(400, "Invalid year or month")
    try:
        date(year, month, 1)
    except ValueError as exc:
        raise ApiError(400, "Invalid year or month") from exc
    return year, month


def _memo_dates_for_grid(year: int, month: int) -> set[str]:
    grid = build_month_grid(year, month)
    start = grid.days[0].date
    end = grid.days[-1].date
    return store.dates_in_range(start, end)


def calendar_month(
    year: int, month: int, highlight: date | None = None
) -> CalendarMonth:
    memo_dates = _memo_dates_for_grid(year, month)
    return build_month_grid(year, month, highlight=highlight, memo_dates=memo_dates)


def get_calendar(qs: dict[str, list[str]]) -> dict[str, Any]:
    today = date.today()
    year = _query_int(qs, "year", today.year)
    month = _query_int(qs, "month", today.month)
    year, month = _require_year_month(year, month)
    return calendar_month(year, month).to_dict()


def get_pre_month(qs: dict[str, list[str]]) -> dict[str, Any]:
    year, month = _require_year_month(_query_int(qs, "year"), _query_int(qs, "month"))
    y, m = pre_month(year, month)
    return calendar_month(y, m).to_dict()


def get_next_month(qs: dict[str, list[str]]) -> dict[str, Any]:
    year, month = _require_year_month(_query_int(qs, "year"), _query_int(qs, "month"))
    y, m = next_month(year, month)
    return calendar_month(y, m).to_dict()


def search_date(qs: dict[str, list[str]]) -> dict[str, Any]:
    year, month = _require_year_month(_query_int(qs, "year"), _query_int(qs, "month"))
    day = _query_int(qs, "day")
    if day is None:
        raise ApiError(400, "day is required")
    try:
        target = parse_ymd(year, month, day)
    except ValueError as exc:
        raise ApiError(400, "Invalid date") from exc
    return calendar_month(target.year, target.month, highlight=target).to_dict()


def list_memos(qs: dict[str, list[str]]) -> list[dict[str, Any]]:
    date_iso = _query_str(qs, "date")
    if date_iso:
        try:
            date.fromisoformat(date_iso)
        except ValueError as exc:
            raise ApiError(400, "Invalid date") from exc
        return [m.to_dict() for m in store.list_by_date(date_iso)]

    year = _query_int(qs, "year")
    month = _query_int(qs, "month")
    if year is not None and month is not None:
        year, month = _require_year_month(year, month)
        return [m.to_dict() for m in store.list_by_month(year, month)]
    raise ApiError(400, "Provide date, or year and month")


def create_memo(body: dict[str, Any]) -> dict[str, Any]:
    date_iso = body.get("date")
    content = body.get("content")
    if not isinstance(date_iso, str) or not isinstance(content, str):
        raise ApiError(400, "date and content are required")
    content = content.strip()
    if not content:
        raise ApiError(400, "content must not be empty")
    try:
        date.fromisoformat(date_iso)
    except ValueError as exc:
        raise ApiError(400, "Invalid date") from exc
    return store.create(date_iso, content).to_dict()


def update_memo(memo_id: int, body: dict[str, Any]) -> dict[str, Any]:
    content = body.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ApiError(400, "content must not be empty")
    updated = store.update(memo_id, content.strip())
    if updated is None:
        raise ApiError(404, "Memo not found")
    return updated.to_dict()


def delete_memo(memo_id: int) -> None:
    if not store.delete(memo_id):
        raise ApiError(404, "Memo not found")
