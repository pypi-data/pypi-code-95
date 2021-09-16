# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import PoolMeta


class Configuration(metaclass=PoolMeta):
    """
    Sale Configuration
    """
    __name__ = 'sale.configuration'

    @staticmethod
    def default_payment_authorize_on():
        return 'manual'

    @staticmethod
    def default_payment_capture_on():
        return 'sale_process'
