from dataclasses import dataclass


@dataclass
class LogException:
    exception: Exception
    traceback: str
