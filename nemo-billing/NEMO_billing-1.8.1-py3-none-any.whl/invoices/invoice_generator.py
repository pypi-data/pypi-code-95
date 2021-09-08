import importlib
import io
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional, Tuple, List, Any

from NEMO.models import User, Project
from NEMO.utilities import get_month_timeframe
from NEMO.views.customization import get_customization
from django.conf import settings
from django.core.files.base import ContentFile
from django.db.models import Sum

from NEMO_billing.invoices.exceptions import NoProjectDetailsSetException, InvoiceAlreadyExistException
from NEMO_billing.invoices.invoice_data_processor import InvoiceDataProcessor
from NEMO_billing.invoices.models import Invoice, ProjectBillingDetails, InvoiceDetailItem, InvoiceSummaryItem
from NEMO_billing.invoices.pdf_utilities import (
    InvoicePDFDocument,
    PDFPageSize,
    SMALL_FONT,
    SMALL_FONT_RIGHT,
    HEADING_FONT,
    HEADING_FONT_CENTERED,
)
from NEMO_billing.invoices.utilities import display_amount


def generate_monthly_invoice(month, project, configuration, user: User, raise_if_exists=False) -> Optional[Invoice]:
    start, end = get_month_timeframe(month)
    return generate_invoice(start, end, project, configuration, user, raise_if_exists)


def generate_invoice(start, end, project: Project, configuration, user, raise_if_exists=False) -> Optional[Invoice]:
    # Start and end will be included in the results. So for example for September data, use: 09/01 to 09/30
    try:
        project_details = ProjectBillingDetails.objects.get(project_id=project.id)
    except ProjectBillingDetails.DoesNotExist:
        raise NoProjectDetailsSetException(project=project)
    # If there is already a invoice for this project for those dates, don't regenerate it (unless void).
    existing_invoices = Invoice.objects.filter(start=start, end=end, project_details=project_details, voided_date=None)
    if existing_invoices.exists():
        if raise_if_exists:
            raise InvoiceAlreadyExistException(existing_invoices.first())
    # No existing invoices, continue
    elif not project_details.no_charge:
        data_processor = invoice_generator_class.get_invoice_data_processor()
        invoice = data_processor.process_data(start, end, project_details, configuration, user)
        if invoice:
            invoice_generator_class.render_invoice(invoice)
            return invoice


class InvoiceGenerator(ABC):
    def __init__(self):
        self.date_time_format = settings.INVOICE_DATETIME_FORMAT
        self.date_format = settings.INVOICE_DATE_FORMAT

    def render_invoice(self, invoice: Invoice):
        file_bytes = io.BytesIO()
        document = self.init_document(invoice, file_bytes)
        self.render_front_page(invoice, document)
        self.render_summary(invoice, document)
        if invoice.configuration.detailed_invoice:
            self.render_details(invoice, document)
        self.close_document(invoice, document, file_bytes)

    def get_invoice_data_processor(self):
        return InvoiceDataProcessor()

    @abstractmethod
    def get_file_extension(self):
        pass

    @abstractmethod
    def init_document(self, invoice: Invoice, file_bytes) -> Any:
        pass

    @abstractmethod
    def render_front_page(self, invoice: Invoice, document):
        pass

    @abstractmethod
    def render_summary(self, invoice: Invoice, document):
        pass

    @abstractmethod
    def render_details(self, invoice: Invoice, document):
        pass

    def close_document(self, invoice: Invoice, document, file_bytes):
        file_bytes.seek(0)
        invoice.file = ContentFile(file_bytes.read(), "invoice." + self.get_file_extension())
        file_bytes.close()
        invoice.save(update_fields=["file"])


class PDFInvoiceGenerator(InvoiceGenerator):
    def get_file_extension(self):
        return "pdf"

    def init_document(self, invoice: Invoice, file_bytes) -> InvoicePDFDocument:
        pdf = InvoicePDFDocument(
            buffer_bytes=file_bytes,
            pagesize=PDFPageSize.Letter,
            header_text=invoice.configuration.merchant_details,
            header_logo=invoice.configuration.merchant_logo,
        )
        return pdf

    def render_front_page(self, invoice: Invoice, pdf: InvoicePDFDocument):
        default_style = pdf.styles[f"{SMALL_FONT}Base11"]
        default_italic_style = pdf.styles[f"{SMALL_FONT}Italic10"]
        heading_style = pdf.styles[f"{HEADING_FONT}Bold18"]
        heading_style_centered = pdf.styles[f"{HEADING_FONT_CENTERED}Bold18"]
        details_key_style = pdf.styles[f"{SMALL_FONT}Bold12"]
        total_charges_style = pdf.styles[f"{SMALL_FONT}Base12"]
        pdf.add_space(1, 10)
        pdf.add_title("Invoice")
        key_value_col_width = [65, None]
        pdf.add_space(1, 30)
        details_data = [
            ("Date:", invoice.created_date.strftime(self.date_format)),
            ("Invoice:", invoice.invoice_number),
            ("Project:", invoice.project_details.name),
            ("Ref/PO:", invoice.project_details.project.application_identifier),
        ]
        pdf.add_table_key_value(details_data, key_value_col_width, details_key_style, default_style)
        pdf.add_space(1, 15)
        pdf.add_table_key_value(
            [("To:", invoice.project_details.addressee)], key_value_col_width, details_key_style, default_style
        )
        pdf.add_space(1, 50)
        facility = get_customization("facility_name")
        pdf.add_heading_paragraph(
            f"{facility} charges for {invoice.start.strftime(self.date_format)} to {invoice.end.strftime(self.date_format)}",
            heading_style_centered,
            fit=True,
            border=True,
        )
        pdf.add_space(1, 15)
        pdf.add_paragraph(
            f"Total {facility} charges: <b>{display_amount(invoice.total_amount, invoice.configuration)}</b>",
            style=total_charges_style,
        )
        pdf.add_space(1, 5)
        pdf.add_paragraph(f"Please refer to attached summary for details.", default_italic_style)
        if invoice.configuration.terms:
            pdf.add_space(1, 70)
            pdf.add_heading_paragraph("Terms and Conditions:", heading_style)
            pdf.add_paragraph(invoice.configuration.terms, default_style)

    def render_summary(self, invoice: Invoice, pdf: InvoicePDFDocument):
        header_name_style = pdf.styles[f"{SMALL_FONT}Bold10"]
        header_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        category_name_style = pdf.styles[f"{SMALL_FONT}Bold12"]
        category_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base12"]
        discount_name_style = pdf.styles[f"{SMALL_FONT}Bold13"]
        discount_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base13"]
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        other_name_style = pdf.styles[f"{SMALL_FONT}Bold10"]
        total_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold12"]
        pdf.add_page_break()
        pdf.add_title("Summary")
        table_data = []
        # Separate type based on invoice configuration options
        separate_item_types = []
        facility_item_types = []

        if invoice.configuration.separate_tool_usage_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.TOOL_USAGE)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.TOOL_USAGE)
        if invoice.configuration.separate_area_access_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.AREA_ACCESS)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.AREA_ACCESS)
        if invoice.configuration.separate_consumable_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.CONSUMABLE)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.CONSUMABLE)
        if invoice.configuration.separate_missed_reservation_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.MISSED_RESERVATION)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.MISSED_RESERVATION)
        if invoice.configuration.separate_staff_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.STAFF_CHARGE)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.STAFF_CHARGE)
        if invoice.configuration.separate_training_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.TRAINING)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.TRAINING)
        if invoice.configuration.separate_custom_charges:
            separate_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.CUSTOM_CHARGE)
        else:
            facility_item_types.append(InvoiceDetailItem.InvoiceDetailItemType.CUSTOM_CHARGE)

        # Deal first with non-empty core facilities
        for core_facility in invoice.sorted_core_facilities():
            if core_facility:
                facility_summary_items = invoice.invoicesummaryitem_set.filter(core_facility=core_facility)
                summary_items = facility_summary_items.filter(
                    summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.ITEM
                )
                facility_display_items = summary_items.filter(item_type__in=facility_item_types)
                sub_total_amount = facility_display_items.aggregate(Sum("amount"))["amount__sum"]
                # Don't show the facility if there are no items in it
                if facility_display_items.exists():
                    table_data.append(["", "", ""])
                    table_data.append(
                        [(core_facility, category_name_style), ("", category_name_style), ("", category_amount_style)]
                    )
                    for item_type in facility_item_types:
                        items = summary_items.filter(item_type=item_type)
                        self.add_items(invoice.configuration, table_data, items, pdf)
                    facility_discount = facility_summary_items.filter(
                        summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.DISCOUNT
                    ).first()
                    facility_discount_amount = Decimal(0)
                    if facility_discount:
                        facility_discount_amount = facility_discount.amount
                        table_data.append(
                            [
                                ("Discount", other_name_style),
                                (facility_discount.details or ""),
                                (display_amount(facility_discount_amount, invoice.configuration), item_amount_style),
                            ]
                        )
                    table_data.append(
                        [
                            ("Subtotal", other_name_style),
                            "",
                            (
                                display_amount(sub_total_amount + facility_discount_amount, invoice.configuration),
                                item_amount_style,
                            ),
                        ]
                    )

        # Add items not in any facilities (and items set as separate in configuration)
        general_summary_items = invoice.invoicesummaryitem_set.filter(
            core_facility=None, summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.ITEM
        )
        for item_type in facility_item_types + separate_item_types:
            if item_type in facility_item_types:
                items = general_summary_items.filter(item_type=item_type)
            else:
                items = invoice.invoicesummaryitem_set.filter(item_type=item_type)
            if items.exists():
                table_data.append(["", "", ""])
                table_data.append(
                    [
                        (
                            InvoiceDetailItem.InvoiceDetailItemType.category_name_for_item_type(item_type),
                            category_name_style,
                        ),
                        "",
                        ("", category_amount_style),
                    ]
                )
                self.add_items(invoice.configuration, table_data, items, pdf)
                sub_total_amount = items.aggregate(Sum("amount"))["amount__sum"]
                table_data.append(
                    [
                        ("Subtotal", other_name_style),
                        "",
                        (display_amount(sub_total_amount, invoice.configuration), item_amount_style),
                    ]
                )

        total_charges_amount = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
        ).aggregate(Sum("amount"))["amount__sum"]
        table_data.append(["", "", ""])
        table_data.append(
            [
                ("Total Charges", category_name_style),
                "",
                (display_amount(total_charges_amount, invoice.configuration), category_amount_style),
            ]
        )

        tax_item = invoice.invoicesummaryitem_set.filter(
            summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX
        ).first()
        if tax_item:
            table_data.append(
                [
                    (tax_item.name, category_name_style),
                    tax_item.details or "",
                    (display_amount(tax_item.amount, invoice.configuration), category_amount_style),
                ]
            )

        table_data.append(
            [
                ("Grand Total", category_name_style),
                "",
                (display_amount(invoice.total_amount, invoice.configuration), total_amount_style),
            ]
        )
        summary_col_width = [None, 87, 87]
        pdf.add_table(
            table_data,
            headers=[("Item", header_name_style), ("Rate", header_name_style), ("Amount Due", header_amount_style)],
            col_width=summary_col_width,
            grid=False,
            border=True,
        )

    def add_items(self, configuration, table_data, items_qs, pdf):
        item_amount_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base10"]
        for item in items_qs:
            # Add prefix of category name only if we have a facility (otherwise it will be in the category with that name)
            item_name = f"{item.category_name_for_item_type()} - {item.name}" if item.core_facility else f"{item.name}"
            table_data.append(
                [item_name, item.details or "", (display_amount(item.amount, configuration), item_amount_style)]
            )

    def render_details(self, invoice: Invoice, pdf: InvoicePDFDocument):
        default_style = pdf.styles[f"{SMALL_FONT}Base12"]
        heading_style_centered = pdf.styles[f"{HEADING_FONT_CENTERED}Bold18"]
        pdf.add_page_break()
        details_col_width = [None, None, 87, 87]
        for core_facility in invoice.sorted_core_facilities():
            facility_name = core_facility if core_facility else "General Charges"
            pdf.add_space(1, 20)
            pdf.add_heading_paragraph(facility_name, heading_style_centered, border=True)
            pdf.add_space(1, 20)
            tool_details = invoice.tool_usage_details(core_facility=core_facility)
            if tool_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Tool Usage", default_style)
                pdf.add_table(
                    *self.duration_details_data(tool_details, "Tool"), col_width=details_col_width, grid=False
                )
            area_details = invoice.area_access_details(core_facility=core_facility)
            if area_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Area Access", default_style)
                pdf.add_table(
                    *self.duration_details_data(area_details, "Area"), col_width=details_col_width, grid=False
                )
            staff_charges_details = invoice.staff_charge_details(core_facility=core_facility)
            if staff_charges_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Technical Work", default_style)
                pdf.add_table(
                    *self.duration_details_data(staff_charges_details, "Item"), col_width=details_col_width, grid=False
                )
            consumable_withdrawals = invoice.consumable_withdrawal_details(core_facility=core_facility)
            if consumable_withdrawals.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Supplies/Materials", default_style)
                pdf.add_table(
                    *self.consumable_details_data(consumable_withdrawals, pdf), col_width=details_col_width, grid=False
                )
            training_details = invoice.training_details(core_facility=core_facility)
            if training_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Training", default_style)
                pdf.add_table(
                    *self.duration_details_data(training_details, "Tool"), col_width=details_col_width, grid=False
                )
            missed_details = invoice.missed_reservation_details(core_facility=core_facility)
            if missed_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Missed Reservation", default_style)
                pdf.add_table(
                    *self.duration_details_data(missed_details, "Reservation"), col_width=details_col_width, grid=False
                )
            custom_details = invoice.custom_charges_details(core_facility=core_facility)
            if custom_details.exists():
                pdf.add_space(1, 10)
                pdf.add_paragraph("Other Charges", default_style)
                pdf.add_table(
                    *self.custom_charge_details_data(custom_details, pdf), col_width=details_col_width, grid=False
                )

    def close_document(self, invoice: Invoice, pdf: InvoicePDFDocument, file_bytes):
        pdf.build()
        super().close_document(invoice, pdf, file_bytes)

    def duration_details_data(self, items: List[InvoiceDetailItem], item_name: str) -> Tuple[List[List], List]:
        return (
            [
                [
                    str(item.user),
                    item.name,
                    item.start.strftime(self.date_time_format),
                    item.end.strftime(self.date_time_format),
                ]
                for item in items
            ],
            ["User", item_name, "Start Time", "End Time"],
        )

    def consumable_details_data(self, items: List[InvoiceDetailItem], pdf) -> Tuple[List[List], List]:
        quantity_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        quantity_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [
                    str(item.user),
                    item.name,
                    item.start.strftime(self.date_time_format),
                    (item.quantity_display(), quantity_item_style),
                ]
                for item in items
            ],
            ["User", "Supply", "Date", ("Quantity", quantity_header_style)],
        )

    def custom_charge_details_data(self, items: List[InvoiceDetailItem], pdf) -> Tuple[List[List], List]:
        amount_item_style = pdf.styles[f"{SMALL_FONT_RIGHT}Base8"]
        amount_header_style = pdf.styles[f"{SMALL_FONT_RIGHT}Bold10"]
        return (
            [
                [
                    str(item.user),
                    item.name,
                    item.start.strftime(self.date_time_format),
                    (item.amount_display(), amount_item_style),
                ]
                for item in items
            ],
            ["User", "Charge", "Date", ("Amount", amount_header_style)],
        )


def get_invoice_generator_class() -> InvoiceGenerator:
    rates_class = getattr(
        settings, "INVOICE_GENERATOR_CLASS", "NEMO_billing.invoices.invoice_generator.PDFInvoiceGenerator"
    )
    assert isinstance(rates_class, str)
    pkg, attr = rates_class.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret()


invoice_generator_class = get_invoice_generator_class()
