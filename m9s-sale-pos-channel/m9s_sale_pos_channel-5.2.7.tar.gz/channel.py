# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pyson import Eval
from trytond.pool import PoolMeta

STATES = {
    'invisible': Eval('source') != 'pos',
    }


class SaleChannel(metaclass=PoolMeta):
    __name__ = 'sale.channel'

    pos_party = fields.Many2One('party.party', 'Default POS Party',
        states=STATES, depends=['source'])
    self_pick_up = fields.Boolean('Default Self Pick Up',
        states=STATES, depends=['source'],
        help='The goods are picked up directly by the customer. '
        '(Delivery without shipment)')

    @classmethod
    def __setup__(cls):
        super(SaleChannel, cls).__setup__()
        source = ('pos', 'POS')
        if source not in cls.source.selection:
            cls.source.selection.append(source)
