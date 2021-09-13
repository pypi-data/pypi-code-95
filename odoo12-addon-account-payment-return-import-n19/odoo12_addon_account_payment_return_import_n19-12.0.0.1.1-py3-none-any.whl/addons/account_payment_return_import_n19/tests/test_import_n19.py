# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.account_payment_return_import.tests import (
    TestPaymentReturnFile)


class TestImport(TestPaymentReturnFile):
    """Run test to import payment return import."""

    @classmethod
    def setUpClass(cls):
        super(TestImport, cls).setUpClass()
        cls.company = cls.env.ref('base.main_company')
        cls.acc_number = 'ES9230044573352643814459'
        cls.acc_bank = cls.env['res.partner.bank'].create({
            'acc_number': cls.acc_number,
            'bank_name': 'TEST BANK',
            'company_id': cls.company.partner_id.id,
            'partner_id': cls.company.partner_id.id,
        })
        cls.journal = cls.env['account.journal'].create({
            'name': 'Test Bank Journal',
            'code': 'BANK',
            'type': 'bank',
            'update_posted': True,
            'bank_account_id': cls.acc_bank.id,
        })
        cls.journal.bank_account_id = cls.acc_bank
        cls.acc_number_customer_1 = 'ES1800598335623239116291'
        cls.customer_1 = cls.env['res.partner'].create({
            'name': "CUSTOMER 1"
        })
        cls.acc_bank_customer_1 = cls.env['res.partner.bank'].create({
            'acc_number': cls.acc_number_customer_1,
            'bank_name': 'TEST BANK CUSTOMER 1',
            'company_id': cls.company.partner_id.id,
            'partner_id': cls.customer_1.id,
        })
        cls.env['account.banking.mandate'].create({
            'partner_id': cls.customer_1.id,
            'partner_bank_id': cls.acc_bank_customer_1.id,
            'unique_mandate_reference': '15805'
        })
        cls.acc_number_customer_2 = 'ES2913011611144790679726'
        cls.customer_2 = cls.env['res.partner'].create({
            'name': "CUSTOMER 2"
        })
        cls.acc_bank_customer_2 = cls.env['res.partner.bank'].create({
            'acc_number': cls.acc_number_customer_2,
            'bank_name': 'TEST BANK CUSTOMER 2',
            'company_id': cls.company.partner_id.id,
            'partner_id': cls.customer_2.id,
        })
        cls.env['account.banking.mandate'].create({
            'partner_id': cls.customer_2.id,
            'partner_bank_id': cls.acc_bank_customer_2.id,
            'unique_mandate_reference': '20290'
        })

    def test_payment_return_import_n19(self):
        """Test correct creation of single payment return."""
        transactions = [
            {
                'returned_amount': 50.01,
                'reference': '611533',
            },
            {
                'returned_amount': 52.67,
                'reference': '620091',
            },
        ]
        self._test_return_import(
            'account_payment_return_import_n19',
            'test-n19.txt',
            'DEV20201027000000147750000012068500',
            local_account='ES9230044573352643814459',
            date='2020-10-26', transactions=transactions
        )
        payment_lines = self.env['payment.return.line'].search([
            '|',
            ('partner_id', '=', self.customer_1.id),
            ('partner_id', '=', self.customer_2.id)
        ])
        self.assertEquals(len(payment_lines), 2)
