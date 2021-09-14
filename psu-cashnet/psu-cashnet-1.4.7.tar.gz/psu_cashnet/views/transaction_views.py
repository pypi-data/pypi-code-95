from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from psu_base.classes.Log import Log
from psu_base.models.audit import Audit
from psu_base.services import (
    utility_service,
    error_service,
    auth_service,
    message_service,
)
from psu_base.decorators import require_authority, require_authentication
from psu_cashnet.models.transaction import Transaction
from psu_cashnet.services import transaction_service
from django.core.paginator import Paginator
from django.db.models import Q
import re
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from psu_cashnet import cn_admin_roles

log = Log()


# Cashnet Error Page
# (template can be overridden at the app level)
def cn_error_page(request):
    auth_service.audit_event(
        "ERROR_PAGE", comments=f"Customer directed to Cashnet error page"
    )
    return render(request, "cashnet/cn_error.html", {})


# Recording of the Cashnet response should NOT require authentication
# Since the POST is coming from Cashnet, CSRF would fail
@method_decorator(csrf_exempt, name="dispatch")
def cn_record_response(request):
    """Record the response from cashnet"""
    tx = transaction_service.record_cashnet_response(request)
    if tx and tx.is_recorded():
        return redirect("cashnet:validation", tx.id)
    else:
        return redirect("cashnet:error")


@require_authentication()
def cn_validate_response(request, tx_id=None, tx_content=None):
    """
    Handle a response from Cashnet
    """
    log.trace([tx_id, tx_content])
    if tx_content and not tx_id:
        if '|' in tx_content:
            try:
                tx_id = tx_content.split('|')[0]
            except Exception as ee:
                log.info(f"Unable to get tx_id from tx_content: {ee}")

    tx = transaction_service.confirm_cashnet_response(tx_id)
    log.info(f"Confirmed response: {tx}")

    # If valid transaction (success or failure)
    if tx and tx.was_processed():
        transaction_service.set_processed_transaction(tx)
        if tx.was_successful():
            return redirect(tx.success_url)
        else:
            return redirect(tx.failure_url)

    # Otherwise, send to error page
    else:
        return redirect("cashnet:error")


@require_authority(cn_admin_roles)
def cn_admin_update_tx(request, tx_id, status):

    tx = get_object_or_404(Transaction, pk=tx_id)
    status_code = status.strip()[:1].upper() if status else None

    # Since this action will fire off post-payment processing, user must be proxying the customer
    auth = auth_service.get_auth_object()
    current_user = auth.get_user()
    proxied_user = auth.proxied_user if auth.is_proxying() else None

    # User may not update their own transaction
    if tx.customer_username == current_user.username:
        message_service.post_error("You may not update your own transaction status")
        return redirect("cashnet:transaction_detail", tx.id)

    elif (not proxied_user) or proxied_user.username != tx.customer_username:
        message_service.post_error(
            "You must be proxying the customer when you update their transaction status."
        )
        return redirect("cashnet:transaction_detail", tx.id)

    if tx and status_code in ["S", "F"]:
        auth_service.audit_event(
            "UPDATE_CASHNET_STATUS",
            previous_value=tx.status_code,
            new_value=status_code,
            reference_code="psu_cashnet.Transaction",
            reference_id=tx.id,
            comments=f"{tx}",
        )

        tx.status_code = status_code
        tx.admin_updated = current_user.username
        tx.admin_updated_date = datetime.now()
        tx.save()
        transaction_service.set_processed_transaction(tx)

        if tx.was_successful():
            return redirect(tx.success_url)
        else:
            return redirect(tx.failure_url)

    message_service.post_error("Invalid transaction or status was provided.")
    return redirect("cashnet:transaction_detail", tx.id)


@require_authority(cn_admin_roles)
def cn_admin_change_tx_status(request, tx_id):
    tx = Transaction.get(tx_id)
    status_code = request.POST.get('status')
    if tx and status_code and status_code in tx.status_options:
        if not tx.status_can_be_updated:
            message_service.post_error("This transaction's status cannot be updated.")
        else:
            old_status = tx.status_code
            tx.status_code = status_code
            tx.save()
            message_service.post_success("Transaction status has been updated.")

            auth_service.audit_event(
                "UPDATE_CASHNET_STATUS",
                previous_value=old_status,
                new_value=status_code,
                reference_code="psu_cashnet.Transaction",
                reference_id=tx.id,
                comments=f"{tx} - No Post-Processing",
            )
    else:
        message_service.post_error("Invalid transaction or status selection.")

    return redirect("cashnet:transaction_detail", tx.id)


@require_authority(cn_admin_roles)
def cn_transaction_index(request, keyword=None):
    """
    Show all transactions
    """
    log.trace()

    # If URL parameter "error" is given, and a search string not containing "error" is also given,
    # redirect to non-error list (search submitted after coming to error list)
    keyword_search = bool("keywords" in request.GET)
    search_string = request.GET.get("keywords")
    if keyword == "error" and keyword_search and "error" not in search_string:
        return redirect(
            f"{reverse('cashnet:transaction_index')}?keywords={search_string}"
        )

    # Start a query set
    transactions = Transaction.objects.all()

    # Get pagination sort and filter data
    sortby, page, kw = utility_service.pagination_sort_info(
        request, "last_updated", "desc", filter_name="keywords"
    )

    # Keyword comes from a URL parameter. kw comes from search field.
    if keyword:
        if kw and "error" not in kw:
            # Append to search string
            kw = f"{keyword} {kw}"
        elif not kw:
            # Use as search string
            kw = keyword

    if kw:
        for ww in kw.split():
            if re.match(r"^9\d{8}$", ww):
                transactions = transactions.filter(customer_psu_id=ww)
            elif re.match(r"^20[2-3]\d0[1-4]$", ww):
                transactions = transactions.filter(term_code=ww)
            elif ww.lower() in [
                "new",
                "initiated",
                "recorded",
                "processing",
                "success",
                "failure",
                "error",
            ]:
                transactions = transactions.filter(status_code=ww.upper()[:1])
            elif ":" in ww:
                pieces = ww.split(":")
                transactions = transactions.filter(reference_class__iexact=pieces[0])
                if len(pieces) > 1 and pieces[1]:
                    transactions = transactions.filter(reference_id=pieces[1])
            else:
                transactions = transactions.filter(
                    Q(customer_name__icontains=ww) | Q(customer_username=ww)
                )

    # Reference object is made of two pieces and needs a secondary sort column
    if sortby and "reference_id" in sortby[0]:
        d = "-" if "-" in sortby[0] else ""
        sortby = (sortby[0], f"{d}reference_class")

    transactions = transactions.order_by(*sortby)

    paginator = Paginator(transactions, 50)
    transactions = paginator.get_page(page)

    return render(
        request,
        "cashnet/transaction/cn_transaction_index.html",
        {"transactions": transactions, "keywords": kw},
    )


@require_authority(cn_admin_roles)
def cn_unprocessed_transactions(request):
    """
    Show all recorded successful transactions that were not processed
    """
    log.trace()

    # Get pagination sort and filter data
    sortby, page, kw = utility_service.pagination_sort_info(
        request, "last_updated", "desc", filter_name="keywords"
    )

    # Get all Recorded successful transactions
    transactions = Transaction.objects.filter(status_code='R', cashnet_result_code=0)

    # Reference object is made of two pieces and needs a secondary sort column
    if sortby and "reference_id" in sortby[0]:
        d = "-" if "-" in sortby[0] else ""
        sortby = (sortby[0], f"{d}reference_class")

    transactions = transactions.order_by(*sortby)

    paginator = Paginator(transactions, 50)
    transactions = paginator.get_page(page)

    # Get other transactions for the same related object (potential duplicate payments)
    related = {}
    if transactions:
        for tx in transactions:
            # Get other transaction for the same object (class and id)
            rel = Transaction.objects.filter(reference_class=tx.reference_class, reference_id=tx.reference_id, cashnet_result_code=0).exclude(id=tx.id).order_by(*sortby)
            related[tx.id] = rel

    return render(
        request,
        "cashnet/transaction/cn_transaction_index.html",
        {"transactions": transactions, "related": related},
    )


@require_authority(cn_admin_roles)
def cn_transaction_detail(request, tx_id):
    """
    Show one transaction
    """
    log.trace()

    tx = get_object_or_404(Transaction, pk=tx_id)

    # If user has both cashnet and proxy authorities, they may update the status of transactions in Error status
    can_update = (
        tx.status_can_be_updated()
        and auth_service.get_user().username != tx.customer_username
    )
    can_proxy = auth_service.has_authority("proxy")
    is_proxied = (
        auth_service.get_auth_object().proxied_user.username == tx.customer_username
    )

    # Get any audit events for this transaction
    audits = Audit.objects.filter(reference_code="psu_cashnet.Transaction", reference_id=tx.id).order_by('date_created')


    return render(
        request,
        "cashnet/transaction/cn_transaction_detail.html",
        {
            "tx": tx,
            "can_update": can_update,
            "can_proxy": can_proxy,
            "is_proxied": is_proxied,
            "audits": audits,
        },
    )
