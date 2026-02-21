from dataclasses import dataclass
from datetime import date

@dataclass
class Resident:
    id: int = None
    full_name: str = ""
    email: str = None
    phone: str = None
    birth_date: date = None
    is_deleted: bool = False