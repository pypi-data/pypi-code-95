import transaction
from pyramid_celery import celery_app
from endi.export.task_pdf import ensure_task_pdf_persisted
from endi.models.task import Task
from endi_celery.hacks import (
    setup_rendering_hacks,
)
from endi_celery.mail import (
    send_customer_new_order_mail,
    send_supplier_new_order_mail,
    send_customer_new_invoice_mail,
    send_supplier_new_invoice_mail,
)
from endi_celery.tasks import utils


logger = utils.get_logger(__name__)


@celery_app.task(bind=True)
def scheduled_render_pdf_task(self, document_id):
    logger.debug("Scheduling a PDF render Task for {}".format(document_id))
    document = utils.get_task(document_id)
    if document is None:
        raise Exception("Document doesn't exist in database")

    request = celery_app.conf['PYRAMID_REQUEST']
    try:
        # Ensure layout_manager
        setup_rendering_hacks(request, document)
        ensure_task_pdf_persisted(document, request)
        transaction.commit()
    except Exception:
        logger.exception("Error in async_internalestimation_valid_callback")
        transaction.abort()


@celery_app.task(bind=True)
def async_internalestimation_valid_callback(self, document_id):
    """
    Handle the transfer of an InternalEstimation to the Client Company

    - Ensure supplier exists
    - Generates the PDF
    - Create a Supplier Order and attache the pdf file
    """
    logger.debug(
        "Async internal estimation validation callback for {}".format(
            document_id
        )
    )
    document = utils.get_task(document_id)
    if document is None:
        logger.error(
            "Document with id {} doesn't exist in database".format(
                document_id
            )
        )
        return

    request = celery_app.conf['PYRAMID_REQUEST']
    # Ensure layout_manager
    try:
        setup_rendering_hacks(request, document)
        order = document.sync_with_customer(request)
        send_customer_new_order_mail(request, order)
        send_supplier_new_order_mail(request, order)
        transaction.commit()
    except Exception:
        logger.exception("Error in async_internalestimation_valid_callback")
        transaction.abort()


@celery_app.task(bind=True)
def async_internalinvoice_valid_callback(self, document_id):
    """
    Handle the transfer of an InternalInvoice to the Client Company

    - Ensure supplier exists
    - Generates the PDF
    - Create a Supplier Invoice and attach the pdf file
    """
    logger.debug(
        "Async internal invoice validation callback for {}".format(
            document_id
        )
    )
    document = utils.get_task(document_id)
    if document is None:
        logger.error(
            "Document with id {} doesn't exist in database".format(
                document_id
            )
        )
        return

    request = celery_app.conf['PYRAMID_REQUEST']
    # Ensure layout_manager
    try:
        setup_rendering_hacks(request, document)
        order = document.sync_with_customer(request)
        send_customer_new_invoice_mail(request, order)
        send_supplier_new_invoice_mail(request, order)
        transaction.commit()
    except Exception:
        logger.exception("Error in async_internalinvoice_valid_callback")
        transaction.abort()
