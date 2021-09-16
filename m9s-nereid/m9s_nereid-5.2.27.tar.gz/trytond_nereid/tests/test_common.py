# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from nereid.testing import POOL as pool
from trytond.pool import Pool

from trytond.tests.test_tryton import USER

from trytond.modules.company.tests import create_company, set_company
from trytond.modules.currency.tests import create_currency, add_currency_rate


def setup_objects(self):
    self.nereid_website_obj = pool.get('nereid.website')
    self.nereid_website_locale_obj = pool.get('nereid.website.locale')
    self.nereid_user_obj = pool.get('nereid.user')
    self.company_obj = pool.get('company.company')
    self.currency_obj = pool.get('currency.currency')
    self.language_obj = pool.get('ir.lang')
    self.party_obj = pool.get('party.party')
    self.country_obj = pool.get('country.country')
    self.subdivision_obj = pool.get('country.subdivision')
    self.party_obj = pool.get('party.party')
    self.address_obj = pool.get('party.address')
    self.static_file_obj = pool.get('nereid.static.file')
    self.static_folder_obj = pool.get('nereid.static.folder')


def create_website_locale(code='en', language=None, currency=None):
    """
    Creates the static file for testing
    """
    pool = Pool()
    Language = pool.get('ir.lang')
    WebsiteLocale = pool.get('nereid.website.locale')
    Currency = pool.get('currency.currency')

    website_locales = WebsiteLocale.search([('code', '=', code)])
    if website_locales:
        return website_locales[0]

    if currency is None:
        currencies = Currency.search([
                ('code', '=', 'usd'),
                ])
        if currencies:
            currency = currencies[0]
        else:
            currency = create_currency('usd')
            add_currency_rate(currency, 1)

    if language is None:
        en, = Language.search([('code', '=', 'en')])
        language = en

    website_locale, = WebsiteLocale.create([{
                'code': code,
                'language': language,
                'currency': currency,
                }])
    return website_locale


def create_website(name='localhost', locales=[], default_locale=None):
    """
    Creates the static file for testing
    """
    pool = Pool()
    Website = pool.get('nereid.website')

    websites = Website.search([('name', '=', name)])
    if websites:
        return websites[0]

    company = create_company()

    if not locales:
        locale = create_website_locale()
        locales = [('add', [locale.id])]
        default_locale = locale
    else:
        locales = [('add', [l for l in locales])]

    if default_locale is None:
        default_locale = locales[0]

    website, = Website.create([{
                'name': name,
                'company': company,
                'application_user': USER,
                'default_locale': default_locale,
                'locales': locales,
                }])
    return website


def create_static_file(file_memoryview, name='test.png'):
    """
    Creates the static file for testing
    """
    pool = Pool()
    StaticFile = pool.get('nereid.static.file')
    StaticFolder = pool.get('nereid.static.folder')

    create_website()

    folders = StaticFolder.search([('name', '=', 'test')])
    if folders:
        folder, = folders
    else:
        folder, = StaticFolder.create([{
                    'name': 'test',
                    'description': 'Test Folder'
                    }])
    static_file, = StaticFile.create([{
                'name': name,
                'folder': folder,
                'file_binary': file_memoryview,
                }])
    return static_file
