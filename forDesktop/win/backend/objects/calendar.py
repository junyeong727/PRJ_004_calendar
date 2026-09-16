from dataclasses import dataclass

from objects.day import DayCell


@dataclass
class CalendarMonth:
    year: int
    month: int
    today: str
    highlight_date: str | None
    days: list[DayCell]

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "today": self.today,
            "highlight_date": self.highlight_date,
            "days": [day.to_dict() for day in self.days],
        }
