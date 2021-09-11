from NEMO.admin import ProjectAdmin
from NEMO.models import Project
from django.contrib import admin
from django.contrib.admin import register, SimpleListFilter

from NEMO_billing.invoices.models import (
    Invoice,
    InvoiceConfiguration,
    ProjectBillingDetails,
    InvoicePayment,
    InvoiceSummaryItem,
    InvoiceDetailItem,
)
from NEMO_billing.invoices.views.invoices import zip_response, review_invoice, void_invoice, send_invoice


def clone_configuration(configuration: InvoiceConfiguration):
    """
    Create a clone of selected configurations and save them.

    :param configuration:
    :return: Newly cloned configuration
    """
    configuration.pk = None
    configuration.name = f"Copy of {configuration.name}"
    configuration.save()

    return configuration


def clone_configurations(modeladmin, request, queryset):
    for configuration in queryset.all():
        clone_configuration(configuration)


clone_configurations.short_description = "Clone selected Configurations"


def email_invoices(modeladmin, request, queryset):
    for invoice in queryset.all():
        send_invoice(request, invoice.id)


email_invoices.short_description = "Email selected invoices to customers"


def review_invoices(modeladmin, request, queryset):
    for invoice in queryset.all():
        review_invoice(request, invoice.id)


review_invoices.short_description = "Mark selected invoices as reviewed"


def void_invoices(modeladmin, request, queryset):
    for invoice in queryset.all():
        void_invoice(request, invoice.id)


void_invoices.short_description = "Mark selected invoices as void"


def zip_invoices(modeladmin, request, queryset):
    return zip_response(request, queryset.all())


zip_invoices.short_description = "Download selected invoices"


class InvoiceSummaryItemInline(admin.TabularInline):
    model = InvoiceSummaryItem
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InvoiceDetailItemInline(admin.TabularInline):
    model = InvoiceDetailItem
    can_delete = False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class InvoiceStatusFilter(SimpleListFilter):
    title = "status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            ("unsent-reviewed", "Reviewed, not sent"),
            ("sent", "Sent"),
            ("unsent", "Not sent"),
            ("reviewed", "Reviewed"),
            ("unreviewed", "Not reviewed"),
            ("voided", "Voided"),
        ]

    def queryset(self, request, queryset):
        new_queryset = Invoice.objects.filter(voided_date=None)
        if self.value() in ["unsent-reviewed", "unsent"]:
            new_queryset = new_queryset.filter(sent_date=None)
        if self.value() in ["reviewed", "unsent-reviewed"]:
            new_queryset = new_queryset.filter(reviewed_date__isnull=False)
        if self.value() == "sent":
            new_queryset = new_queryset.filter(sent_date__isnull=False)
        if self.value() == "unreviewed":
            new_queryset = new_queryset.filter(reviewed_date=None)
        if self.value() == "voided":
            new_queryset = Invoice.objects.filter(voided_date__isnull=False)
        return new_queryset


@register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = (InvoiceSummaryItemInline, InvoiceDetailItemInline)
    list_display = (
        "invoice_number",
        "get_total_amount_currency",
        "get_tax_display",
        "project_details",
        "configuration",
        "created_date",
        "due_date",
        "last_sent_date",
        "reviewed_date",
        "voided_date",
        "file",
    )
    list_filter = (InvoiceStatusFilter, "due_date", "configuration__currency")
    ordering = ("-invoice_number",)
    readonly_fields = ("created_by", "created_date")
    actions = (email_invoices, review_invoices, void_invoices, zip_invoices)

    def get_total_amount_currency(self, obj: Invoice):
        return obj.total_amount_display()

    get_total_amount_currency.admin_order_field = "total_amount"
    get_total_amount_currency.short_description = "Amount"

    def get_tax_display(self, obj: Invoice):
        return obj.tax_display()

    get_tax_display.short_description = "Tax"


@register(InvoiceConfiguration)
class InvoiceConfigurationAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "merchant_name", "currency")
    ordering = ("name",)
    actions = (clone_configurations,)
    fieldsets = (
        (None, {"fields": ("name", "invoice_due_in", "detailed_invoice")}),
        ("Communication", {"fields": ("email_from", "email_cc", "reminder_frequency")}),
        ("Merchant info", {"fields": ("merchant_name", "merchant_details", "merchant_logo", "terms")}),
        ("Currency", {"fields": ("currency", "currency_symbol")}),
        ("Tax", {"fields": ("tax_name", "tax")}),
        (
            "Display charges",
            {
                "fields": (
                    "separate_tool_usage_charges",
                    "separate_area_access_charges",
                    "separate_staff_charges",
                    "separate_consumable_charges",
                    "separate_missed_reservation_charges",
                    "separate_training_charges",
                    "separate_custom_charges",
                )
            },
        ),
    )


@register(InvoicePayment)
class InvoicePaymentAdmin(admin.ModelAdmin):
    readonly_fields = ("created_by", "created_date", "updated_by", "updated_date")
    list_display = ("invoice", "payment_received", "payment_processed", "updated_by", "updated_date")
    list_filter = ("invoice", "invoice__project_details__project__name")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        obj.save()


class ProjectBillingDetailsInline(admin.StackedInline):
    model = ProjectBillingDetails
    can_delete = False
    verbose_name_plural = "details"


class NewProjectAdmin(ProjectAdmin):
    inlines = (ProjectBillingDetailsInline,)


# Re-register ProjectAdmin
admin.site.unregister(Project)
admin.site.register(Project, NewProjectAdmin)
