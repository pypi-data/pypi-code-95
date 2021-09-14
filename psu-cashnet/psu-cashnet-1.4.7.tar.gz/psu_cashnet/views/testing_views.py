from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.conf import settings
from psu_base.classes.Log import Log
from psu_base.services import utility_service, error_service, message_service
from psu_base.decorators import (
    require_authority,
    require_authentication,
    require_non_production,
)
from psu_cashnet.models.catalog import CatalogItem
from psu_cashnet.services import transaction_service
from decimal import Decimal

log = Log()

# A limited set of responses to respond with
cn_response_options = {
    "0": "SUCCESS",
    "902": "Customer Cancelled before processing payment",
    "232": "AVS FAIL. For security reasons, we cannot accept your credit card",
    "7": "Invalid expiration date, no expiration date provided",
}


@require_non_production()
@require_authentication()
def test_transaction_form(request):
    """
    Create a test transaction
    """
    log.trace()
    catalog_items = CatalogItem.objects.all()
    log.end("infotext/index")
    return render(
        request, "cashnet/test/fake_transaction_form.html", {"catalog_items": catalog_items}
    )


@require_non_production()
@require_authentication()
def test_transaction_response(request):
    """
    Create a test transaction
    """
    log.trace()
    if request.method != "POST":
        return redirect("test_form")

    # Gather form parameters
    merchant_code = request.POST.get("merchant_code")
    reference_class = request.POST.get("reference_class")
    reference_id = request.POST.get("reference_id")
    secret_key = request.POST.get("secret_key")
    success_url = request.POST.get("success_url")
    failure_url = request.POST.get("failure_url")
    term_code = request.POST.get("term_code")
    # Get requested items and quantities
    requested_items = []
    for kk, vv in request.POST.items():
        if kk.startswith("item_id_"):
            qty = request.POST.get(f"qty_{vv}")
            if qty and int(qty) > 1:
                requested_items.append((vv, int(qty)))
            else:
                requested_items.append(vv)

    # catalog_items = CatalogItem.objects.filter(id__in=requested_items)

    tx = transaction_service.create_transaction(
        requested_items=requested_items,
        success_url=success_url,
        failure_url=failure_url,
        merchant_code=merchant_code,
        reference_class=reference_class,
        reference_id=reference_id,
        secret_key=secret_key,
        term_code=term_code,
    )
    if tx:
        return transaction_service.cashnet_redirect(tx)
    else:
        return redirect("cashnet:test_form")


@require_non_production()
@require_authentication()
def cn_fake_site(request, tx_id):

    # Gather Items from parameters (not from transaction instance)
    items = []
    ii = 0
    while ii < 100:
        ii += 1
        item_code = request.GET.get(f"itemcode{ii}")
        if item_code:
            amount = request.GET.get(f"amount{ii}")
            amount = Decimal(amount if amount else None)
            items.append({"itemcode": item_code, "amount": amount})
        else:
            break

    # In stage, allow user to link to Train site
    train_url = None
    if not utility_service.is_development():
        tx = transaction_service.get_transaction(tx_id)
        train_url = tx.cashnet_url(force_train=True) if tx else None

    # Display payment form
    return render(
        request,
        "cashnet/test/fake_cashnet_site.html",
        {
            "ref1type1": request.GET.get("ref1type1"),
            "ref1val1": request.GET.get("ref1val1"),
            "custcode": request.GET.get("custcode"),
            "fname": request.GET.get("fname"),
            "lname": request.GET.get("lname"),
            "email": request.GET.get("email"),
            "items": items,
            "cn_response_options": cn_response_options,
            "train_url": train_url,
        },
    )


def fake_success(request):
    tx = transaction_service.get_processed_transaction()
    if not tx:
        message_service.post_error(
            "Transaction not found. This would happen if you refreshed the page."
        )
        return redirect("cashnet:error")
    tx.set_post_processing_status("Completed")
    tx.save()
    return render(request, "cashnet/test/fake_tx_success.html", {"tx": tx})


def fake_failure(request):
    tx = transaction_service.get_processed_transaction()
    if not tx:
        message_service.post_error(
            "Transaction not found. This would happen if you refreshed the page."
        )
        return redirect("cashnet:error")
    tx.set_post_processing_status("Not Required")
    tx.save()
    return render(request, "cashnet/test/fake_tx_failure.html", {"tx": tx})
