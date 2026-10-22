from enum import StrEnum


class TaskReminderChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"

    def __str__(self) -> str:
        return str(self.value)
