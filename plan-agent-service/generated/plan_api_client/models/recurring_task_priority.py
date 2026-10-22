from enum import StrEnum


class RecurringTaskPriority(StrEnum):
    HIGH = "HIGH"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    URGENT = "URGENT"

    def __str__(self) -> str:
        return str(self.value)
