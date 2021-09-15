from pagarme.resources.routes.recipient_routes import BASE_URL as BASE_RECIPIENT

BASE_URL = BASE_RECIPIENT + '/{0}/bulk_anticipations'

CANCEL_ANTICIPATION = BASE_URL + '/{1}/cancel'

CONFIRM_ANTICIPATION = BASE_URL + '/{1}/confirm'

DELETE_ANTICIPATION = BASE_URL + '/{1}'

GET_ALL_ANTICIPATIONS = BASE_URL

GET_ANTICIPATION_LIMITS = BASE_URL + '/limits'
