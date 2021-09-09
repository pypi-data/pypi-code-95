from odoo.addons.component.core import Component
from pycastiphone_client.resources.login import Login
from pycastiphone_client.resources.cliente import Cliente


class Contract(Component):
    _name = 'contract.listener'
    _inherit = 'base.event.listener'
    _apply_on = ['contract.contract']

    def on_record_create(self, record, fields=None):
        if not record.partner_id.ref:
            cliente_data = ClientePresenter(record.partner_id).to_dict()
            login = Login.authenticate()
            castiphone_cliente = Cliente.create(login.token, **cliente_data)
            record.partner_id.write({
                'ref': castiphone_cliente.codigo
            })


class ClientePresenter():
    def __init__(self, partner):
        self.partner = partner

    def to_dict(self):
        return {
            "razonSocial": self.partner.name,
            "cif": self.partner.vat,
            "direccion": self.partner.street,
            "correo": self.partner.email,
            "idioma": self.language(),
            "formaPago": 3,
        }

    def language(self):
        if self.partner.lang == 'eu_ES':
            language = 6
        else:
            language = 0
        return language
