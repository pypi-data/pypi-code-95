# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import configuration
from . import channel
from . import party
from . import sale
from . import user

__all__ = ['register']


def register():
    Pool.register(
        configuration.Configuration,
        configuration.ConfigurationSequence,
        sale.Sale,
        sale.SaleLine,
        sale.StatementLine,
        sale.AddProductForm,
        sale.SalePaymentForm,
        channel.SaleChannel,
        user.User,
        module='sale_pos_channel', type_='model')
    Pool.register(
        sale.SaleTicketReport,
        sale.SaleReportSummary,
        module='sale_pos_channel', type_='report')
    Pool.register(
        party.PartyReplace,
        sale.WizardAddProduct,
        sale.WizardSalePayment,
        module='sale_pos_channel', type_='wizard')
