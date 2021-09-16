from typing import List, Iterable, Optional
import datetime
import decimal
from dataclasses import dataclass
import io
import csv
import pathlib

import networkbilling.base as base


@dataclass(frozen=True)
class Header(base.HeaderRow):
    record_type: str
    distributor_code: str
    retailer_code: str
    timestamp: str
    start_period: datetime.date
    end_period: datetime.date

    @staticmethod
    def get_record_type() -> int:
        return 940

    @staticmethod
    def from_row(row: List[str]) -> "Header":
        return Header(
            record_type=row[0],
            distributor_code=row[1],
            retailer_code=row[2],
            timestamp=row[3],
            start_period=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            end_period=datetime.datetime.strptime(row[5], "%Y%m%d").date()
        )


@dataclass(frozen=True)
class Detail(base.DetailRow):
    record_type: str
    invoice_number: str
    nmi: str
    nmi_checksum: str
    total_gst_inclusive: decimal.Decimal
    balance_gst_inclusive: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 941

    @staticmethod
    def from_row(row: List[str]) -> "Detail":
        return Detail(
            record_type=row[0],
            invoice_number=row[1],
            nmi=row[2],
            nmi_checksum=row[3],
            total_gst_inclusive=decimal.Decimal(row[4]),
            balance_gst_inclusive=decimal.Decimal(row[5])
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    balance_count: decimal.Decimal
    total_gst_inclusive: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 942

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            balance_count=decimal.Decimal(row[1]),
            total_gst_inclusive=decimal.Decimal(row[2])
        )


class Creditbalance:

    @staticmethod
    def from_filesystem(path: pathlib.Path) -> "Creditbalance":
        with open(path, 'r') as f:
            return Creditbalance(csv.reader(f))

    @staticmethod
    def from_str(f: str) -> "Creditbalance":
        return Creditbalance(csv.reader(io.StringIO(f)))

    def __init__(self, csv_reader: Iterable[List[str]]) -> None:
        self.detail: List[Detail] = list()
        for row in csv_reader:
            record_type = int(row[0])
            if record_type == Header.get_record_type():
                self.header = Header.from_row(row)
            elif record_type == Detail.get_record_type():
                self.detail.append(Detail.from_row(row))
            elif record_type == Footer.get_record_type():
                self.footer = Footer.from_row(row)
            else:
                raise base.UnexpectedRecordType(
                    "got {got} when parsing Creditbalance file row {row}"
                    .format(got=record_type, row=row))
        if self.header is None:
            raise base.MissingHeader()
        if self.footer is None:
            raise base.MissingFooter()
