# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import random
import json

from decimal import Decimal
from ast import literal_eval
from unittest.mock import patch
from datetime import date

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.config import config

from nereid.testing import NereidModuleTestCase

from trytond.modules.company.tests import create_company, set_company
from trytond.modules.nereid.tests.test_common import (create_website_locale,
    create_static_file)
from trytond.modules.payment_gateway.tests import (create_payment_gateway,
    create_payment_profile)
from trytond.modules.nereid_cart_b2c.tests import (create_website,
    create_countries, create_pricelists, create_product_template)

config.set('email', 'from', 'from@xyz.com')


def process_sale_by_completing_payments(sales):
    '''
    Process sale and complete payments.
    '''
    pool = Pool()
    Sale = pool.get('sale.sale')

    Sale.process(sales)
    Sale.process_all_pending_payments()


def create_order(client, quantity=None, mode='guest'):
    '''
    A helper function that creates an order for a
    guest/registered user.
    '''
    pool = Pool()
    Account = pool.get('account.account')
    Country = pool.get('country.country')
    Product = pool.get('product.product')
    Party = pool.get('party.party')

    # Setup defaults
    # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
    # etc.)
    website = create_website()
    website.save()
    gateway = create_payment_gateway()
    gateway.save()

    product_uri = 'product-1'
    products = Product.search([
            ('uri', '=', product_uri),
            ])
    if products:
        product1 = products[0]
    else:
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri=product_uri,
        )

        product1 = template1.products[0]

    if not quantity:
        quantity = random.randrange(10, 100)
    client.post('/en/cart/add',
        data={
            'product': product1.id,
            'quantity': quantity,
            })

    # Sign-in
    if mode == 'guest':
        login_data = {
            'email': 'new@example.com',
            'checkout_mode': 'guest',
            }
    else:
        login_data = {
            'email': 'email@example.com',
            'password': 'password',
            'checkout_mode': 'account',
            }
    rv = client.post('/en/checkout/sign-in',
            data=login_data)

    countries = Country.search([])
    if not countries:
        create_countries()
        countries = Country.search([])
    if not website.countries:
        website.countries = countries
        website.save()
    country = countries[0]
    subdivision = country.subdivisions[0]

    rv = client.post('/en/checkout/shipping-address',
        data={
            'name': 'Max Mustermann',
            'street': 'Musterstr. 26',
            'zip': '79852',
            'city': 'Musterstadt',
            'country': country.id,
            'subdivision': subdivision.id,
        })

    # Post to payment delivery-address with same flag
    rv = client.post('/en/checkout/payment',
        data={
            'use_shipment_address': 'True',
            })

    receivable, = Account.search([
            ('type.receivable', '=', True),
            ])
    parties = Party.search([])
    Party.write(parties, {
            'account_receivable': receivable,
            })


def create_alternate_payment_method():
    '''
    A helper function that creates an alternate (manual) gateway and assigns
    it to the website.
    '''
    pool = Pool()
    PaymentMethod = pool.get('nereid.website.payment_method')

    website = create_website()
    website.save()
    gateway = create_payment_gateway(method='manual')

    payment_method = PaymentMethod(
        name='Cheque',
        gateway=gateway,
        website=website
    )
    payment_method.save()
    return payment_method


class NereidCheckoutPaymentTestCase(NereidModuleTestCase):
    'Test Nereid Checkout module'
    module = 'nereid_checkout'
    extras = ['sale_shipment_cost', 'sale_channel_price_list']

    def setUp(self):
        self.templates = {
            'home.jinja': '{{get_flashed_messages()}}',
            'login.jinja':
                '{{ login_form.errors }} {{get_flashed_messages()}}',
            'shopping-cart.jinja':
                'Cart:{{ cart.id }},{{get_cart_size()|round|int}},'
                '{{cart.sale.total_amount}}',
            'product.jinja':
                '{{ product.sale_price(product.id) }}',
            'address-edit.jinja':
            'Address Edit {% if address %}ID:{{ address.id }}{% endif %}'
            '{{ form.errors }}',
            'address.jinja': '',
            'checkout/signin.jinja': '{{form.errors|safe}}',
            'checkout/signin-email-in-use.jinja': '{{email}} in use',
            'checkout/shipping_address.jinja': '{{address_form.errors|safe}}',
            'checkout/billing_address.jinja': '{{address_form.errors|safe}}',
            'checkout/payment_method.jinja': '''[
                {{payment_form.errors|safe}},
                {{credit_card_form.errors|safe}},
            ]''',
            'emails/sale-confirmation-text.jinja': ' ',
            'emails/sale-confirmation-html.jinja': ' ',
            'checkout.jinja': '{{form.errors|safe}}',
            'sale.jinja':
                '{{ sale.id }} {{get_flashed_messages()}}',
            'sales.jinja': '''{{request.args.get('filter_by')}}
                {% for sale in sales %}#{{sale.id}}{% endfor %}
            '''
            }

        # Patch SMTP Lib
        self.smtplib_patcher = patch('smtplib.SMTP')
        self.PatchedSMTP = self.smtplib_patcher.start()

    def tearDown(self):
        # Unpatch SMTP Lib
        self.smtplib_patcher.stop()

    @with_transaction()
    def test_0005_no_skip_signin(self):
        '''
        Ensure that guest orders cant directly skip to enter shipping address
        '''
        pool = Pool()
        Company = pool.get('company.company')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()
        company, = Company.search([])

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product1 = template1.products[0]
        quantity = 5

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                }
            )
            rv = c.get('/en/checkout/payment')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/sign-in'))

    @with_transaction()
    def test_0010_no_skip_shipping_address(self):
        '''
        Ensure that guest orders cant directly skip to payment without a
        valid shipment_address.

        Once shipment address is there, it should be possible to get the
        page even without a invoice_address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product1 = template1.products[0]
        quantity = 5

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Sign-in
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })

            # redirect to shipment address page
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'name': 'Max Mustermann',
                    'street': 'Musterstr. 26',
                    'zip': '79852',
                    'city': 'Musterstadt',
                    'country': country.id,
                    'subdivision': subdivision.id,
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            sales = Sale.search([])
            self.assertEqual(len(sales), 1)

            rv = c.get('/en/checkout/payment')
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0020_no_skip_invoice_address(self):
        '''
        While it is possible to view the payment_method page without a
        billing_address, it should not be possible to complete payment without
        it.
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product1 = template1.products[0]
        quantity = 5

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Sign-in
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })

            # redirect to shipment address page
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'name': 'Max Mustermann',
                    'street': 'Musterstr. 26',
                    'zip': '79852',
                    'city': 'Musterstadt',
                    'country': country.id,
                    'subdivision': subdivision.id,
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            sales = Sale.search([])
            self.assertEqual(len(sales), 1)

            # GET requests get served
            rv = c.get('/en/checkout/payment')
            self.assertEqual(rv.status_code, 200)

            # POST redirects to billing address
            rv = c.post('/en/checkout/payment', data={})

            # redirect to shipment address page
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/billing-address'))

    @with_transaction()
    def test_0030_address_with_payment(self):
        '''
        Send address along with the payment
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Party = pool.get('party.party')
        Country = pool.get('country.country')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        # Create product templates with products
        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product1 = template1.products[0]
        quantity = 5

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Sign-in
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })

            # redirect to shipment address page
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Shipping address page gets rendered
            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'zip': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                }
            rv = c.post('/en/checkout/shipping-address',
                data=address_data)
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            sales = Sale.search([])
            self.assertEqual(len(sales), 1)

            # POST to payment delivery-address with same flag
            rv = c.post('/en/checkout/payment',
                data={
                    'use_shipment_address': 'True',
                    })
            self.assertEqual(rv.status_code, 200)

            # Assert that just one address was created
            party, = Party.search([
                ('contact_mechanisms.value', '=', 'new@example.com'),
                ('contact_mechanisms.type', '=', 'email'),
            ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, address_data['street'])

            sales = Sale.search([
                ('shipment_address', '=', address.id),
                ('invoice_address', '=', address.id),
            ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0100_guest_credit_card(self):
        '''
        Guest - Credit Card
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='guest')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='guest')
                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                # Test the names on party and address
                self.assertEqual(
                    sale.party.name, 'Guest with email: new@example.com')
                self.assertEqual(
                    sale.party.addresses[0].party_name, 'Max Mustermann')

    @with_transaction()
    def test_0110_guest_alternate_payment(self):
        '''
        Guest - Alternate Payment Method
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        alternate_method = create_alternate_payment_method()
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:

            context = {
                'company': company.id,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='guest')
                # Try to pay using alternate method
                rv = c.post('/en/checkout/payment',
                    data={
                        'alternate_payment_method': alternate_method.id,
                        })

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

    @with_transaction()
    def test_0120_guest_profile_fail(self):
        "Guest - Error with profile"
        pool = Pool()
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='guest')

            # Try to pay using credit card
            rv = c.post(
                '/en/checkout/payment',
                data={
                    'payment_profile': 1
                    })
            self.assertEqual(rv.status_code, 200)
            payment_form_errors, _ = literal_eval(rv.data.decode('utf-8'))

            self.assertTrue('payment_profile' in payment_form_errors)

    @with_transaction()
    def test_0200_regd_new_credit_card_wo_save(self):
        '''"
        Registered User - Credit Card
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            'add_card_to_profiles': '',
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='reg')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='reg')
                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                # We don't save payment profiles (DSGVO)
                self.assertEqual(len(sale.party.payment_profiles), 0)

                # Test the names on party and address
                self.assertEqual(
                    sale.party.name, 'Registered User 1')
                self.assertEqual(sale.party.addresses[0].name, 'Address1')

    @with_transaction()
    def test_0205_regd_new_credit_card(self):
        '''
        Registered User - Credit Card (with saving the card)
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            'add_card_to_profiles': 'y',
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='reg')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='reg')
                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                # We don't save payment profiles (DSGVO)
                # Ensure that the card is not saved despite the setting
                # add_card_to_profile
                self.assertEqual(len(sale.party.payment_profiles), 0)

                # Test the names on party and address
                print(sale.party.rec_name)
                self.assertEqual(
                    sale.party.name, 'Registered User 1')
                self.assertEqual(sale.party.addresses[0].name, 'Address1')

    @with_transaction()
    def test_0210_regd_alternate_payment(self):
        '''
        Registered User - Alternate Payment Method
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        alternate_method = create_alternate_payment_method()
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:

            context = {
                'company': company.id,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='reg')
                # Try to pay using alternate method
                rv = c.post('/en/checkout/payment',
                    data={
                        'alternate_payment_method': alternate_method.id,
                        })

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertEqual(payment_transaction.state, 'posted')
                self.assertFalse(sale.payment_available)

    @with_transaction()
    def test_0220_regd_profile_fail(self):
        '''
        Registered User - Error with profile
        '''
        pool = Pool()
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='reg')

            # Try to pay using credit card
            rv = c.post(
                '/en/checkout/payment',
                data={
                    'payment_profile': 1
                    })
            self.assertEqual(rv.status_code, 200)
            payment_form_errors, _ = literal_eval(rv.data.decode('utf-8'))

            self.assertTrue('payment_profile' in payment_form_errors)

    @with_transaction()
    def test_0240_add_comment_to_sale(self):
        '''
        Add comment to a sale for a logged in user.
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            'add_card_to_profiles': 'y',
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='reg')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:
            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='reg')
                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                response = c.post('/en/login',
                    data={
                        'email': 'email@example.com',
                        'password': 'password',
                        })
                self.assertEqual(response.status_code, 302)  # Login success

                comment = 'This is a comment on sale!'
                rv = c.post('/en/order/%s/add-comment' % (sale.id,),
                    data={
                        'comment': comment,
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])

                json_data = json.loads(rv.data.decode('utf-8'))['message']
                self.assertEqual('Comment Added', json_data)
                self.assertEqual(comment, sale.comment)

                # Updating a comment is not allowed and aborts silently
                rv = c.post('/en/order/%s/add-comment' % (sale.id,),
                    data={
                        'comment': 'Another comment!'
                        })
                self.assertTrue(rv.status_code, 302)
                self.assertEqual(comment, sale.comment)

    @with_transaction()
    def test_0245_no_comment_on_cancelled_sale(self):
        '''
        Trying to comment on a cancelled sale should return 403.
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            'add_card_to_profiles': 'y',
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='reg')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        # Define a new credit card payment gateway
        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:
            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='reg')
                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                # Cancel the sale order now.
                Sale.cancel([sale])

                response = c.post('/en/login',
                    data={
                        'email': 'email@example.com',
                        'password': 'password',
                        })
                self.assertEqual(response.status_code, 302)  # Login success

                # Comment is not allowed and returns forbidden
                rv = c.post('/en/order/%s/add-comment' % (sale.id,),
                    data={
                        'comment': 'Another comment!'
                        })
                self.assertTrue(rv.status_code, 403)

    @with_transaction()
    def test_0250_add_comment_to_guest_sale(self):
        '''
        Add comment to a sale for a guest user with access code
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        alternate_method = create_alternate_payment_method()
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:

            context = {
                'company': company.id,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='guest')
                # Try to pay using alternate method
                rv = c.post('/en/checkout/payment',
                    data={
                        'alternate_payment_method': alternate_method.id,
                        })

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(payment_transaction.amount, sale.total_amount)
                self.assertFalse(sale.payment_available)

                # Forbidden without access_code
                comment = 'This is a comment on sale!'
                rv = c.post('/en/order/%s/add-comment' % (sale.id,),
                    data={
                        'comment': comment,
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])
                self.assertEqual(rv.status_code, 403)

                # Try again with access code
                rv = c.post('/en/order/%s/add-comment?access_code=%s' % (
                        sale.id, sale.guest_access_code),
                    data={
                        'comment': comment,
                    }, headers=[('X-Requested-With', 'XMLHttpRequest')])

                json_data = json.loads(rv.data.decode('utf-8'))['message']
                self.assertEqual('Comment Added', json_data)
                self.assertEqual(comment, sale.comment)

                self.assertTrue(rv.status_code, 302)
                self.assertEqual(comment, sale.comment)

    @with_transaction()
    def test_0300_access_order_page(self):
        '''
        Test the access to the order page
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        alternate_method = create_alternate_payment_method()
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:

            context = {
                'company': company.id,
                }
            with Transaction().set_context(**context):
                create_order(c, mode='guest')
                # Try to pay using alternate method
                rv = c.post('/en/checkout/payment',
                    data={
                        'alternate_payment_method': alternate_method.id,
                        })

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales(Sale.search([]))
                sale, = Sale.search([('state', '=', 'quotation')])

                # Process sale with payments
                #process_sale_by_completing_payments([sale])
                #payment_transaction, = sale.gateway_transactions
                #self.assertEqual(payment_transaction.amount, sale.total_amount)
                #self.assertFalse(sale.payment_available)

                # Forbidden without access_code
                rv = c.get('/en/order/%s' % (sale.id, ))
                self.assertEqual(rv.status_code, 302)  # Redirect to login

                # Forbidden with wrong access_code
                rv = c.get(
                    '/en/order/%s?access_code=%s' % (sale.id, "wrong-access-code")
                )
                self.assertEqual(rv.status_code, 403)

                # Success with correct access code
                rv = c.get('/en/order/%s?access_code=%s' % (
                        sale.id, sale.guest_access_code))
                self.assertEqual(rv.status_code, 200)


    @with_transaction()
    def test_0305_orders_page_regd(self):
        '''
        Access the orders page for a registered user.
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        NereidUser = pool.get('nereid.user')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        company, = Company.search([])

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        party = registered_user.party

        template1, = create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
            }],
            uri='product-1',
        )

        product = template1.products[0]
        uom = template1.sale_uom

        app = self.get_app()
        with app.test_client() as c:
            # Sign-in
            rv = c.post('/en/login',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                    })

            # Create sales
            with Transaction().set_context(company=company.id):
                sale1, = Sale.create([{
                    'reference': 'Sale1',
                    'sale_date': date.today(),
                    'invoice_address': party.addresses[0].id,
                    'shipment_address': party.addresses[0].id,
                    'party': party.id,
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 2,
                            'unit': uom,
                            'unit_price': 200,
                            'description': 'Test description1',
                            'product': product.id,
                        }])
                    ]}])
                sale2, = Sale.create([{
                    'reference': 'Sale2',
                    'sale_date': date.today(),
                    'invoice_address': party.addresses[0].id,
                    'shipment_address': party.addresses[0].id,
                    'state': 'done',  # For testing purpose.
                    'party': party.id,
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 2,
                            'unit': uom,
                            'unit_price': 200,
                            'description': 'Test description1',
                            'product': product.id,
                        }])
                    ]}])
                sale3, = Sale.create([{
                    'reference': 'Sale3',
                    'sale_date': date.today(),
                    'invoice_address': party.addresses[0].id,
                    'shipment_address': party.addresses[0].id,
                    'party': party.id,
                    'sale_date': '2014-06-06',  # For testing purpose.
                    'lines': [
                        ('create', [{
                            'type': 'line',
                            'quantity': 2,
                            'unit': uom,
                            'unit_price': 200,
                            'description': 'Test description1',
                            'product': product.id,
                        }])
                    ]}])

            Sale.quote([sale1])
            Sale.confirm([sale1])

            rv = c.get('/en/orders?filter_by=recent')
            self.assertIn('recent', rv.data.decode('utf-8'))
            self.assertIn('#{0}'.format(sale1.id), rv.data.decode('utf-8'))
            self.assertIn('#{0}'.format(sale2.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale3.id), rv.data.decode('utf-8'))

            rv = c.get('/en/orders?filter_by=done')
            self.assertIn('done', rv.data.decode('utf-8'))
            self.assertIn('#{0}'.format(sale2.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale1.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale3.id), rv.data.decode('utf-8'))

            Sale.cancel([sale3])

            rv = c.get('/en/orders?filter_by=canceled')
            self.assertIn('cancel', rv.data.decode('utf-8'))
            self.assertIn('#{0}'.format(sale3.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale1.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale2.id), rv.data.decode('utf-8'))

            rv = c.get('/en/orders?filter_by=archived')
            self.assertIn('archived', rv.data.decode('utf-8'))
            self.assertIn('#{0}'.format(sale3.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale1.id), rv.data.decode('utf-8'))
            self.assertNotIn('#{0}'.format(sale2.id), rv.data.decode('utf-8'))

    @with_transaction()
    def test_0310_guest_user_payment_using_credit_card(self):
        '''
        Note: The guest user has per default setup (create_website)
        a price list associated with factor * 1.2

        ===================================
        Total Sale Amount       |   $120
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $120
        ===================================
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        #sale_config.payment_authorize_on = 'manual'
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            #'add_card_to_profiles': True
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='guest')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, quantity=10, mode='guest')

                sale, = Sale.search([], limit=1)
                # The guest user has a price list with f * 1.2 per
                # create_website()
                self.assertEqual(sale.total_amount, Decimal('120'))
                self.assertEqual(sale.payment_total, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('0'))
                self.assertEqual(sale.payment_captured, Decimal('0'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                self.assertEqual(sale.state, 'draft')

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales([sale])
                sale, = Sale.search([('state', '=', 'quotation')])

                sale_payment, = sale.payments
                self.assertEqual(sale_payment.method, gateway.method)

                self.assertEqual(sale.payment_total, Decimal('120'))
                self.assertEqual(sale.payment_available, Decimal('120'))
                self.assertEqual(sale.payment_collected, Decimal('0'))
                self.assertEqual(sale.payment_captured, Decimal('0'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

                # Process sale with payments
                sale.payment_processing_state = "waiting_for_capture"
                sale.save()
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(sale.state, 'quotation')
                self.assertEqual(payment_transaction.state, 'posted')

                self.assertEqual(sale.payment_total, Decimal('120'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('120'))
                self.assertEqual(sale.payment_captured, Decimal('120'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

    @with_transaction()
    def test_0330_registered_user_payment_using_credit_card(self):
        '''
        Note: The registered user has per default setup (create_website)
        a price list associated with factor * 1.1

        ===================================
        Total Sale Amount       |   $110
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $110
        ===================================
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        NereidWebsite = pool.get('nereid.website')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'sale_confirm'
        sale_config.payment_capture_on = 'sale_process'
        sale_config.save()

        card_data = {
            'owner': 'Joe Blow',
            'number': '4111111111111111',
            'expiry_year': '2030',
            'expiry_month': '01',
            'cvv': '911',
            #'add_card_to_profiles': True
            }

        app = self.get_app()
        with app.test_client() as c:
            create_order(c, mode='guest')

            # Try to pay using credit card
            rv = c.post('/en/checkout/payment',
                data=card_data)
            # Though the card is there, the website is not configured
            # to accept credit cards as there is no credit card gateway defined.
            self.assertEqual(rv.status_code, 200)

        # Delete the draft sale to not interfere later with quote_web_sales for
        # missing payment amounts
        Sale.delete(Sale.search([]))

        gateway = create_payment_gateway(method='dummy')

        websites = NereidWebsite.search([])
        NereidWebsite.write(websites, {
            'accept_credit_card': True,
            'save_payment_profile': True,
            'credit_card_gateway': gateway.id,
        })

        company, = Company.search([])

        with app.test_client() as c:

            context = {
                'company': company.id,
                'use_dummy': True,
                'dummy_succeed': True,
                }
            with Transaction().set_context(**context):
                create_order(c, quantity=10, mode='reg')

                sale, = Sale.search([], limit=1)
                self.assertEqual(sale.total_amount, Decimal('110'))
                self.assertEqual(sale.payment_total, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('0'))
                self.assertEqual(sale.payment_captured, Decimal('0'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

                # Try to pay using credit card
                rv = c.post('/en/checkout/payment',
                    data=card_data)
                self.assertEqual(sale.state, 'draft')

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales([sale])
                sale, = Sale.search([('state', '=', 'quotation')])

                sale_payment, = sale.payments
                self.assertEqual(sale_payment.method, gateway.method)

                self.assertEqual(sale.payment_total, Decimal('110'))
                self.assertEqual(sale.payment_available, Decimal('110'))
                self.assertEqual(sale.payment_collected, Decimal('0'))
                self.assertEqual(sale.payment_captured, Decimal('0'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

                # Process sale with payments
                sale.payment_processing_state = "waiting_for_capture"
                sale.save()
                process_sale_by_completing_payments([sale])
                payment_transaction, = sale.gateway_transactions
                self.assertEqual(sale.state, 'quotation')
                self.assertEqual(payment_transaction.state, 'posted')

                self.assertEqual(sale.payment_total, Decimal('110'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('110'))
                self.assertEqual(sale.payment_captured, Decimal('110'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

    @with_transaction()
    def test_0340_registered_user_payment_using_alternate_method(self):
        '''
        Note: The registered user has per default setup (create_website)
        a price list associated with factor * 1.1

        ===================================
        Total Sale Amount       |   $110
        Payment Authorize On:   | 'sale_confirm'
        Payment Capture On:     | 'sale_process'
        ===================================
        Total Payment Lines     |     1
        Payment 1               |   $110
        ===================================
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Company = pool.get('company.company')
        SaleConfiguration = pool.get('sale.configuration')

        sale_config = SaleConfiguration(1)
        sale_config.payment_authorize_on = 'manual'
        sale_config.payment_capture_on = 'manual'
        sale_config.save()

        alternate_method = create_alternate_payment_method()
        company, = Company.search([])
        gateway = alternate_method.gateway

        app = self.get_app()
        with app.test_client() as c:

            context = {
                'company': company.id,
                }
            with Transaction().set_context(**context):
                create_order(c, quantity=10, mode='reg')

                sale, = Sale.search([])
                self.assertEqual(sale.total_amount, Decimal('110'))
                self.assertEqual(sale.payment_total, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('0'))
                self.assertEqual(sale.payment_captured, Decimal('0'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))

                # Try to pay using alternate method
                rv = c.post('/en/checkout/payment',
                    data={
                        'alternate_payment_method': alternate_method.id,
                        })

                # Run the sale and payment processing usually delegated
                # to the queue
                Sale.quote_web_sales([sale])
                sale, = Sale.search([('state', '=', 'quotation')])

                sale_payment, = sale.payments
                self.assertEqual(sale_payment.method, gateway.method)

                # Alternate method is captured at once
                self.assertEqual(sale.payment_total, Decimal('110'))
                self.assertEqual(sale.payment_available, Decimal('0'))
                self.assertEqual(sale.payment_collected, Decimal('110'))
                self.assertEqual(sale.payment_captured, Decimal('110'))
                self.assertEqual(sale.payment_authorized, Decimal('0'))
