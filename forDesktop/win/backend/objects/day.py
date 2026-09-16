from dataclasses import dataclass


@dataclass
class DayCell:
    year: int
    month: int
    day: int
    weekday: int
    in_current_month: bool
    is_today: bool
    is_highlighted: bool
    has_memo: bool

    @property
    def date(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "weekday": self.weekday,
            "in_current_month": self.in_current_month,
            "is_today": self.is_today,
            "is_highlighted": self.is_highlighted,
            "has_memo": self.has_memo,
            "date": self.date,
        }
