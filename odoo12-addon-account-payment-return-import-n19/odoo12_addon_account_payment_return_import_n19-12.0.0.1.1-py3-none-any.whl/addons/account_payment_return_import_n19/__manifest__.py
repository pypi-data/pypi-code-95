# Copyright 2020 Coopdevs SCCL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Payment Return Import Norma 19',
    'summary': """
        This addon allows to import payment returns from Cuaderno/Norma 19 files
        """,
    'version': '12.0.0.1.1',
    'development_status': 'Production/Stable',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA),Coopdevs SCCL',
    'website': 'https://github.com/OCA/l10n-spain/tree/12.0/'
               'account_payment_return_import_n19',
    'depends': [
        # OCA/l10n-spain
        'account_payment_return_import_iso20022',
        'account_banking_mandate'
    ],
}
