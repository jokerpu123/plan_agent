from enum import StrEnum


class FocusSessionStatus(StrEnum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    RUNNING = "RUNNING"

    def __str__(self) -> str:
        return str(self.value)
