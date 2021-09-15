from pagarme.resources import handler_request
from pagarme.resources.routes import recipient_routes


def create(dictionary):
    return handler_request.post(recipient_routes.BASE_URL, dictionary)


def default_recipient():
    return handler_request.get(recipient_routes.GET_DEFAULT_RECIPIENT)['default_recipient_id']


def find_all():
    return handler_request.get(recipient_routes.GET_ALL_RECIPIENTS)


def find_by(search_params):
    return handler_request.get(recipient_routes.GET_RECIPIENT_BY, search_params)


def recipient_balance(recipient_id):
    return handler_request.get(recipient_routes.GET_RECIPIENT_BALANCE.format(recipient_id))


def recipient_balance_operation(recipient_id):
    return handler_request.get(recipient_routes.GET_RECIPIENT_BALANCE_OPERATIONS.format(recipient_id))


def recipient_balance_operation_id(recipient_id, operation_id):
    return \
        handler_request.get(recipient_routes.GET_RECIPIENT_BALANCE_OPERATION_BY_ID.format(recipient_id, operation_id))


def update_recipient(recipient_id, dictionary):
    return handler_request.put(recipient_routes.UPDATE_RECIPIENT.format(recipient_id), dictionary)
