# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta, Pool


class User(metaclass=PoolMeta):
    __name__ = "res.user"

    @fields.depends('current_channel', 'sale_device')
    def on_change_current_channel(self):
        SaleDevice = Pool().get('sale.device')
        if (not self.sale_device
                or self.current_channel != self.sale_device.channel):
            devices = SaleDevice.search([
                    ('channel', '=', self.current_channel)
                    ])
            if len(devices) == 1:
                self.sale_device = devices[0].id
        else:
            self.sale_device = None
