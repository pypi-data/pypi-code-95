import enum


class Result(enum.Enum):
    PASSED = False, False
    FAILED = True, False
    ABORTED = True, True

    @property
    def failed(self) -> bool:
        return self.value[0]

    @property
    def aborted(self) -> bool:
        return self.value[1]
