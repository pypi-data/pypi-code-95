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
        return 930

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
    invoice_date: datetime.date
    due_date: datetime.date
    total_gst_inclusive: decimal.Decimal
    dispute_indicator: str
    comment: Optional[str]

    @staticmethod
    def get_record_type() -> int:
        return 931

    @staticmethod
    def from_row(row: List[str]) -> "Detail":
        return Detail(
            record_type=row[0],
            invoice_number=row[1],
            nmi=row[2],
            nmi_checksum=row[3],
            invoice_date=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            due_date=datetime.datetime.strptime(row[5], "%Y%m%d").date(),
            total_gst_inclusive=decimal.Decimal(row[6]),
            dispute_indicator=row[7],
            comment=row[8]
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    outstanding_count: decimal.Decimal
    total_gst_inclusive: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 932

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            outstanding_count=decimal.Decimal(row[1]),
            total_gst_inclusive=decimal.Decimal(row[2])
        )


class Outstanding:

    @staticmethod
    def from_filesystem(path: pathlib.Path) -> "Outstanding":
        with open(path, 'r') as f:
            return Outstanding(csv.reader(f))

    @staticmethod
    def from_str(f: str) -> "Outstanding":
        return Outstanding(csv.reader(io.StringIO(f)))

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
                    "got {got} when parsing Outstanding file row {row}"
                    .format(got=record_type, row=row))
        if self.header is None:
            raise base.MissingHeader()
        if self.footer is None:
            raise base.MissingFooter()
