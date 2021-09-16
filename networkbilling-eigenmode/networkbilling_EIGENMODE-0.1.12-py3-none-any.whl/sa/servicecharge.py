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
        return 12

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
    old_line_identifier: Optional[str]
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: Optional[str]
    nmi: str
    nmi_checksum: str
    distributor_reference: Optional[str]
    retailer_reference: Optional[str]
    service_code: str
    line_description: str
    service_date: Optional[datetime.date]
    after_hours_indicator: Optional[str]
    completion_code: Optional[str]
    quantity: decimal.Decimal
    rate: decimal.Decimal
    charge_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 916

    @staticmethod
    def from_row(row: List[str]) -> "Detail":
        return Detail(
            record_type=row[0],
            invoice_number=row[1],
            line_identifier=row[2],
            old_line_identifier=row[3],
            old_invoice_number=row[4],
            transaction_date=datetime.datetime.strptime(row[5], "%Y%m%d").date(),
            adjustment_indicator=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            distributor_reference=row[9],
            retailer_reference=row[10],
            service_code=row[11],
            line_description=row[12],
            service_date=datetime.datetime.strptime(row[13], "%Y%m%d").date(),
            after_hours_indicator=row[14],
            completion_code=row[15],
            quantity=decimal.Decimal(row[16]),
            rate=decimal.Decimal(row[17]),
            charge_gst_exclusive=decimal.Decimal(row[18]),
            gst_amount=decimal.Decimal(row[19]),
            gst_indicator=row[20]
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    total_gst_exclusive: decimal.Decimal
    charge_count: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 13

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            total_gst_exclusive=decimal.Decimal(row[1]),
            charge_count=decimal.Decimal(row[2])
        )


class Servicecharge:

    @staticmethod
    def from_filesystem(path: pathlib.Path) -> "Servicecharge":
        with open(path, 'r') as f:
            return Servicecharge(csv.reader(f))

    @staticmethod
    def from_str(f: str) -> "Servicecharge":
        return Servicecharge(csv.reader(io.StringIO(f)))

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
                    "got {got} when parsing Servicecharge file row {row}"
                    .format(got=record_type, row=row))
        if self.header is None:
            raise base.MissingHeader()
        if self.footer is None:
            raise base.MissingFooter()
