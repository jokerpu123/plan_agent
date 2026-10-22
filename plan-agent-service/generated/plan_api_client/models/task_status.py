from enum import StrEnum


class TaskStatus(StrEnum):
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    POSTPONED = "POSTPONED"
    TODO = "TODO"

    def __str__(self) -> str:
        return str(self.value)
