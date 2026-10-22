from enum import StrEnum


class RecurringTaskReminderChannel(StrEnum):
    EMAIL = "EMAIL"
    SMS = "SMS"

    def __str__(self) -> str:
        return str(self.value)
