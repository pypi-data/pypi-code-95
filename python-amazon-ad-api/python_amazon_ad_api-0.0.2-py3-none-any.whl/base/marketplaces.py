import sys
import os
import logging
from enum import Enum
from dotenv import dotenv_values

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s:%(levelname)s:%(message)s"
)

class AuthorizationError(Exception):
    """Exception raised for errors in the input salary.

    Attributes:
        salary -- input salary which caused the error
        message -- explanation of the error
    """

    def __init__(self, code, message=".env problem set your file in the root project"):
        # self.code = code
        # self.message = message
        # super().__init__(self.message)
        logging.warning(message);

class AWS_ENV(Enum):
    PRODUCTION = "PRODUCTION"
    SANDBOX = "SANDBOX"

config = dotenv_values(".env")

AWS_ENVIRONMENT = config.get('AWS_ENV')

BASE_URL_EU = "https://advertising-api-eu.amazon.com"
BASE_URL_US = "https://advertising-api.amazon.com"

if AWS_ENVIRONMENT is not None:
    #print(AWS_ENVIRONMENT)
    logging.warning('Running in choosen mode : %s' % AWS_ENVIRONMENT)

if AWS_ENVIRONMENT is None:
    # raise AuthorizationError(0, 'e', 'status_code')
    default_mode = os.environ["__MODE__"] = "SANDBOX"
    AWS_ENVIRONMENT = default_mode

    if AWS_ENVIRONMENT is not None:
        # print(AWS_ENVIRONMENT)
        logging.warning('Running in default: %s' % default_mode )
        # raise EnvironmentError(13900, 'Need create your own .env file: ')

    # sys.exit()

'''
if AWS_ENV(AWS_ENVIRONMENT) is None:
    print(AWS_ENVIRONMENT)
'''
'''
try:
    type(AWS_ENV(AWS_ENVIRONMENT))
except Exception as ex:
    print('except')
    print(ex)
    raise MissingCredentials(f'The following configuration parameters are missing: {ex}')
'''

if AWS_ENV(AWS_ENVIRONMENT) is AWS_ENV.SANDBOX:
    BASE_URL_EU = "https://advertising-api-test.amazon.com"
    BASE_URL_US = "https://advertising-api-test.amazon.com"

class Marketplaces(Enum):
    """Enumeration for MWS marketplaces, containing endpoints and marketplace IDs.
    Example, endpoint and ID for UK marketplace:
        endpoint = Marketplaces.UK.endpoint
        marketplace_id = Marketplaces.UK.marketplace_id
    """

    US = (f"{BASE_URL_US}", 'EUR')
    ES = (f"{BASE_URL_EU}", 'EUR')
    GB = (f"{BASE_URL_EU}", 'GBP')
    IT = (f"{BASE_URL_EU}", 'EUR')
    FR = (f"{BASE_URL_EU}", 'EUR')
    DE = (f"{BASE_URL_EU}", 'EUR')


    def __init__(self, endpoint, currency):
        """Easy dot access like: Marketplaces.endpoint ."""
        self.endpoint = endpoint
        self.currency = currency
