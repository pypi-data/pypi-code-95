from pagarme.resources import handler_request
from pagarme.resources.routes import payment_link_routes

def cancel(payment_link_id):
    return handler_request.post(payment_link_routes.CANCEL_PAYMENT_LINK.format(payment_link_id))

def create(dictionary):
    return handler_request.post(payment_link_routes.BASE_URL, dictionary)

def find_all():
    return handler_request.get(payment_link_routes.BASE_URL)

def find_by(search_params):
    return handler_request.get(payment_link_routes.BASE_URL, search_params)

def find_by_id(payment_link_id):
    return handler_request.get(payment_link_routes.PAYMENT_LINK_BY_ID.format(payment_link_id))

def update_by_id(payment_link_id, dictionary):
    return handler_request.put(payment_link_routes.PAYMENT_LINK_BY_ID.format(payment_link_id), dictionary)
