from enum import Enum


class RequestTaskSchemaType(str, Enum):
    REQUEST_TASK = "request_task"

    def __str__(self) -> str:
        return str(self.value)
