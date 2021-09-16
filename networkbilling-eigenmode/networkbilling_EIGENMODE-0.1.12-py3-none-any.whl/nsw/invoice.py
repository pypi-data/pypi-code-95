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
        return 10

    @staticmethod
    def from_row(row: List[str]) -> "Header":
        return Header(
            record_type=row[0],
            distributor_code=row[1],
            retailer_code=row[2],
            timestamp=row[3]
        )


@dataclass(frozen=True)
class Summary(base.DetailRow):
    record_type: str
    invoice_number: str
    nmi: str
    nmi_checksum: str
    invoice_date: datetime.date
    due_date: datetime.date
    distributor_name: str
    distributor_abn: str
    retailer_name: str
    retailer_abn: str
    invoice_status: str
    total_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    total_gst_inclusive: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 20

    @staticmethod
    def from_row(row: List[str]) -> "Summary":
        return Summary(
            record_type=row[0],
            invoice_number=row[1],
            nmi=row[2],
            nmi_checksum=row[3],
            invoice_date=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            due_date=datetime.datetime.strptime(row[5], "%Y%m%d").date(),
            distributor_name=row[6],
            distributor_abn=row[7],
            retailer_name=row[8],
            retailer_abn=row[9],
            invoice_status=row[10],
            total_gst_exclusive=decimal.Decimal(row[11]),
            gst_amount=decimal.Decimal(row[12]),
            total_gst_inclusive=decimal.Decimal(row[13]),
            gst_indicator=row[14]
        )


@dataclass(frozen=True)
class Nuos(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    adjustment_reason: Optional[str]
    nmi: str
    nmi_checksum: str
    tariff_code: str
    step_number: decimal.Decimal
    start_date: datetime.date
    end_date: datetime.date
    tariff_component: str
    reading_type: str
    description: str
    quantity: decimal.Decimal
    unit_measure: str
    rate: decimal.Decimal
    charge_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 100

    @staticmethod
    def from_row(row: List[str]) -> "Nuos":
        return Nuos(
            record_type=row[0],
            invoice_number=row[1],
            line_identifier=row[2],
            old_invoice_number=row[3],
            transaction_date=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            adjustment_indicator=row[5],
            adjustment_reason=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            tariff_code=row[9],
            step_number=decimal.Decimal(row[10]),
            start_date=datetime.datetime.strptime(row[11], "%Y%m%d").date(),
            end_date=datetime.datetime.strptime(row[12], "%Y%m%d").date(),
            tariff_component=row[13],
            reading_type=row[14],
            description=row[15],
            quantity=decimal.Decimal(row[16]),
            unit_measure=row[17],
            rate=decimal.Decimal(row[18]),
            charge_gst_exclusive=decimal.Decimal(row[19]),
            gst_amount=decimal.Decimal(row[20]),
            gst_indicator=row[21]
        )


@dataclass(frozen=True)
class EventCharge(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    adjustment_reason: Optional[str]
    nmi: str
    nmi_checksum: str
    distributor_reference: Optional[str]
    retailer_reference: Optional[str]
    distributor_rate_code: str
    line_description: str
    charge_date: datetime.date
    quantity: decimal.Decimal
    unit_of_measure: str
    rate: decimal.Decimal
    charge_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 200

    @staticmethod
    def from_row(row: List[str]) -> "EventCharge":
        return EventCharge(
            record_type=row[0],
            invoice_number=row[1],
            line_identifier=row[2],
            old_invoice_number=row[3],
            transaction_date=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            adjustment_indicator=row[5],
            adjustment_reason=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            distributor_reference=row[9],
            retailer_reference=row[10],
            distributor_rate_code=row[11],
            line_description=row[12],
            charge_date=datetime.datetime.strptime(row[13], "%Y%m%d").date(),
            quantity=decimal.Decimal(row[14]),
            unit_of_measure=row[15],
            rate=decimal.Decimal(row[16]),
            charge_gst_exclusive=decimal.Decimal(row[17]),
            gst_amount=decimal.Decimal(row[18]),
            gst_indicator=row[19]
        )


@dataclass(frozen=True)
class InterestCharge(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    adjustment_reason: Optional[str]
    nmi: str
    nmi_checksum: str
    overdue_invoice_number: str
    original_due_date: datetime.date
    principal_amount: decimal.Decimal
    calculation_start_date: datetime.date
    calculation_end_date: datetime.date
    charge_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 900

    @staticmethod
    def from_row(row: List[str]) -> "InterestCharge":
        return InterestCharge(
            record_type=row[0],
            invoice_number=row[1],
            line_identifier=row[2],
            old_invoice_number=row[3],
            transaction_date=datetime.datetime.strptime(row[4], "%Y%m%d").date(),
            adjustment_indicator=row[5],
            adjustment_reason=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            overdue_invoice_number=row[9],
            original_due_date=datetime.datetime.strptime(row[10], "%Y%m%d").date(),
            principal_amount=decimal.Decimal(row[11]),
            calculation_start_date=datetime.datetime.strptime(row[12], "%Y%m%d").date(),
            calculation_end_date=datetime.datetime.strptime(row[13], "%Y%m%d").date(),
            charge_gst_exclusive=decimal.Decimal(row[14]),
            gst_amount=decimal.Decimal(row[15]),
            gst_indicator=row[16]
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    charge_count: decimal.Decimal
    summary_count: decimal.Decimal
    total_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    total_gst_inclusive: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 11

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            charge_count=decimal.Decimal(row[1]),
            summary_count=decimal.Decimal(row[2]),
            total_gst_exclusive=decimal.Decimal(row[3]),
            gst_amount=decimal.Decimal(row[4]),
            total_gst_inclusive=decimal.Decimal(row[5])
        )


class Invoice:

    @staticmethod
    def from_filesystem(path: pathlib.Path) -> "Invoice":
        with open(path, 'r') as f:
            return Invoice(csv.reader(f))

    @staticmethod
    def from_str(f: str) -> "Invoice":
        return Invoice(csv.reader(io.StringIO(f)))

    def __init__(self, csv_reader: Iterable[List[str]]) -> None:
        self.summary: List[Summary] = list()
        self.nuos: List[Nuos] = list()
        self.eventcharge: List[EventCharge] = list()
        self.interestcharge: List[InterestCharge] = list()
        for row in csv_reader:
            record_type = int(row[0])
            if record_type == Header.get_record_type():
                self.header = Header.from_row(row)
            elif record_type == Summary.get_record_type():
                self.summary.append(Summary.from_row(row))
            elif record_type == Nuos.get_record_type():
                self.nuos.append(Nuos.from_row(row))
            elif record_type == EventCharge.get_record_type():
                self.eventcharge.append(EventCharge.from_row(row))
            elif record_type == InterestCharge.get_record_type():
                self.interestcharge.append(InterestCharge.from_row(row))
            elif record_type == Footer.get_record_type():
                self.footer = Footer.from_row(row)
            else:
                raise base.UnexpectedRecordType(
                    "got {got} when parsing Invoice file row {row}"
                    .format(got=record_type, row=row))
        if self.header is None:
            raise base.MissingHeader()
        if self.footer is None:
            raise base.MissingFooter()
