from typing import List

from NEMO.models import Project
from NEMO.views.api_billing import BillingFilterForm, date_time_format
from django.utils import timezone
from drf_renderer_xlsx.mixins import XLSXFileMixin
from rest_framework import status
from rest_framework.fields import CharField, IntegerField, DateTimeField, DecimalField
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import GenericViewSet

from NEMO_billing.invoices.invoice_generator import invoice_generator_class
from NEMO_billing.invoices.models import InvoiceDetailItem, Invoice, InvoiceConfiguration

date_time_format_export = "%m_%d_%Y-%H_%M_%S"


class BillingDataSerializer(Serializer):
    item_type = CharField(source="get_item_type_display")
    core_facility = CharField(max_length=200, read_only=True)
    name = CharField(max_length=200, read_only=True)
    account = CharField(max_length=200, read_only=True)
    account_id = IntegerField(read_only=True)
    project = CharField(max_length=200, read_only=True)
    project_id = IntegerField(read_only=True)
    reference_po = CharField(max_length=200, read_only=True)
    user = CharField(max_length=255, read_only=True)
    start = DateTimeField(read_only=True)
    end = DateTimeField(read_only=True)
    quantity = DecimalField(read_only=True, decimal_places=2, max_digits=8)
    rate = CharField(max_length=200, read_only=True)
    amount = DecimalField(read_only=True, decimal_places=2, max_digits=14)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        fields = "__all__"


class BillingDataViewSet(XLSXFileMixin, GenericViewSet):
    serializer_class = BillingDataSerializer

    def list(self, request, *args, **kwargs):
        billing_form = BillingFilterForm(self.request.GET)
        if not billing_form.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=billing_form.errors)
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        billing_form = BillingFilterForm(self.request.GET)
        billing_form.full_clean()

        queryset = Project.objects.filter()
        start, end = billing_form.get_start_date(), billing_form.get_end_date()
        if billing_form.get_account_id():
            queryset = queryset.filter(account_id=billing_form.get_account_id())
        if billing_form.get_account_name():
            queryset = queryset.filter(account__name=billing_form.get_account_name())
        if billing_form.get_project_id():
            queryset = queryset.filter(id=billing_form.get_project_id())
        if billing_form.get_project_name():
            queryset = queryset.filter(name=billing_form.get_project_name())
        if billing_form.get_application_name():
            queryset = queryset.filter(application_identifier=billing_form.get_application_name())

        data_processor = invoice_generator_class.get_invoice_data_processor()
        detail_items: List[InvoiceDetailItem] = []
        for project in queryset:
            invoice = Invoice(start=start, end=end, project_details=project.projectbillingdetails)
            invoice.configuration = InvoiceConfiguration()
            invoice.configuration.currency = ""
            detail_items.extend(add_prj_acct_info(data_processor.tool_usages_invoice_details(invoice), project))
            detail_items.extend(add_prj_acct_info(data_processor.area_access_records_invoice_details(invoice), project))
            detail_items.extend(add_prj_acct_info(data_processor.missed_reservations_invoice_details(invoice), project))
            detail_items.extend(add_prj_acct_info(data_processor.staff_charges_invoice_details(invoice), project))
            detail_items.extend(
                add_prj_acct_info(data_processor.consumable_withdrawals_invoice_details(invoice), project)
            )
            detail_items.extend(add_prj_acct_info(data_processor.training_sessions_invoice_details(invoice), project))
            detail_items.extend(add_prj_acct_info(data_processor.custom_charges_invoice_details(invoice), project))

        detail_items.sort(key=lambda x: x.start, reverse=True)
        return detail_items

    def get_filename(self):
        return f"billing-{timezone.localtime().strftime(date_time_format_export)}.xlsx"


def add_prj_acct_info(detail_items: List[InvoiceDetailItem], project: Project):
    for detail_item in detail_items:
        detail_item.project = project.name
        detail_item.project_id = project.id
        detail_item.account = project.account.name
        detail_item.account_id = project.account.id
        detail_item.reference_po = project.application_identifier
    return detail_items
