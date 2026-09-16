from dataclasses import dataclass


@dataclass
class Memo:
    id: int
    date: str
    content: str
    created_at: str
    updated_at: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "date": self.date,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
