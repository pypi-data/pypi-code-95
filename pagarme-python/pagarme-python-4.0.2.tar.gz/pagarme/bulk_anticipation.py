from pagarme.resources import handler_request
from pagarme.resources.routes import bulk_anticipation_routes


def cancel(recipient_id, bulk_anticipation_id):
    return \
        handler_request.post(bulk_anticipation_routes.CANCEL_ANTICIPATION.format(recipient_id, bulk_anticipation_id))


def confirm(recipient_id, bulk_anticipation_id):
    return \
        handler_request.post(bulk_anticipation_routes.CONFIRM_ANTICIPATION.format(recipient_id, bulk_anticipation_id))


def create(recipient_id, dictionary):
    return handler_request.post(bulk_anticipation_routes.BASE_URL.format(recipient_id), dictionary)


def delete(recipient_id, bulk_anticipation_id):
    return \
        handler_request.delete(bulk_anticipation_routes.DELETE_ANTICIPATION.format(recipient_id, bulk_anticipation_id))


def find_all(recipient_id):
    return handler_request.get(bulk_anticipation_routes.GET_ALL_ANTICIPATIONS.format(recipient_id))


def limits(recipient_id, dictionary):
    return handler_request.get(bulk_anticipation_routes.GET_ANTICIPATION_LIMITS.format(recipient_id), dictionary)
