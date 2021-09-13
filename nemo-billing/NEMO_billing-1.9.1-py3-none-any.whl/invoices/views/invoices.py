import io
import zipfile
from datetime import datetime
from decimal import Decimal
from typing import List

from NEMO.models import Project
from NEMO.tasks import synchronized
from NEMO.utilities import month_list
from NEMO.views.pagination import SortedPaginator
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import F, Sum, Case, When, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.formats import date_format
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET, require_POST

from NEMO_billing.invoices.exceptions import (
    NoRateSetException,
    NoProjectDetailsSetException,
    InvoiceAlreadyExistException,
    InvoiceItemsNotInFacilityException,
)
from NEMO_billing.invoices.invoice_generator import generate_monthly_invoice
from NEMO_billing.invoices.models import Invoice, InvoiceConfiguration, InvoicePayment, InvoiceSummaryItem
from NEMO_billing.models import CoreFacility


@staff_member_required(login_url=None)
@require_GET
def invoices(request):

    # Add outstanding balance and total tax that will be sortable columns
    invoice_list = (
        Invoice.objects.filter(voided_date=None)
        .annotate(outstanding=F("total_amount") - Coalesce(Sum("invoicepayment__amount"), 0))
        .annotate(
            total_tax=Sum(
                Case(
                    When(
                        invoicesummaryitem__summary_item_type=InvoiceSummaryItem.InvoiceSummaryItemType.TAX,
                        then=F("invoicesummaryitem__amount"),
                    ),
                    output_field=DecimalField(),
                    default=0,
                )
            )
        )
    )

    page = SortedPaginator(invoice_list, request, order_by="-created_date").get_current_page()

    core_facilities = CoreFacility.objects.all()

    return render(
        request,
        "invoices/invoices.html",
        {
            "page": page,
            "month_list": month_list(since=settings.INVOICE_MONTH_LIST_SINCE),
            "projects": Project.objects.filter(active=True).order_by("account__name"),
            "configuration_list": InvoiceConfiguration.objects.all(),
            "invoices_search": Invoice.objects.all(),
            "core_facilities": core_facilities,
            "display_general_facility": not core_facilities.exists()
            or not settings.INVOICE_ALL_ITEMS_MUST_BE_IN_FACILITY,
        },
    )


@staff_member_required(login_url=None)
@require_POST
@synchronized()
def generate_monthly_invoices(request):
    try:
        project_id = request.POST["project_id"]
        configuration_id = request.POST["configuration_id"]
        configuration = get_object_or_404(InvoiceConfiguration, id=configuration_id)
        if project_id == "All":
            for project in Project.objects.filter(active=True):
                generate_monthly_invoice(request.POST["month"], project, configuration, request.user)
        else:
            project = get_object_or_404(Project, id=project_id)
            invoice = generate_monthly_invoice(request.POST["month"], project, configuration, request.user, True)
            if not invoice:
                messages.warning(request, f"No billable items were found for project: {project}")
    except NoProjectDetailsSetException as e:
        link = reverse("project", args=[e.project.id])
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to add some."
        messages.error(request, mark_safe(message))
    except NoRateSetException as e:
        link = reverse("rates")
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to create one."
        messages.error(request, mark_safe(message))
    except InvoiceAlreadyExistException as e:
        link = reverse("view_invoice", args=[e.invoice.id])
        message = "Invoice generation failed: " + e.msg + f" - click <a href='{link}'>here</a> to view it."
        messages.error(request, mark_safe(message))
    except InvoiceItemsNotInFacilityException as e:
        messages.error(request, e.msg)
    return redirect("invoices")


@staff_member_required(login_url=None)
@require_GET
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(
        request, "invoices/invoice.html", {"invoice": invoice, "core_facilities": CoreFacility.objects.exists()}
    )


@staff_member_required(login_url=None)
@require_POST
def review_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if not invoice.reviewed_date:
        invoice.reviewed_date = timezone.now()
        invoice.reviewed_by = request.user
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} was successfully marked as reviewed.")
    else:
        messages.error(request, f"Invoice {invoice.invoice_number} has already been reviewed.")
    return redirect("view_invoice", invoice_id=invoice_id)


@staff_member_required(login_url=None)
@require_POST
def send_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if invoice.reviewed_date:
        if not invoice.project_details.email_to():
            link = reverse("project", args=[invoice.project_details.project.id])
            messages.error(
                request,
                mark_safe(
                    f"Invoice {invoice.invoice_number} could not sent because no email is set on the project - click <a href='{link}'>here</a> to add some"
                ),
            )
        else:
            sent = invoice.send()
            if sent:
                messages.success(request, f"Invoice {invoice.invoice_number} was successfully sent.")
            else:
                messages.error(request, f"Invoice {invoice.invoice_number} could not be sent.")
    else:
        messages.error(request, f"Invoice {invoice.invoice_number} needs to be reviewed before sending.")
    return redirect("view_invoice", invoice_id=invoice_id)


@staff_member_required(login_url=None)
@require_POST
def void_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if not invoice.voided_date:
        invoice.voided_date = timezone.now()
        invoice.voided_by = request.user
        invoice.save()
        messages.success(request, f"Invoice {invoice.invoice_number} was successfully marked as void.")
    else:
        messages.error(request, f"Invoice {invoice.invoice_number} is already void.")
    return redirect("view_invoice", invoice_id=invoice_id)


@staff_member_required(login_url=None)
@require_POST
def zip_invoices(request):
    invoice_ids: List[str] = request.POST.getlist("selected_invoice_id[]")
    if not invoice_ids:
        return redirect("invoices")
    else:
        return zip_response(request, Invoice.objects.filter(id__in=invoice_ids))


@staff_member_required(login_url=None)
@require_POST
def invoice_payment_received(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    payment = InvoicePayment()
    payment.invoice = invoice
    payment.created_by = request.user
    payment.updated_by = request.user
    payment.payment_received = datetime.strptime(request.POST["payment_received_date"], "%m/%d/%Y")
    payment.amount = Decimal(request.POST["payment_received_amount"])
    payment.save()
    messages.success(
        request,
        f"The payment of {payment.amount_display()} for invoice {invoice.invoice_number} was marked as received on {date_format(payment.payment_received)}.",
    )
    return redirect("view_invoice", invoice_id=invoice_id)


@staff_member_required(login_url=None)
@require_POST
def invoice_payment_processed(request, payment_id):
    payment = get_object_or_404(InvoicePayment, id=payment_id)
    payment.updated_by = request.user
    payment.payment_processed = datetime.strptime(request.POST["payment_processed_date"], "%m/%d/%Y")
    payment.save()
    messages.success(
        request,
        f"The payment of {payment.amount_display()} for invoice {payment.invoice.invoice_number} was marked as processed on {date_format(payment.payment_processed)}.",
    )
    return redirect("view_invoice", invoice_id=payment.invoice_id)


@login_required
@require_GET
@permission_required("NEMO.trigger_timed_services", raise_exception=True)
def send_invoice_payment_reminder(request):
    return do_send_invoice_payment_reminder()


def do_send_invoice_payment_reminder():
    today = timezone.now()
    unpaid_invoices = Invoice.objects.filter(due_date__lte=today, voided_date=None)
    for unpaid_invoice in unpaid_invoices:
        if unpaid_invoice.total_outstanding_amount() > Decimal(0):
            if not unpaid_invoice.last_reminder_sent_date:
                unpaid_invoice.send_reminder()
            else:
                # Check days since last reminder sent
                time_diff = today - unpaid_invoice.last_reminder_sent_date
                too_long_since_last = (
                    unpaid_invoice.configuration.reminder_frequency
                    and time_diff.days >= unpaid_invoice.configuration.reminder_frequency
                )
                # Send reminder if none has been sent yet, or if it's been too long
                if too_long_since_last:
                    unpaid_invoice.send_reminder()
    return HttpResponse()


def zip_response(request, invoice_list: List[Invoice]):
    generated_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    parent_folder_name = f"invoices_{generated_date}"
    zip_io = io.BytesIO()
    with zipfile.ZipFile(zip_io, mode="w", compression=zipfile.ZIP_DEFLATED) as backup_zip:
        for invoice in invoice_list:
            if invoice.file:
                backup_zip.write(invoice.file.path, f"{parent_folder_name}/" + invoice.filename_for_zip())
    response = HttpResponse(zip_io.getvalue(), content_type="application/x-zip-compressed")
    response["Content-Disposition"] = "attachment; filename=%s" % parent_folder_name + ".zip"
    response["Content-Length"] = zip_io.tell()
    return response
