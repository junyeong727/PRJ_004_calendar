"""터미널에서 달력/메모 기능을 직접 확인하는 CLI."""

from __future__ import annotations

import argparse
from datetime import date

from features.api import calendar_month, store
from features.calendar import next_month, pre_month
from objects.calendar import CalendarMonth
from objects.errors import ApiError


def print_month(cal: CalendarMonth) -> None:
    print(f"{cal.year}년 {cal.month}월  (오늘: {cal.today})")
    if cal.highlight_date:
        print(f"검색 강조: {cal.highlight_date}")
    print("일 월 화 수 목 금 토")
    week = []
    for cell in cal.days:
        if not cell.in_current_month:
            token = "   ."
        else:
            mark = " "
            if cell.is_today:
                mark = "*"
            elif cell.is_highlighted:
                mark = "!"
            elif cell.has_memo:
                mark = "m"
            token = f"{cell.day:2d}{mark}"
        week.append(token)
        if cell.weekday == 6:
            print(" ".join(week))
            week = []
    print("표시: *오늘  !검색  m메모")


def cmd_calendar(args: argparse.Namespace) -> None:
    today = date.today()
    year = args.year or today.year
    month = args.month or today.month
    print_month(calendar_month(year, month))


def cmd_pre(args: argparse.Namespace) -> None:
    today = date.today()
    year = args.year or today.year
    month = args.month or today.month
    y, m = pre_month(year, month)
    print_month(calendar_month(y, m))


def cmd_next(args: argparse.Namespace) -> None:
    today = date.today()
    year = args.year or today.year
    month = args.month or today.month
    y, m = next_month(year, month)
    print_month(calendar_month(y, m))


def cmd_search(args: argparse.Namespace) -> None:
    target = date.fromisoformat(args.date)
    print_month(calendar_month(target.year, target.month, highlight=target))


def cmd_memo_add(args: argparse.Namespace) -> None:
    date.fromisoformat(args.date)
    memo = store.create(args.date, args.content)
    print(f"추가됨 id={memo.id} {memo.date} {memo.content}")


def cmd_memo_list(args: argparse.Namespace) -> None:
    memos = store.list_by_date(args.date)
    if not memos:
        print("메모 없음")
        return
    for memo in memos:
        print(f"id={memo.id} {memo.date} {memo.content}")


def cmd_memo_update(args: argparse.Namespace) -> None:
    memo = store.update(args.id, args.content)
    if memo is None:
        raise ApiError(404, "Memo not found")
    print(f"수정됨 id={memo.id} {memo.content}")


def cmd_memo_delete(args: argparse.Namespace) -> None:
    if not store.delete(args.id):
        raise ApiError(404, "Memo not found")
    print(f"삭제됨 id={args.id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PRJ_004 calendar CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    cal = sub.add_parser("calendar", help="이번 달(또는 지정 년월) 달력")
    cal.add_argument("--year", type=int)
    cal.add_argument("--month", type=int)
    cal.set_defaults(func=cmd_calendar)

    pre = sub.add_parser("pre", help="이전달")
    pre.add_argument("--year", type=int)
    pre.add_argument("--month", type=int)
    pre.set_defaults(func=cmd_pre)

    nxt = sub.add_parser("next", help="다음달")
    nxt.add_argument("--year", type=int)
    nxt.add_argument("--month", type=int)
    nxt.set_defaults(func=cmd_next)

    search = sub.add_parser("search", help="년-월-일로 이동")
    search.add_argument("date", help="YYYY-MM-DD")
    search.set_defaults(func=cmd_search)

    add = sub.add_parser("memo-add", help="메모 추가")
    add.add_argument("date", help="YYYY-MM-DD")
    add.add_argument("content")
    add.set_defaults(func=cmd_memo_add)

    listed = sub.add_parser("memo-list", help="해당 날짜 메모")
    listed.add_argument("date", help="YYYY-MM-DD")
    listed.set_defaults(func=cmd_memo_list)

    upd = sub.add_parser("memo-update", help="메모 수정")
    upd.add_argument("id", type=int)
    upd.add_argument("content")
    upd.set_defaults(func=cmd_memo_update)

    delete = sub.add_parser("memo-delete", help="메모 삭제")
    delete.add_argument("id", type=int)
    delete.set_defaults(func=cmd_memo_delete)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except (ValueError, ApiError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
