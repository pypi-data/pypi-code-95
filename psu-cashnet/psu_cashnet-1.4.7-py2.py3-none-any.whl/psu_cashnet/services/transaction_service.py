from psu_base.services import utility_service, auth_service, error_service
from django.db.models.query import QuerySet
from django.urls import reverse
from psu_base.classes.Log import Log
from psu_cashnet.models.transaction import Transaction
from psu_cashnet.models.purchase import PurchasedItem
from psu_cashnet.models.catalog import CatalogItem
from datetime import datetime
from psu_base.services import email_service, message_service
from decimal import Decimal
from django.shortcuts import redirect
from psu_cashnet import cn_notify_roles

log = Log()


def get_transaction(transaction_id):
    log.trace(transaction_id)
    try:
        tx = Transaction.objects.get(pk=transaction_id)
    except Transaction.DoesNotExist:
        log.warning(f"Transaction #{transaction_id} does not exist")
        tx = None
    log.end(tx)
    return tx


def get_transaction_queryset():
    return Transaction.objects.filter(app_code=utility_service.get_app_code())


def create_transaction(
    requested_items,
    success_url,
    failure_url,
    merchant_code=None,
    reference_class=None,
    reference_id=None,
    secret_key=None,
    term_code=None,
):
    # ** VALIDATION ***********************************************************
    catalog_items = []
    try:
        # If a single item was given, put it in a list (for consistency)
        if type(requested_items) not in [list, QuerySet]:
            requested_items = [requested_items]
            for ii in requested_items:
                log.info(f"Item {ii} is type {type(ii)}")

        # If IDs were given, look up the item
        invalid_items = False
        for ii in requested_items:

            # If quantity of an item is being included, it will be a tuple
            if type(ii) is tuple:
                p1 = ii[0]
                p2 = ii[1]

                # if IDs were given for the items, both pieces will be numeric.
                # this is not great, and should be avoided, but handle with logged warning
                if str(p1).isnumeric() and str(p2).isnumeric():
                    # The first number should be the qty
                    item = p1
                    qty = int(p2)
                    log.warning(
                        f"Item ID was given with quantity.  Using first number as the ID and second as qty."
                    )
                elif str(p1).isnumeric():
                    qty = int(p1)
                    item = p2
                elif str(p2).isnumeric():
                    qty = int(p2)
                    item = p1
                else:
                    error_service.record("Invalid cashnet item tuple", ii)
                    invalid_items = True
                    item = 0
                    qty = 0

            else:
                item = ii
                qty = 1

            if type(item) is CatalogItem:
                catalog_items.append((item, qty))
            else:
                ci = CatalogItem.objects.get(id=item) if item else None
                if ci:
                    catalog_items.append((ci, qty))
                else:
                    invalid_items = True
                    error_service.unexpected_error(
                        "Invalid catalog item selected.",
                        f'Could not find a valid catalog item from "{item}"',
                    )

        # All requested items must have been accounted for
        if invalid_items:
            return None

        # At least one item is required
        if not catalog_items:
            error_service.unexpected_error(
                "No catalog items were requested",
                "Attempted to create a transaction with no items",
            )
            return None

        # At least one non-percentage item is required
        np = False
        for ii in catalog_items:
            item_instance = ii[0]
            item_qty = ii[1]
            if item_instance.current_price() >= 1:
                np = True
        if not np:
            error_service.unexpected_error(
                "No catalog items were requested",
                "Attempted to create a transaction with only percentage-based items",
            )
            return None

        # Get the merchant code
        #  Most apps will have the merchant code in settings.py, but some
        #  apps may have multiple merchant codes and need to specify which to use.
        if not merchant_code:
            merchant_code = utility_service.get_setting("CASHNET_MERCHANT_CODE")

        # A merchant code is required to continue
        if not merchant_code:
            error_service.unexpected_error(
                "Unable to process the transaction.",
                "Unable to determine the Cashnet merchant code.",
            )
            return None

        # Secret key is not being used.
        # Cashnet was unable to support their digest feature in the past
        # There are post-audits in place (at the department level) to detect parameter tampering
        if secret_key:
            secret_key = None
            log.warning("Secret key feature is disabled")

        # Success and failure URLs are required
        if not success_url:
            error_service.unexpected_error(
                "Unable to process the transaction.", "No success URL was provided"
            )
            return None

        if not failure_url:
            error_service.unexpected_error(
                "Unable to process the transaction.", "No failure URL was provided"
            )
            return None

        # Get the logged in user (the customer)
        customer = auth_service.get_user()
    except Exception as ee:
        error_service.unexpected_error("Unable to validate the transaction.", ee)
        return None

    # ** CREATION *************************************************************
    try:
        # Create the transaction
        tx = Transaction()
        tx.status_code = "N"
        tx.app_code = utility_service.get_app_code()
        tx.customer_username = customer.username
        tx.customer_psu_id = customer.psu_id
        tx.customer_name = customer.display_name
        tx.merchant_code = merchant_code
        tx.secret_key = secret_key
        tx.reference_class = reference_class
        tx.reference_id = reference_id

        # Success and Failure URLs can be URLs, URL names, or tuples of (URL-name, arg1, arg2, arg3, ...)
        # Success URL
        try:
            if type(success_url) is tuple:
                tx.success_url = reverse(success_url[0], args=success_url[1:])
            else:
                tx.success_url = success_url
        except Exception as ee:
            error_service.record(ee, f"Could not resolve success_url: {success_url}")
            tx.success_url = "cashnet:error"

        # Failure URL
        try:
            if type(failure_url) is tuple:
                tx.failure_url = reverse(failure_url[0], args=failure_url[1:])
            else:
                tx.failure_url = failure_url
        except Exception as ee:
            error_service.record(ee, f"Could not resolve failure_url: {failure_url}")
            tx.success_url = "cashnet:error"

        # If a valid term code was given, add it
        if term_code and term_code.isdigit() and len(term_code) == 6:
            tx.term_code = term_code

        # Transaction must be saved before adding items
        tx.save()
    except Exception as ee:
        error_service.unexpected_error("Unable to create a new transaction.", ee)
        return None

    # ** ADD ITEMS ************************************************************
    try:
        percentages = []
        subtotal = 0
        for ii in catalog_items:
            item_instance = ii[0]
            item_qty = ii[1]

            # Items less than 1.00 are percentages
            if item_instance.current_price() < 1:
                percentages.append(ii)
                continue

            log.info(f"Adding {item_instance} of type {type(item_instance)} to {tx}")
            pi = PurchasedItem()
            pi.transaction = tx
            pi.catalog_item = item_instance
            pi.purchase_amount = item_instance.current_price()
            pi.qty = item_qty
            pi.save()
            log.info(f"Added {item_instance} to {tx}")
            subtotal += pi.purchase_amount * item_qty

        # Add percentages
        if percentages:
            # Expecting only one percentage, but do not enforce
            if len(percentages) > 1:
                log.warning(f"Adding {len(percentages)} percentage-based items")

            for ii in percentages:
                item_instance = ii[0]
                item_qty = ii[1]

                # Expecting qty of one, but do not enforce
                if item_qty > 1:
                    log.warning(f"Adding {item_qty} qty of a percentage-based fee")

                calculated_amount = subtotal * item_instance.current_price()
                pi = PurchasedItem()
                pi.transaction = tx
                pi.catalog_item = item_instance
                pi.purchase_amount = calculated_amount
                pi.qty = item_qty
                pi.save()
                log.info(f"Added {item_instance} to {tx}")

    except Exception as ee:
        error_service.unexpected_error(
            "Unable to add items to the new transaction.", ee
        )
        return None

    log.info(f"Created transaction: {tx}")
    return tx


def cashnet_redirect(tx):
    """Prepare to redirect customer to cashnet. Returns the appropriate Cashnet URL"""

    # Update the status and initiation date
    tx.status_code = "I"
    tx.initiation_date = datetime.now()
    tx.save()

    # Save tx ID in the session
    utility_service.set_session_var("cashnet_tx_id", tx.id)

    return redirect(tx.cashnet_url())


def record_cashnet_response(request):
    """
    Record Cashnet response parameters in the database
    This does not require authentication, and will be validated in a separate step

    Returns a transaction
        If successful, status_code == 'R' (Recorded)
        It is possible for status to be any legitimate status_code (if the check is duplicated)
        Also possible to be None if transaction was not found
    """
    tx = None
    try:
        # Get cashnet response parameters
        parameters = request.POST.dict()

        # Do parameters indicate success? (needs to be validated)
        result = parameters.get("result")
        payment_completed = result is not None and str(result) == "0"

        auth_service.audit_event(
            "CASHNET_RESPONSE", new_value=result, comments=f"{parameters}"
        )

        # Retrieve the transaction from database (no validation)
        tx = _retrieve_transaction_from_cn_parameters(parameters)

        # Validate the status of the retrieved transaction (does not change status)
        # valid_status can be False (invalid), None (not found), or True (valid)
        valid_status = _validate_unprocessed_tx_status(tx, payment_completed)

        # If tx in valid state, record the parameters
        if tx and valid_status:
            _update_tx_from_parameters(tx, parameters)
            # tx status is now either [R]ecorded, or [E]rror

        # If successfully recorded, return it
        if tx and tx.is_recorded():
            return tx

        # If there was an error, and the payment was potentially successful, notify someone
        elif payment_completed:
            try:
                error_service.record(
                    "Error on potentially successful transaction",
                    f"Email sent regarding transaction {f'#{tx.id}' if tx else None}",
                )

                customer = auth_service.get_user()
                if not customer:
                    psu_id = parameters.get("custcode")
                    if psu_id:
                        customer = auth_service.look_up_user_cache(psu_id)

                msg = f"""
                    Cashnet responded that the following transaction was successful, but the
                    response could not be validated.  This transaction must be manually verified.<br />
                    <br />
                    <b>Customer:</b><br />
                    {customer.display_name}<br />
                    {customer.psu_id}<br />
                    {customer.email_address}<br />
                    <br />
                """
                if tx:
                    msg += f"""
                        Web & Mobile Team Data:<br />
                        Transaction #{tx.id}<br />
                        Status: {tx.status_desc()}<br />
                        Internal Error Message: {tx.internal_error_message}<br />
                        <br />
                        <br />
                        Cashnet Data:<br />
                        Cashnet Transaction #: {tx.cashnet_transaction}<br />
                        Cashnet Batch #: {tx.cashnet_batch}<br />
                        Cashnet Response Message: {tx.cashnet_result_message}<br />
                        Cashnet Error Message: {tx.cashnet_error_message}<br />
                        <br />
                    """
                else:
                    msg += f"""
                        Cashnet Data:<br />
                        Cashnet Transaction #: {parameters.tx}<br />
                        Cashnet Batch #: {parameters.batchno}<br />
                        Cashnet Response Message: {parameters.get('respmessage')}<br />
                        Cashnet Error Message: {parameters.get('ccerrormessage')}<br />
                        <br />
                    """

                email_service.send(
                    subject=f"{utility_service.get_app_code()}: Error on potentially successful Cashnet response",
                    content=msg,
                    to=email_service.get_authorized_emails(cn_notify_roles),
                    bcc=["oit-ia-group@pdx.edu"],
                    suppress_status_messages=True,
                    email_template="cashnet/emails/safe_template.html",
                )
            except Exception as ee:
                error_service.record(ee, "Unable to notify admins of Cashnet error")

    except Exception as ee:
        error_service.record(
            ee, "Unhandled error while trying to record cashnet response"
        )

    return tx


def confirm_cashnet_response(tx_id):
    """
    After authentication, confirm that the logged in user is the customer
    """
    log.trace([tx_id])
    tx = None
    try:
        user = auth_service.get_user()
        tx = get_transaction(tx_id)

        # If this transaction ws already processed, send user to error page
        if tx and tx.was_processed():
            log.error(f"Attempting to confirm already-processed transaction: {tx}")
            return None

        # If recorded transaction does not belong to current user
        if tx and tx.customer_username != user.username:
            # In non-production, impersonation is lost when returning from training site
            if (
                utility_service.is_non_production()
                and auth_service.get_auth_object().can_impersonate()
            ):
                message_service.post_warning(
                    """
                    <span class="fa fa-user-secret"></span>
                    You are not the customer!<br>
                    <br>
                    Since this is non-prod, and you can impersonate, it is assumed that you were impersonating
                    the customer.  Impersonation may be lost during the return from Cashnet, so this identity
                    mix-up will be ignored.<br>
                    <br>
                    In production, this would not be ignored.
                    """
                )
                auth = auth_service.get_auth_object()
                if not (auth.is_proxying() or auth.is_impersonating()):
                    if auth.start_impersonating(tx.customer_username):
                        message_service.post_info(
                            "Impersonation has been automatically re-established."
                        )
                    else:
                        message_service.post_info(
                            "Unable to automatically re-establish impersonation."
                        )
            else:
                msg = f"Authenticated user ({user.username}) is not the customer"
                log.error(msg)
                tx.internal_error_message = msg
                tx.status_code = "E"
                tx.save()
                return tx

        # If recorded transaction belongs to current user (because previous condition allowed it)
        if tx and tx.is_recorded():
            payment_status = "S" if tx.cashnet_result_code == 0 else "F"
            tx.status_code = payment_status
            tx.save()
        else:
            # tx already has error info in it
            pass

    except Exception as ee:
        error_service.record(ee, f"Unable to confirm recorded transaction #{tx_id}")

    return tx


def set_processed_transaction(tx):
    if tx and tx.was_processed():
        utility_service.set_flash_variable("cashnet_tx_id", tx.id)
    else:
        utility_service.set_flash_variable("cashnet_tx_id", None)


def get_processed_transaction():
    tx_id = utility_service.get_flash_variable("cashnet_tx_id")
    if tx_id:
        return get_transaction(tx_id)
    else:
        return None


def _update_tx_from_parameters(tx, parameters):
    log.debug(f"Updating transaction #{tx.id}")

    # RECORD CASHNET PARAMETERS
    # -----------------------------------------------------
    try:
        tx.result_parameters = str(parameters)[0:500]
        tx.response_date = datetime.now()
        tx.status_code = "P"  # Processing (must be updated again before exiting)
        # Save specific Cashnet response values
        tx.cashnet_result_code = parameters.get("result")
        tx.cashnet_result_message = parameters.get("respmessage")
        tx.cashnet_error_code = parameters.get("ccerrorcode")
        tx.cashnet_error_message = parameters.get("ccerrormessage")
        tx.cashnet_transaction = parameters.get("tx")
        tx.cashnet_batch = parameters.get("batchno")
        tx.save()
    except Exception as ee:
        msg = f"Error updating transaction #{tx.id}"
        tx.status_code = "E"  # <-- ERROR STATUS
        tx.internal_error_message = msg
        tx.save()
        error_service.record(ee, msg)
        return tx

    # VALIDATE PARAMETERS
    # -----------------------------------------------------
    # Must contain a result parameter
    if "result" not in parameters:
        msg = "Missing 'result' parameter"
        tx.status_code = "E"  # <-- ERROR STATUS
        tx.internal_error_message = msg
        tx.save()
        log.error(msg)
        return tx

    # VALIDATE AMOUNT
    # -----------------------------------------------------
    log.debug(f"Validating transaction amount")
    ii = 0
    total = Decimal(0.00)
    try:
        while ii < 100:
            ii += 1
            if f"amount{ii}" not in parameters:
                break

            this_amount = parameters[f"amount{ii}"]
            if this_amount is not None:
                total += Decimal(this_amount)

    except Exception as ee:
        error_service.record(
            ee, f"Error verifying item amounts for transaction #{tx.id}"
        )

    # Amounts in parameters must match amount in transaction
    if total != tx.total_amount():
        error = f"Amount mismatch: {total} / {tx.total_amount()}"
        log.error(error)
        tx.status_code = "E"  # <-- ERROR STATUS
        tx.internal_error_message = error
        tx.save()
        return tx

    # Update the status to Recorded.
    # Success or Error status will be determined after authentication
    tx.status_code = "R"
    tx.save()
    log.info(f"Transaction #{tx.id} data recorded")

    return tx


def _validate_unprocessed_tx_status(tx, payment_completed):
    if tx:
        try:
            # If transaction status was already updated, mark as duplicate
            # ------------------------------------------------------------
            if tx and tx.status_code != "I":
                tx.duplicate_count += 1
                tx.duplicate_date = datetime.now()
                tx.save()

                # If this instance is successful, and previous was not, flag error
                if payment_completed and not tx.was_successful():
                    error_service.record(
                        "Duplicated transaction with non-matching result",
                        f"{tx} claims to be successful",
                    )

                # Never re-process a transaction
                return False
            # ------------------------------------------------------------
        except Exception as ee:
            error_service.record(
                ee, f"Error checking duplicate transaction status for {tx}"
            )

    # If no transaction was found, cannot process the result
    else:

        browser = utility_service.get_browser()
        # Maybe the link was shared in Slack (asking to be set up in Cashnet Admin interface)
        if 'Slackbot' in browser:
            log.warning("Unable to process Cashnet response page for Slackbot.")
        elif 'Iframely' in browser:
            log.warning("Unable to process Cashnet response page for Iframely.")
        else:
            log.error("No transaction was found. Unable to process Cashnet response.")
        return None

    # Otherwise, transaction is in a status that can be updated
    return True


def _retrieve_transaction_from_cn_parameters(parameters):
    log.trace(parameters)

    # Determine the transaction ID
    tx_id = None
    ok_to_be_none = False
    try:
        # Retrieve tx ID from session
        tx_id_session = utility_service.get_session_var("cashnet_tx_id")
        utility_service.set_session_var("cashnet_tx_id", None)

        # Also get tx ID from Cashnet parameters (sometimes CN puts it in the wrong parameter (val2))
        tx_id_cn = parameters.get("ref1val1", parameters.get("ref1val2"))
        if not tx_id_cn:
            try:
                for kk, vv in parameters.items():
                    if kk.startswith("ref1type") and vv == "TRANSACTION_ID":
                        tx_id_cn = parameters.get(kk.replace("type", "val"))
                        if tx_id_cn and str(tx_id_cn).isnumeric():
                            break
            except Exception as ee:
                error_service.record(
                    ee, "Trying to find TRANSACTION_ID in Cashnet parameters"
                )

        # Sometimes Cashnet does not return the tx ID
        if tx_id_session and not tx_id_cn:
            tx_id = tx_id_session
        # Session could have expired if on cn site for a while
        elif tx_id_cn and not tx_id_session:
            tx_id = tx_id_cn
        # They should both match
        elif tx_id_cn and tx_id_session and str(tx_id_cn) == str(tx_id_session):
            tx_id = tx_id_cn
        # If they don't match, log warning, but use CN
        elif tx_id_cn and tx_id_session:
            log.warning(
                f"Cashnet and Session disagree on transaction ID. CN: {tx_id_cn}, Session: {tx_id_session}"
            )
            tx_id = tx_id_cn
        # Without a transaction ID, cannot process the results
        else:
            tx_id = None
            browser = utility_service.get_browser()
            # Maybe the link was shared in Slack (asking to be set up in Cashnet Admin interface)
            if 'Slackbot' in browser:
                ok_to_be_none = True
                log.info("Slackbot is trying to display a preview the Cashnet Response page")
            elif 'Iframely' in browser:
                ok_to_be_none = True
                log.info("Iframely is trying to do something with the Cashnet Response URL")
            else:
                log.error("No transaction ID was found in the session or parameters")
    except Exception as ee:
        error_service.record(ee, f"Error locating transaction ID")

    # Retrieve the transaction from database
    tx = None
    if tx_id:
        log.info(f"Retrieving transaction #{tx_id}")
        try:
            tx = get_transaction(tx_id)
        except Exception as ee:
            error_service.record(ee, f"Error querying transaction #{tx_id}")

    # If transaction was not located...
    if not tx:
        # If someone pasted the link into Slack, or some other link-expanding bot is detected
        if ok_to_be_none:
            log.warning("Transaction Not Found, but that's probably OK in this case.")

        # Seems common for CN to not include transaction # on canceled transactions
        elif 'result' in parameters and str(parameters.get("result")) != '0':
            log.warning("Transaction not specified. Failed transaction will remain in 'initiated' state.")

        # Log the parameters as an unexpected error for easy retrieval
        else:
            error_service.record("Transaction Not Found", f"Error querying transaction #{tx_id}")

    log.end(tx)
    return tx
