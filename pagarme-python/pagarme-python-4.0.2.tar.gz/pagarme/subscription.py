from pagarme.resources import handler_request
from pagarme.resources.routes import subscription_routes


def cancel(subscription_id):
    return handler_request.post(subscription_routes.CANCEL_SUBSCRIPTION.format(subscription_id))


def create(dictionary):
    return handler_request.post(subscription_routes.BASE_URL, dictionary)


def find_all():
    return handler_request.get(subscription_routes.GET_ALL_SUBSCRIPTIONS)


def find_by(search_params):
    return handler_request.get(subscription_routes.GET_SUBSCRIPTION_BY, search_params)


def transactions(subscription_id):
    return handler_request.get(subscription_routes.GET_ALL_SUBSCRIPTIONS_TRANSACTIONS.format(subscription_id))


def postbacks(subscription_id):
    return handler_request.get(subscription_routes.GET_ALL_SUBSCRIPTIONS_POSTBACKS.format(subscription_id))


def postback_redeliver(subscription_id, postback_id):
    return \
        handler_request.post(subscription_routes.REDELIVER_SUBSCRIPTION_POSTBACK_BY_ID.format(subscription_id, postback_id))


def settle_charges(subscription_id, dictionary = {}):
    return handler_request.post(subscription_routes.SETTLE_CHARGES_SUBSCRIPTION.format(subscription_id), dictionary)


def update(subscription_id, dictionary):
    return handler_request.put(subscription_routes.UPDATE_SUBSCRIPTION.format(subscription_id), dictionary)
