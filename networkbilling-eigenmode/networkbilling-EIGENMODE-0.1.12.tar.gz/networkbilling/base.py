from typing import List, Optional, Any
import decimal

import abc


def opt_decimal(s: str) -> Optional[decimal.Decimal]:
    if s == "":
        return None
    else:
        return decimal.Decimal(s)


class InvalidFilename(Exception):
    pass


class UnsupportedState(Exception):
    pass


class UnexpectedRecordType(Exception):
    pass


class UnexpectedNumberOfRows(Exception):
    pass


class MissingHeader(Exception):
    pass


class MissingFooter(Exception):
    pass


class NetworkRow(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def from_row(row: List[str]) -> Any:
        ...

    @staticmethod
    @abc.abstractmethod
    def get_record_type() -> int:
        ...

    def is_header(self) -> bool:
        return False

    def is_footer(self) -> bool:
        return False


class DetailRow(NetworkRow):
    pass


class HeaderRow(NetworkRow):
    def is_header(self) -> bool:
        return True


class FooterRow(NetworkRow):
    def is_footer(self) -> bool:
        return True
