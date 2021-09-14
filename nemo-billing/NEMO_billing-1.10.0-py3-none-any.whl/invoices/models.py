import os
from datetime import timedelta
from decimal import Decimal
from typing import List, Dict

from NEMO import fields
from NEMO.models import Project, User, Customization, TaskImages
from NEMO.utilities import create_email_attachment
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from NEMO_billing.invoices.utilities import (
    get_invoice_document_filename,
    get_merchant_logo_filename,
    display_amount,
    render_and_send_email,
)
from NEMO_billing.models import CoreFacility
from NEMO_billing.rates.models import Rate, RateCategory


class ProjectBillingDetails(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    category = models.ForeignKey(RateCategory, null=True, blank=True, on_delete=models.SET_NULL)
    project_name = models.CharField(
        null=True,
        blank=True,
        max_length=200,
        help_text="The project name that will appear on the invoices. Leave blank to use NEMO project name",
    )
    contact_name = models.CharField(
        null=True, blank=True, max_length=255, help_text="The contact name to use in the invoice email"
    )
    contact_phone = models.CharField(
        null=True, blank=True, max_length=40, help_text="The contact's phone number"
    )
    contact_email = fields.MultiEmailField(
        null=True,
        blank=True,
        help_text="Email to send the invoice to. A comma-separated list can be used. Leave blank to use project managers/PIs emails",
    )
    expires_on = models.DateField(
        null=True, blank=True, help_text="Date after which this project will be automatically deactivated."
    )
    addressee = models.TextField(null=True, blank=True, help_text="The addressee details to be included in the invoice")
    comments = models.TextField(null=True, blank=True)
    no_charge = models.BooleanField(
        default=False, help_text="Check this box if invoices should not be created for this project."
    )
    no_tax = models.BooleanField(
        default=False, help_text="Check this box if this project is tax exempt."
    )

    @property
    def name(self):
        return self.project_name if self.project_name else self.project.name

    def clean(self):
        if not self.category and RateCategory.objects.exists():
            raise ValidationError({"category": "You need to select a rate category for this project"})

    def email_to(self) -> List[str]:
        # return project PIs emails if not set here
        return self.contact_email if not self.email_empty() else [pi.email for pi in self.project.manager_set.all()]

    def email_empty(self):
        return not self.contact_email or not [email for email in self.contact_email if email]

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Project details"


class InvoiceConfiguration(models.Model):
    name = models.CharField(max_length=200, unique=True, help_text="The name of this invoice configuration")
    invoice_due_in = models.PositiveIntegerField(
        help_text="The default number of days invoices are due after", default=30
    )
    reminder_frequency = models.PositiveIntegerField(
        null=True,
        blank=True,
        default=7,
        help_text="How often to send a reminder. Default value is 7, meaning every week after past due invoice",
    )
    email_from = models.EmailField(help_text="The email address used to send invoices and reminders")
    email_cc = fields.MultiEmailField(
        null=True, blank=True, help_text="Email to cc the invoice to. A comma-separated list can be used"
    )
    merchant_name = models.CharField(max_length=255)
    merchant_details = models.TextField(
        null=True,
        blank=True,
        help_text="The merchant details to be included in the invoice (address, phone number etc.)",
    )
    merchant_logo = models.ImageField(null=True, blank=True, upload_to=get_merchant_logo_filename)
    terms = models.TextField(null=True, blank=True, help_text="Terms and conditions to be included in the invoice")

    currency = models.CharField(max_length=4, default="USD")
    currency_symbol = models.CharField(null=True, blank=True, max_length=4, default="$")

    tax = models.DecimalField(
        null=True, blank=True, decimal_places=3, max_digits=5, help_text="Tax in percent. For 20.5% enter 20.5"
    )
    tax_name = models.CharField(max_length=50, null=True, blank=True, default="VAT")

    detailed_invoice = models.BooleanField(
        default=True, help_text="Check this box if customers should receive a detailed invoice."
    )

    separate_tool_usage_charges = models.BooleanField(
        default=False, help_text="Check this box to display tool usage charges as a separate invoice category"
    )
    separate_area_access_charges = models.BooleanField(
        default=False, help_text="Check this box to display area access charges as a separate invoice category"
    )
    separate_staff_charges = models.BooleanField(
        default=False, help_text="Check this box to display staff charges as a separate invoice category"
    )
    separate_consumable_charges = models.BooleanField(
        default=False, help_text="Check this box to display supplies/material as a separate invoice category"
    )
    separate_missed_reservation_charges = models.BooleanField(
        default=False, help_text="Check this box to display missed reservation charges as a separate invoice category"
    )
    separate_training_charges = models.BooleanField(
        default=False, help_text="Check this box to display training charges as a separate invoice category"
    )
    separate_custom_charges = models.BooleanField(
        default=False, help_text="Check this box to display custom charges as a separate invoice category"
    )

    def tax_display(self):
        return f"{self.tax:.2f}"

    def tax_amount(self):
        return self.tax / Decimal(100)

    def __str__(self):
        return self.name


class Invoice(models.Model):
    invoice_number = models.CharField(
        null=False, blank=True, max_length=100, unique=True, help_text="Leave blank to be assigned automatically"
    )
    start = models.DateTimeField()
    end = models.DateTimeField()

    configuration = models.ForeignKey(InvoiceConfiguration, on_delete=models.PROTECT)
    project_details = models.ForeignKey(ProjectBillingDetails, on_delete=models.PROTECT)

    due_date = models.DateField(blank=True, null=True)
    sent_date = models.DateTimeField(blank=True, null=True)
    last_sent_date = models.DateTimeField(blank=True, null=True)
    last_reminder_sent_date = models.DateTimeField(blank=True, null=True)
    reviewed_date = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        User, blank=True, null=True, related_name="reviewed_invoice_set", on_delete=models.PROTECT
    )
    voided_date = models.DateTimeField(blank=True, null=True)
    voided_by = models.ForeignKey(
        User, blank=True, null=True, related_name="voided_invoice_set", on_delete=models.PROTECT
    )

    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    created_date = models.DateTimeField(auto_now_add=True)

    total_amount = models.DecimalField(decimal_places=2, max_digits=14)

    file = models.FileField(null=True, blank=True, max_length=255, upload_to=get_invoice_document_filename)
    temp_file = None

    def generate_invoice_number(self, update: bool = False):
        number_format = get_invoice_customization("invoice_number_format", "{:04d}")
        current_number = 0
        try:
            current_number = int(get_invoice_customization("invoice_number_current", "0"))
        except ValueError:
            pass
        current_number += 1
        if update:
            Customization.objects.update_or_create(
                name="invoice_number_current", defaults={"value": str(current_number)}
            )
        return number_format.format(current_number)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number(True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("invoice", kwargs={"invoice_id": self.id})

    def filename(self):
        return os.path.basename(self.file.name)

    def filename_for_zip(self):
        ext = os.path.splitext(self.filename())[1]
        month = self.created_date.strftime("%B")
        year = self.created_date.strftime("%Y")
        name = slugify(self.project_details.name)
        return f"{name}/{name}-{month}-{year}-{slugify(self.invoice_number)}." + ext

    def _email_invoice(self, template_name) -> bool:
        attachment = create_email_attachment(self.file, self.filename())
        sent = render_and_send_email(
            template_name,
            {"invoice": self},
            to=self.project_details.email_to(),
            from_email=self.configuration.email_from,
            cc=self.configuration.email_cc,
            attachments=[attachment],
        )
        return bool(sent)

    def send(self) -> bool:
        # Email the invoice. If it was already sent, don't change the due date
        if not self.voided_date and self.reviewed_date:
            self.last_sent_date = timezone.now()
            if not self.sent_date:
                self.sent_date = timezone.now()
                self.due_date = timezone.now() + timedelta(days=self.configuration.invoice_due_in)
            if self._email_invoice("invoices/email/email_send_invoice"):
                self.save()
                return True
        return False

    def send_reminder(self) -> bool:
        if self.sent_date:
            if self.total_payments_received() < self.total_amount:
                # Invoice hasn't been paid in full, reminder should be sent
                self.last_reminder_sent_date = timezone.now()
                if self._email_invoice("invoices/email/email_send_invoice_reminder"):
                    self.save()
                    return True
        return False

    def sorted_core_facilities(self):
        core_facilities = list(self.invoicedetailitem_set.values_list("core_facility", flat=True).distinct())
        core_facilities.sort(key=lambda x: x if x else "", reverse=True)
        return core_facilities

    def summary_dict(self) -> Dict[str, List]:
        summary_details = {}
        for core_facility in self.sorted_core_facilities():
            summary_details.setdefault(core_facility, self.invoicesummaryitem_set.filter(core_facility=core_facility))
        summary_details.setdefault(None, self.invoicesummaryitem_set.filter(core_facility=None))
        return summary_details

    def details_dict(self) -> Dict[str, Dict[str, List]]:
        details = {}
        for core_facility in self.sorted_core_facilities():
            details.setdefault(core_facility, {})
            core_facility_items = details.get(core_facility)
            core_facility_items.setdefault("tool_usage", self.tool_usage_details(core_facility=core_facility))
            core_facility_items.setdefault("area_access", self.area_access_details(core_facility=core_facility))
            core_facility_items.setdefault("staff_charges", self.staff_charge_details(core_facility=core_facility))
            core_facility_items.setdefault(
                "consumable_withdrawals", self.consumable_withdrawal_details(core_facility=core_facility)
            )
            core_facility_items.setdefault("trainings", self.training_details(core_facility=core_facility))
            core_facility_items.setdefault(
                "missed_reservations", self.missed_reservation_details(core_facility=core_facility)
            )
            core_facility_items.setdefault("custom_charges", self.custom_charges_details(core_facility=core_facility))
        return details

    def tool_usage_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.TOOL_USAGE
        ).order_by("start")

    def area_access_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.AREA_ACCESS
        ).order_by("start")

    def staff_charge_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.STAFF_CHARGE
        )

    def consumable_withdrawal_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.CONSUMABLE
        ).order_by("start")

    def training_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.TRAINING
        ).order_by("start")

    def missed_reservation_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.MISSED_RESERVATION
        ).order_by("start")

    def custom_charges_details(self, core_facility: CoreFacility):
        return self.invoicedetailitem_set.filter(
            core_facility=core_facility, item_type=InvoiceDetailItem.InvoiceDetailItemType.CUSTOM_CHARGE
        ).order_by("start")

    def total_amount_display(self) -> str:
        return display_amount(self.total_amount, self.configuration)

    def total_payments_received(self) -> Decimal:
        return self.invoicepayment_set.aggregate(
            total_received=Coalesce(
                Sum(Case(When(payment_received__isnull=False, then="amount"), output_field=DecimalField(), default=0)),
                0,
            )
        )["total_received"]

    def total_payments_processed(self) -> Decimal:
        return self.invoicepayment_set.aggregate(
            total_processed=Coalesce(
                Sum(Case(When(payment_processed__isnull=False, then="amount"), output_field=DecimalField(), default=0)),
                0,
            )
        )["total_processed"]

    def total_outstanding_amount(self) -> Decimal:
        return self.total_amount - self.total_payments_received()

    def total_outstanding_display(self) -> str:
        return display_amount(self.total_outstanding_amount(), self.configuration)

    def total_payments_display(self) -> str:
        pending_display = f" ({display_amount(self.total_payments_received()-self.total_payments_processed(), self.configuration)} pending)"
        return f"{self.total_outstanding_display()}{pending_display}"

    def tax_display(self) -> str:
        return display_amount(
            self.invoicesummaryitem_set.aggregate(
                total_tax=Coalesce(
                    Sum(
                        Case(
                            When(summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX, then="amount"),
                            output_field=DecimalField(),
                            default=0,
                        )
                    ),
                    0,
                )
            )["total_tax"],
            self.configuration,
        )

    def facilities_subtotals(self) -> Dict:
        result = {}
        # We are creating subtotals for all facilities, and None which correspond to general charges
        facility_names = [facility.name for facility in CoreFacility.objects.all()] + [None]
        for facility_name in facility_names:
            result[facility_name] = display_amount(Decimal(0), self.configuration)
            try:
                facility_subtotal = self.invoicesummaryitem_set.get(
                    core_facility=facility_name, summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.SUBTOTAL
                )
                result[facility_name] = facility_subtotal.amount_display()
            except InvoiceSummaryItem.DoesNotExist:
                pass
        return result

    def __str__(self):
        created_date = f" ({self.created_date.date()})" if self.created_date else ""
        return f"{self.invoice_number}: {self.project_details.name}{created_date}"

    class Meta:
        ordering = ["-created_date", "-invoice_number"]


class InvoiceDetailItem(models.Model):
    class InvoiceDetailItemType(object):
        TOOL_USAGE = 1
        AREA_ACCESS = 2
        CONSUMABLE = 3
        MISSED_RESERVATION = 4
        STAFF_CHARGE = 5
        TRAINING = 6
        CUSTOM_CHARGE = 7
        choices = (
            (TOOL_USAGE, "tool_usage"),
            (AREA_ACCESS, "area_access"),
            (CONSUMABLE, "consumable"),
            (MISSED_RESERVATION, "missed_reservation"),
            (STAFF_CHARGE, "staff_charge"),
            (TRAINING, "training_session"),
            (CUSTOM_CHARGE, "custom_charge"),
        )

        @classmethod
        def is_time_type(cls, item_type):
            return item_type in [
                InvoiceDetailItem.InvoiceDetailItemType.TOOL_USAGE,
                InvoiceDetailItem.InvoiceDetailItemType.AREA_ACCESS,
                InvoiceDetailItem.InvoiceDetailItemType.TRAINING,
                InvoiceDetailItem.InvoiceDetailItemType.STAFF_CHARGE,
            ]

        @classmethod
        def category_name_for_item_type(cls, item_type):
            from NEMO_billing.invoices.invoice_generator import invoice_generator_class

            return invoice_generator_class.get_invoice_data_processor().category_name_for_item_type(item_type)

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    core_facility = models.CharField(null=True, blank=True, max_length=255)
    item_type = models.IntegerField(choices=InvoiceDetailItemType.choices)
    name = models.CharField(max_length=255)
    quantity = models.DecimalField(decimal_places=2, max_digits=8)
    start = models.DateTimeField()
    end = models.DateTimeField()
    user = models.CharField(max_length=200)
    rate = models.CharField(null=True, blank=True, max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=14)

    def quantity_display(self):
        quantity = f"{self.quantity:.2f}"
        if self.InvoiceDetailItemType.is_time_type(self.item_type):
            return f"{quantity} min"
        else:
            return quantity

    def amount_display(self):
        return display_amount(self.amount, self.invoice.configuration)


class InvoiceSummaryItem(models.Model):
    class InvoiceSummaryItemType(object):
        ITEM = 1  # Any billable summary item
        SUBTOTAL = 2  # Facility subtotal (sum of billable summary item minus discounts)
        DISCOUNT_SUBTOTAL = 3  # Facility amount for discount (only used to calculate future accumulation discounts)
        DISCOUNT = 4  # Facility discount
        TAX = 5  # Tax
        OTHER = 6  # Other
        choices = (
            (ITEM, "item"),
            (SUBTOTAL, "sub_total"),
            (DISCOUNT_SUBTOTAL, "discount_sub_total"),
            (DISCOUNT, "discount"),
            (TAX, "tax"),
            (OTHER, "other"),
        )

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    summary_item_type = models.IntegerField(choices=InvoiceSummaryItemType.choices)
    item_type = models.IntegerField(null=True, blank=True, choices=InvoiceDetailItem.InvoiceDetailItemType.choices)
    core_facility = models.CharField(null=True, blank=True, max_length=255)
    name = models.CharField(max_length=255)
    details = models.CharField(null=True, blank=True, max_length=100)
    amount = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=14)

    def amount_display(self):
        return display_amount(self.amount, self.invoice.configuration)

    def category_name_for_item_type(self):
        return InvoiceDetailItem.InvoiceDetailItemType.category_name_for_item_type(self.item_type)


class InvoicePayment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    payment_received = models.DateField(help_text="Date when payment was received")
    payment_processed = models.DateField(null=True, blank=True, help_text="Date when payment was processed")
    amount = models.DecimalField(decimal_places=2, max_digits=14, help_text="Amount received")
    note = models.CharField(null=True, blank=True, max_length=255, help_text="Payment note")
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="payment_created_by_set", on_delete=models.PROTECT)
    updated_date = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, related_name="payment_updated_by_set", on_delete=models.PROTECT)

    def amount_display(self):
        return display_amount(self.amount, self.invoice.configuration)

    def __str__(self):
        return f"Payment for invoice {self.invoice.invoice_number}"

    class Meta:
        ordering = ["-payment_received"]


def get_invoice_customization(name, default_value=None):
    try:
        return Customization.objects.get(name=name).value
    except Customization.DoesNotExist:
        return default_value
