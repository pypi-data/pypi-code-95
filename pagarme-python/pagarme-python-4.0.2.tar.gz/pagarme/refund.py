from pagarme.resources import handler_request
from pagarme.resources.routes import refund_routes


def refunds():
    return handler_request.get(refund_routes.BASE_URL)
