from .lambda_client import AbstractLambdaClient
from .normalize import map_values


class AddressValidationClient(AbstractLambdaClient):

    IS_VALID_ADDRESS = "is_valid_address"
    NORMALIZE_ADDRESS = 'normalize_address'

    valid_triggers = [IS_VALID_ADDRESS, NORMALIZE_ADDRESS]

    def __init__(self):
        super().__init__("us-east-2", "AddressValidation")

    def is_valid_address(self, *, address_line_one, postal_code, country="US", city=None, state=None, address_line_two=None):
        body = {
            "addressLineOne": address_line_one,
            "postalCode": postal_code,
            "country": country
        }

        if city != None:
            body['city'] = city

        if state != None:
            body['state'] = state

        if address_line_two != None:
            body['addressLineTwo'] = address_line_two

        try:
            super().invoke(self.IS_VALID_ADDRESS, body)
            return True
        except:
            return False

    def normalize_address(self, *, address_line_one, postal_code, country="US", city=None, state=None, address_line_two=None):
        body = {
            "addressLineOne": address_line_one,
            "postalCode": postal_code,
            "country": country
        }

        if city != None:
            body['city'] = city

        if state != None:
            body['state'] = state

        if address_line_two != None:
            body['addressLineTwo'] = address_line_two

        response = super().invoke(self.NORMALIZE_ADDRESS, body)

        return map_values(response['body'], {
            "address_line_one": "address_one",
            "address_line_two": "address_two",
            "state_code": "state",
            "country_code": "country",
            "geo": "geocode"
        }
        )
