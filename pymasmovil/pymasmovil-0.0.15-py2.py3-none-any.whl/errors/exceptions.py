from pymasmovil.models.order_item_status import OrderItemStatus


class MissingLoginCredentialsError(Exception):
    """Raised when login credentials are missing"""

    message = """
    Autenthication failed.
    The required configuration setting {} was not found in your environment.
    To authenticate follow the instructions explained in the README:
    https://gitlab.com/coopdevs/pymasmovil#login
    """

    def __init__(self, missing_credential):
        self.message = self.message.format(missing_credential)
        super().__init__(self.message)


class AutenthicationError(Exception):
    """Raised when login to MM API failed"""

    message = """
    Autenthication to MM API failed. We may be using wrong login
    credentials or because there is a problem in the MM server side.
    """

    def __init__(self):
        super().__init__(self.message)


class AccountRequiredParamsError(Exception):
    """Raised when trying to create an account without some required paramether"""

    message = "Missing or empty attributes required to create an account: {}"

    def __init__(self, missing_argument_list):
        self.message = self.message.format(", ".join(missing_argument_list))
        super().__init__(self.message)


class NewLineRequestRequiredParamsError(Exception):
    """Exception raised when some compulsary attributes for the portability process
    are missing in the OTRS request."""

    message = "Missing or empty attributes required for the requested {}: {}"

    def __init__(self, is_portability, missing_argument_list):
        request_type = (
            "portability" if is_portability else "new phone number registration"
        )

        self.message = self.message.format(
            request_type, ", ".join(missing_argument_list)
        )
        super().__init__(self.message)


class TariffChangeRequiredParamsError(Exception):
    """Exception raised when some required parameters to build a tariff change request
    are missing."""

    message = "Missing or empty required attributes for the requested {}: {}"

    def __init__(self, update_type, missing_argument_list):
        self.message = self.message.format(
            update_type, ", ".join(missing_argument_list)
        )
        super().__init__(self.message)


class OrderItemNotFoundByICC(Exception):
    """Raised when no OrderItem is found with the given ICC"""

    message = "No order item with ICC: {} can be found in the account with id: {}"

    def __init__(self, ICC, account_id):
        self.message = self.message.format(ICC, account_id)
        super().__init__(self.message)


class OrderItemStatusNotFound(Exception):
    """Raised when a requested OrderItem status does not exist"""

    message = "Some of the requested order-item status: {} don't exist. Available ones are: {}"

    def __init__(self, status_list):
        self.message = self.message.format(status_list, OrderItemStatus.available_status)
        super().__init__(self.message)


class UnknownMMError(Exception):
    """Raised when the MM API returns an error with an unknown structure"""

    def __init__(self, MM_response_body):
        self.message = MM_response_body
        super().__init__(self.message)
