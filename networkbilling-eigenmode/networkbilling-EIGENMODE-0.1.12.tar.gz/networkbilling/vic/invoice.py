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
    invoice_date: datetime.date
    due_date: datetime.date
    retailer_name: str
    retailer_abn: str
    distributor_name: str
    distributor_abn: str
    invoice_status: str
    total_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    total_gst_inclusive: decimal.Decimal
    first_transaction_id: Optional[str]
    last_transaction_id: Optional[str]
    count_transactions: decimal.Decimal
    count_invoice_detail: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 20

    @staticmethod
    def from_row(row: List[str]) -> "Summary":
        return Summary(
            record_type=row[0],
            invoice_number=row[1],
            invoice_date=datetime.datetime.strptime(row[2], "%Y%m%d").date(),
            due_date=datetime.datetime.strptime(row[3], "%Y%m%d").date(),
            retailer_name=row[4],
            retailer_abn=row[5],
            distributor_name=row[6],
            distributor_abn=row[7],
            invoice_status=row[8],
            total_gst_exclusive=decimal.Decimal(row[9]),
            gst_amount=decimal.Decimal(row[10]),
            total_gst_inclusive=decimal.Decimal(row[11]),
            first_transaction_id=row[12],
            last_transaction_id=row[13],
            count_transactions=decimal.Decimal(row[14]),
            count_invoice_detail=decimal.Decimal(row[15])
        )


@dataclass(frozen=True)
class Detail(base.DetailRow):
    record_type: str
    invoice_number: str
    transaction_type: str
    transaction_description: str
    transaction_count: decimal.Decimal
    total_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    total_gst_inclusive: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 21

    @staticmethod
    def from_row(row: List[str]) -> "Detail":
        return Detail(
            record_type=row[0],
            invoice_number=row[1],
            transaction_type=row[2],
            transaction_description=row[3],
            transaction_count=decimal.Decimal(row[4]),
            total_gst_exclusive=decimal.Decimal(row[5]),
            gst_amount=decimal.Decimal(row[6]),
            total_gst_inclusive=decimal.Decimal(row[7])
        )


@dataclass(frozen=True)
class Nuos(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_line_identifier: Optional[str]
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    nmi: str
    nmi_checksum: str
    tariff_code: str
    start_date: datetime.date
    end_date: datetime.date
    tariff_component: str
    reading_type: Optional[str]
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
            old_line_identifier=row[3],
            old_invoice_number=row[4],
            transaction_date=datetime.datetime.strptime(row[5], "%Y%m%d").date(),
            adjustment_indicator=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            tariff_code=row[9],
            start_date=datetime.datetime.strptime(row[10], "%Y%m%d").date(),
            end_date=datetime.datetime.strptime(row[11], "%Y%m%d").date(),
            tariff_component=row[12],
            reading_type=row[13],
            description=row[14],
            quantity=decimal.Decimal(row[15]),
            unit_measure=row[16],
            rate=decimal.Decimal(row[17]),
            charge_gst_exclusive=decimal.Decimal(row[18]),
            gst_amount=decimal.Decimal(row[19]),
            gst_indicator=row[20]
        )


@dataclass(frozen=True)
class Gsl(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_line_identifier: Optional[str]
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    nmi: str
    nmi_checksum: str
    distributor_reference: Optional[str]
    retailer_reference: Optional[str]
    gsl_code: str
    line_description: str
    gsl_event_date: datetime.date
    charge_gst_exclusive: decimal.Decimal
    gst_amount: Optional[decimal.Decimal]
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 400

    @staticmethod
    def from_row(row: List[str]) -> "Gsl":
        return Gsl(
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
            gsl_code=row[11],
            line_description=row[12],
            gsl_event_date=datetime.datetime.strptime(row[13], "%Y%m%d").date(),
            charge_gst_exclusive=decimal.Decimal(row[14]),
            gst_amount=base.opt_decimal(row[15]),
            gst_indicator=row[16]
        )


@dataclass(frozen=True)
class ExcludedServiceCharge(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_line_identifier: Optional[str]
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    nmi: str
    nmi_checksum: str
    distributor_reference: Optional[str]
    retailer_reference: Optional[str]
    service_code: str
    line_description: str
    service_date: datetime.date
    after_hours_indicator: str
    completion_code: Optional[str]
    quantity: decimal.Decimal
    rate: decimal.Decimal
    charge_gst_exclusive: decimal.Decimal
    gst_amount: decimal.Decimal
    gst_indicator: str

    @staticmethod
    def get_record_type() -> int:
        return 600

    @staticmethod
    def from_row(row: List[str]) -> "ExcludedServiceCharge":
        return ExcludedServiceCharge(
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
class InterestCharge(base.DetailRow):
    record_type: str
    invoice_number: str
    line_identifier: str
    old_line_identifier: Optional[str]
    old_invoice_number: Optional[str]
    transaction_date: datetime.date
    adjustment_indicator: str
    nmi: str
    nmi_checksum: str
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
            old_line_identifier=row[3],
            old_invoice_number=row[4],
            transaction_date=datetime.datetime.strptime(row[5], "%Y%m%d").date(),
            adjustment_indicator=row[6],
            nmi=row[7],
            nmi_checksum=row[8],
            original_due_date=datetime.datetime.strptime(row[9], "%Y%m%d").date(),
            principal_amount=decimal.Decimal(row[10]),
            calculation_start_date=datetime.datetime.strptime(row[11], "%Y%m%d").date(),
            calculation_end_date=datetime.datetime.strptime(row[12], "%Y%m%d").date(),
            charge_gst_exclusive=decimal.Decimal(row[13]),
            gst_amount=decimal.Decimal(row[14]),
            gst_indicator=row[15]
        )


@dataclass(frozen=True)
class Footer(base.FooterRow):
    record_type: str
    nuos_charge_total_gst_exclusive: decimal.Decimal
    gsl_charge_total_gst_exclusive: decimal.Decimal
    excluded_charge_total_gst_exclusive: decimal.Decimal
    interest_charge_total_gst_exclusive: decimal.Decimal
    nuos_charge_count: decimal.Decimal
    gsl_charge_count: decimal.Decimal
    excluded_charge_count: decimal.Decimal
    interest_charge_count: decimal.Decimal
    invoice_summary: decimal.Decimal
    invoice_detail: decimal.Decimal

    @staticmethod
    def get_record_type() -> int:
        return 11

    @staticmethod
    def from_row(row: List[str]) -> "Footer":
        return Footer(
            record_type=row[0],
            nuos_charge_total_gst_exclusive=decimal.Decimal(row[1]),
            gsl_charge_total_gst_exclusive=decimal.Decimal(row[2]),
            excluded_charge_total_gst_exclusive=decimal.Decimal(row[3]),
            interest_charge_total_gst_exclusive=decimal.Decimal(row[4]),
            nuos_charge_count=decimal.Decimal(row[5]),
            gsl_charge_count=decimal.Decimal(row[6]),
            excluded_charge_count=decimal.Decimal(row[7]),
            interest_charge_count=decimal.Decimal(row[8]),
            invoice_summary=decimal.Decimal(row[9]),
            invoice_detail=decimal.Decimal(row[10])
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
        self.detail: List[Detail] = list()
        self.nuos: List[Nuos] = list()
        self.gsl: List[Gsl] = list()
        self.excludedservicecharge: List[ExcludedServiceCharge] = list()
        self.interestcharge: List[InterestCharge] = list()
        for row in csv_reader:
            record_type = int(row[0])
            if record_type == Header.get_record_type():
                self.header = Header.from_row(row)
            elif record_type == Summary.get_record_type():
                self.summary.append(Summary.from_row(row))
            elif record_type == Detail.get_record_type():
                self.detail.append(Detail.from_row(row))
            elif record_type == Nuos.get_record_type():
                self.nuos.append(Nuos.from_row(row))
            elif record_type == Gsl.get_record_type():
                self.gsl.append(Gsl.from_row(row))
            elif record_type == ExcludedServiceCharge.get_record_type():
                self.excludedservicecharge.append(ExcludedServiceCharge.from_row(row))
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
