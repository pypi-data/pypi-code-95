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

    @staticmethod
    def get_record_type() -> int:
        return 920

    @staticmethod
    def from_row(row: List[str]) -> "Header":
        return Header(
            record_type=row[0],
            distributor_code=row[1],
            retailer_code=row[2],
            timestamp=row[3]
        )


@dataclass(frozen=True)
class Detail(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    nmi: str
    nmi_checksum: str
    payment_gst_exclusive: decimal.Decimal
    gst_amount: Optional[decimal.Decimal]
    payment_gst_inclusive: decimal.Decimal
    payment_date: Optional[datetime.date]

    @staticmethod
    def get_record_type() -> int:
        return 921

    @staticmethod
    def from_row(row: List[str]) -> "Detail":
        return Detail(
            record_type=row[0],
            invoice_number=row[1],
            line_identifier=row[2],
            nmi=row[3],
            nmi_checksum=row[4],
            payment_gst_exclusive=decimal.Decimal(row[5]),
            gst_amount=base.opt_decimal(row[6]),
            payment_gst_inclusive=decimal.Decimal(row[7]),
            payment_date=datetime.datetime.strptime(row[8], "%Y%m%d").date()
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    total_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    total_gst_inclusive: decimal.Decimal
    remittance_count: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 922

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            total_gst_exclusive=decimal.Decimal(row[1]),
            gst_amount=decimal.Decimal(row[2]),
            total_gst_inclusive=decimal.Decimal(row[3]),
            remittance_count=decimal.Decimal(row[4])
        )


class Remittance:

    @staticmethod
    def from_filesystem(path: pathlib.Path) -> "Remittance":
        with open(path, 'r') as f:
            return Remittance(csv.reader(f))

    @staticmethod
    def from_str(f: str) -> "Remittance":
        return Remittance(csv.reader(io.StringIO(f)))

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
                    "got {got} when parsing Remittance file row {row}"
                    .format(got=record_type, row=row))
        if self.header is None:
            raise base.MissingHeader()
        if self.footer is None:
            raise base.MissingFooter()
