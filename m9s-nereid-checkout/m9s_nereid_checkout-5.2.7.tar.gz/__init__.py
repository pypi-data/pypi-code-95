# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import sale
from . import payment
from . import checkout
from . import configuration

__all__ = ['register']


def register():
    Pool.register(
        checkout.Address,
        checkout.Cart,
        configuration.Configuration,
        checkout.Party,
        checkout.Checkout,
        payment.Website,
        payment.NereidPaymentMethod,
        sale.Sale,
        sale.SaleLine,
        type_="model", module="nereid_checkout"
    )
