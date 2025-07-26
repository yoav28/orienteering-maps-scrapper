from get_map import get_map
from typing import Optional


class Event:

    def __init__(self, event_id: int, name: str, country: str, date: str, location: tuple[float, float]):
        self.name: str = name
        self.id: int = event_id
        self.country: str = country
        self.location: tuple[float, float] = location
        self.date: str = date
        self.map: Optional[str] = None


    def __eq__(self, other) -> bool:
        if isinstance(other, Event):
            return self.id == other.id or self.name == other.name
        return False


    def __str__(self) -> str:
        return self.name


    def __bool__(self) -> bool:
        return self.map is not None and self.location is not None


    def get_map(self, cookies: dict) -> None:
        self.map = get_map(self.id, cookies=cookies)
