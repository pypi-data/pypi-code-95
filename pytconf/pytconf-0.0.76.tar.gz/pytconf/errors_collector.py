from typing import List, Generator


class ErrorsCollector:
    """
    This collector support two types of error. Regular errors and special errors
    Regular errors are the ones to be printed and carry the error_type = false.
    """
    def __init__(self):
        self._errors: List[str] = []
        self.do_help: bool = False
        self.show_errors: bool = True
        self.force_show_errors: bool = False

    def add_error(self, msg: str) -> None:
        self._errors.append(msg)

    def have_errors(self) -> bool:
        return len(self._errors) > 0

    def set_do_help(self) -> None:
        self.do_help = True

    def get_show_errors(self):
        return self.show_errors or self.force_show_errors

    def get_do_help(self) -> bool:
        return self.do_help

    def unset_show_errors(self) -> None:
        self.show_errors = False

    def set_force_show_errors(self) -> None:
        self.force_show_errors = True

    def yield_errors(self) -> Generator[str, None, None]:
        for error in self._errors:
            yield error
