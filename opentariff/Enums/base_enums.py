from enum import Enum


class EnumBase(Enum):
    """Base class for enums to ensure consistent string representation"""

    @classmethod
    def values(cls) -> list:
        return [member.value for member in cls]


class DayOfWeek(int, EnumBase):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6
