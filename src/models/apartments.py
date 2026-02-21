from dataclasses import dataclass
from enum import Enum

class AptType(Enum):
    STUDIO = "Студія"
    ONE = "Однокімнатна"
    TWO = "Двокімнатна"
    THREE = "Трикімнатна"
    FOUR = "Чотирикімнатна"

@dataclass
class Apartment:
    id: int = None
    number: str = ""
    floor: int = 0
    type: AptType = AptType.STUDIO
    square_meters: float = 0.0