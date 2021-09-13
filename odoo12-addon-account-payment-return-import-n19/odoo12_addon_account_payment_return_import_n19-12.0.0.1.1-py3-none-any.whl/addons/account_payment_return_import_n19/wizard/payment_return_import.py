# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import api, models
from .n19_parser import N19Parser

_logger = logging.getLogger(__name__)


class PaymentReturnImport(models.TransientModel):
    _inherit = 'payment.return.import'

    @api.model
    def _parse_file(self, data_file):
        try:
            _logger.debug("Try parsing as a Norma 19 "
                          "Debit Credit Notification.")
            n19_parser = N19Parser(data_file)
            parsed_return_import = n19_parser.parse()
            for transaction in parsed_return_import['transactions']:
                mandate = self.env['account.banking.mandate'].search([
                    ('unique_mandate_reference', '=', transaction.pop('mandate')),
                ])
                if mandate:
                    transaction['partner_id'] = mandate.partner_id.id
            return parsed_return_import
        except ValueError:
            _logger.debug("Payment return file is not a Norma 19 "
                          "supported file.", exc_info=True)
            return super(PaymentReturnImport, self)._parse_file(data_file)
