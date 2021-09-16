# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest

from decimal import Decimal
from ast import literal_eval
from unittest.mock import patch
from datetime import date

from trytond.tests.test_tryton import suite as test_suite
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

from .test_nereid_checkout_payment import NereidCheckoutPaymentTestCase


config.set('database', 'path', '/tmp')


class NereidCheckoutTestCase(NereidModuleTestCase):
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
            'sale.jinja': ' ',
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

    # ##################################
    # 000 Test the checkout Sign In Step
    # ##################################

    @with_transaction()
    def test_0010_check_cart(self):
        '''
        Assert nothing added by this module broke the cart.
        '''
        pool = Pool()
        Company = pool.get('company.company')
        Sale = pool.get('sale.sale')

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
            rv = c.get('/en/cart')
            self.assertEqual(rv.status_code, 200)

        sales = Sale.search([])
        self.assertEqual(len(sales), 1)
        sale = sales[0]
        self.assertEqual(len(sale.lines), 1)
        self.assertEqual(sale.lines[0].product, product1)
        self.assertEqual(sale.lines[0].quantity, quantity)

    @with_transaction()
    def test_0015_signin_with_empty_cart(self):
        '''
        Sign in with empty cart should redirect
        '''
        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        app = self.get_app()
        with app.test_client() as c:
            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 302)

    @with_transaction()
    def test_0020_guest_no_email(self):
        '''
        Submit as guest without email
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 200)

            rv = c.post('/en/checkout/sign-in', data={})
            self.assertTrue('email' in rv.data.decode('utf-8'))

            # Change the checkout mode to sign_in and even password
            # should become a required field
            rv = c.post('/en/checkout/sign-in',
                data={
                    'checkout_mode': 'account',
                    })
            for field in ['email', 'password']:
                self.assertTrue(field in rv.data.decode('utf-8'))

    @with_transaction()
    def test_0030_guest_valid(self):
        '''
        Submit as guest with a new email
        '''
        pool = Pool()
        Party = pool.get('party.party')

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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 200)

            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@m9s.biz',
                    })
            self.assertEqual(rv.status_code, 302)

            party, = Party.search([], order=[('id', 'DESC')], limit=1)
            self.assertEqual(party.email, 'new@m9s.biz')

    @with_transaction()
    def test_0035_guest_checkout_with_registered_email(self):
        '''
        When the user is guest and uses a registered email in the guest
        checkout, the default behavior is to show a help page in the
        template checkout/signin-email-in-use.jinja.
        '''
        pool = Pool()
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 200)

            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': registered_user.email
                })
            self.assertEqual(rv.status_code, 200)
            self.assertEqual(
                rv.data.decode('utf-8'), '%s in use' % registered_user.email)

    @with_transaction()
    def test_0040_registered_user_signin_wrong(self):
        '''
        A registered user signs in with wrong credentials
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'email@example.com',
                    'password': 'wrong_password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0045_registered_user_signin(self):
        '''
        A registered user signs in with correct credentials
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Now sign in with the correct password
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

    @with_transaction()
    def test_0050_recent_signins_auto_proceed(self):
        '''
        Recent signings can have an automatic proceed
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Now sign in with the correct password
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))
            rv = c.get('/en/checkout/sign-in')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

    # ##################################
    # 100 Test the Shipping Address Step
    # ##################################

    @with_transaction()
    def test_0105_no_skip_signin(self):
        '''
        Ensure that guest orders cant directly skip to enter shipping address
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/shipping-address')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/sign-in'))

    @with_transaction()
    def test_0110_guest_get_address_page(self):
        '''
        Guest user goes to shipping address after sign-in
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })

            # Sign-in and expect the redirect to shipping-address
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Shipping address page gets rendered
            rv = c.get('/en/checkout/shipping-address')
            self.assertEqual(rv.status_code, 200)

    @with_transaction()
    def test_0120_guest_adds_address(self):
        '''
        The guest user goes to shipping address after sign-in
        and adds an address
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

            # Assert that just one address was created
            party, = Party.search([
                ('contact_mechanisms.value', '=', 'new@example.com'),
                ('contact_mechanisms.type', '=', 'email')
                ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, 'Musterstr. 26')

            self.assertEqual(
                len(Sale.search([('shipment_address', '=', address.id)])),
                1)

            # Post another address again
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'zip': '682013',
                    'city': 'Cochin',
                    'country': country.id,
                    'subdivision': subdivision.id,
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            # Assert that the same address was updated and a new one
            # was not created
            party, = Party.search([
                ('contact_mechanisms.value', '=', 'new@example.com'),
                ('contact_mechanisms.type', '=', 'email')
                ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, '2J Skyline Daffodil')

            self.assertEqual(
                len(Sale.search([('shipment_address', '=', address.id)])),
                1)

    @with_transaction()
    def test_0130_guest_misuse_existing_address(self):
        '''
        A guest user tries to corrupt the system by sending
        an existing address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Country = pool.get('country.country')
        Address = pool.get('party.address')

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
        country = Country.search([])[0]

        address, = Address.search([], limit=1)

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

            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'address': address.id
                    })
            self.assertEqual(rv.status_code, 200)
            form_errors = literal_eval(rv.data.decode('utf-8'))
            self.assertTrue('street' in form_errors)

            self.assertEqual(
                len(Sale.search([('shipment_address', '=', None)])), 1)

    @with_transaction()
    def test_0140_registered_user_with_new_address(self):
        '''
        A registered user creates a new address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                    })

            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'name': 'Max Mustermann',
                    'street': 'Musterstr. 26',
                    'zip': '79852',
                    'city': 'Musterstadt',
                    'phone': '1234567891',
                    'country': country.id,
                    'subdivision': subdivision.id,
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            # Assert that just one address was created
            user, = NereidUser.search([
                    ('email', '=', 'email@example.com'),
                    ])
            addresses = Address.search([
                    ('party', '=', user.party.id),
                    ('street', '=', 'Musterstr. 26'),
                    ('phone', '=', '1234567891'),
                    ])

            self.assertEqual(len(addresses), 1)

            sales = Sale.search([
                    ('shipment_address', '=', addresses[0].id)
                    ])
            self.assertEqual(len(sales), 1)

            # Post another address again, which should create another
            # address
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'zip': '682013',
                    'city': 'Cochin',
                    'phone': '1234567891',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))
            # Assert that the address was created as another one
            addresses = Address.search([
                    ('party', '=', user.party.id),
                    ('street', 'in', (
                        'Musterstr. 26', '2J Skyline Daffodil')),
                    ])
            self.assertEqual(len(addresses), 2)

            # Assert the new address is now the shipment_address
            address, = Address.search([
                    ('party', '=', user.party.id),
                    ('street', '=', '2J Skyline Daffodil'),
                    ])
            sales = Sale.search([
                    ('shipment_address', '=', address.id),
                    ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0150_registered_user_with_existing_address(self):
        '''
        A registered user uses one of his existing addresses
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        # The setup creates an address, add another one
        Address.create([{
                    'party': registered_user.party.id,
                    'name': 'New Address',
                    }])
        addresses = Address.search([
                ('party', '=', registered_user.party.id),
                ])
        self.assertEqual(len(addresses), 2)

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Set the first address as shipment address
            rv = c.post(
                '/en/checkout/shipping-address',
                data={'address': addresses[0].id}
                )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))
            sales = Sale.search([
                    ('shipment_address', '=', addresses[0].id),
                    ])
            self.assertEqual(len(sales), 1)

            # Set the second address as shipment address
            rv = c.post('/en/checkout/shipping-address',
                data={'address': addresses[1].id}
                )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))
            sales = Sale.search([
                    ('shipment_address', '=', addresses[1].id),
                    ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0160_registered_user_wrong_address(self):
        '''
        A registered user tries to use someone else's address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        addresses = Address.search([
                ('party', '!=', registered_user.party.id),
                ])

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })

            # Set the first address not belonging to the user
            # as shipment address
            rv = c.post(
                '/en/checkout/shipping-address',
                data={'address': addresses[0].id}
            )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address')
            )
            sales = Sale.search([
                ('shipment_address', '=', None)]
            )
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0170_guest_edits_shipping_address(self):
        '''
        A guest user wants to edit the shipping address in the checkout step
        '''
        pool = Pool()
        Country = pool.get('country.country')

        Checkout = pool.get('nereid.checkout')
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

            # Sign-in and expect the redirect to shipping-address
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'zip': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
            }
            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data=address_data)
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            rv = c.get('/en/checkout/shipping-address')
            render_obj = Checkout.shipping_address()
            self.assertTrue(render_obj)

            self.assertTrue(render_obj.context['address_form'])
            address_form = render_obj.context['address_form']
            self.assertEqual(address_form.name.data, address_data['name'])
            self.assertEqual(
                address_form.street.data, address_data['street'])
            self.assertEqual(address_form.city.data, address_data['city'])
            self.assertEqual(
                address_form.country.data, address_data['country'])

    # ##################################
    # 200 Test the Delivery Method Step
    # ##################################

    @with_transaction()
    def test_0205_guest_no_skip_signin(self):
        '''
        Ensure that guest orders cant directly skip to enter shipping address
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/delivery-method')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/sign-in'))

    @with_transaction()
    def test_0210_guest_signedin_no_skip_shipping_address(self):
        '''
        Ensure that guest orders cant directly skip to enter shipping address
        '''
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

            # Redirect to shipping address since there is no address
            # and shipment method can't be selected without a delivery
            # address
            rv = c.get('/en/checkout/delivery-method')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

    # ##################################
    # 300 Test the Billing Address Step
    # ##################################

    @with_transaction()
    def test_0305_guest_no_skip_signin(self):
        '''
        Ensure that guest orders can't directly skip to enter billing address
        '''
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

        app = self.get_app()
        with app.test_client() as c:
            c.post('/en/cart/add',
                data={
                    'product': product1.id,
                    'quantity': quantity,
                    })
            rv = c.get('/en/checkout/billing-address')
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/sign-in'))

    @with_transaction()
    def test_0320_guest_adds_address(self):
        '''
        The guest user goes to billing address after sign-in
        and adds an address
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

            # Shipping address page gets rendered
            rv = c.post('/en/checkout/billing-address',
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
                rv.location.endswith('/en/checkout/delivery-method'))

            # Assert that just one address was created
            party, = Party.search([
                        ('name', 'ilike', '%new@example.com%'),
                        ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, 'Musterstr. 26')

            self.assertEqual(
                len(Sale.search([('invoice_address', '=', address.id)])), 1)

            # Post the address again
            rv = c.post('/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'zip': '682013',
                    'city': 'Cochin',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/delivery-method'))

            # Assert that the same address was updated and a new one
            # was not created
            party, = Party.search([
                ('name', 'ilike', '%new@example.com%')
            ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, '2J Skyline Daffodil')

            self.assertEqual(
                len(Sale.search([('invoice_address', '=', address.id)])), 1)

    @with_transaction()
    def test_0330_guest_misuse_existing_address(self):
        '''
        A guest user tries to corrupt the system by sending
        an existing address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Country = pool.get('country.country')
        Address = pool.get('party.address')

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
        country = Country.search([])[0]

        address, = Address.search([], limit=1)

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

            # Billing address page gets rendered
            rv = c.post('/en/checkout/billing-address',
                data={
                    'address': address.id
                    })
            self.assertEqual(rv.status_code, 200)
            form_errors = literal_eval(rv.data.decode('utf-8'))
            self.assertTrue('street' in form_errors)

            self.assertEqual(
                len(Sale.search([('invoice_address', '=', None)])), 1)

    @with_transaction()
    def test_0340_registered_user_with_new_address(self):
        '''
        A registered user creates a new address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                    })

            # Billing address page gets rendered
            rv = c.post('/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': 'Musterstr. 26',
                    'zip': '79852',
                    'city': 'Musterstadt',
                    'phone': '1234567891',
                    'country': country.id,
                    'subdivision': subdivision.id,
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/delivery-method'))

            # Assert that just one address was created
            user, = NereidUser.search([
                    ('email', '=', 'email@example.com'),
                    ])
            addresses = Address.search([
                    ('party', '=', user.party.id),
                    ('street', '=', 'Musterstr. 26'),
                    ('phone', '=', '1234567891'),
                    ])

            self.assertEqual(len(addresses), 1)

            sales = Sale.search([
                    ('invoice_address', '=', addresses[0].id)
                    ])
            self.assertEqual(len(sales), 1)

            # Post another address again, which should create another
            # address
            rv = c.post('/en/checkout/billing-address',
                data={
                    'name': 'Max Mustermann',
                    'street': '2J Skyline Daffodil',
                    'zip': '682013',
                    'city': 'Cochin',
                    'phone': '1234567891',
                    'country': country.id,
                    'subdivision': subdivision.id,
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/delivery-method'))

            # Assert that the address was created as another one
            addresses = Address.search([
                    ('party', '=', user.party.id),
                    ('street', 'in', (
                        'Musterstr. 26', '2J Skyline Daffodil')),
                    ])
            self.assertEqual(len(addresses), 2)

            # Assert the new address is now the invoice_address
            address, = Address.search([
                    ('party', '=', user.party.id),
                    ('street', '=', '2J Skyline Daffodil'),
                    ])
            sales = Sale.search([
                    ('invoice_address', '=', address.id),
                    ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0350_registered_user_with_existing_address(self):
        '''
        A registered user uses one of his existing addresses
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        # The setup creates an address, add another one
        Address.create([{
                    'party': registered_user.party.id,
                    'party_name': 'New Address',
                    }])
        addresses = Address.search([
                ('party', '=', registered_user.party.id),
                ])
        self.assertEqual(len(addresses), 2)

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            # Set the first address as billing address
            rv = c.post('/en/checkout/billing-address',
                data={
                    'address': addresses[0].id,
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/delivery-method'))
            sales = Sale.search([
                    ('invoice_address', '=', addresses[0].id),
                    ])
            self.assertEqual(len(sales), 1)

            # Set the second address as billing address
            rv = c.post('/en/checkout/billing-address',
                data={'address': addresses[1].id}
                )
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/delivery-method'))
            sales = Sale.search([
                    ('invoice_address', '=', addresses[1].id),
                    ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0360_registered_user_wrong_address(self):
        '''
        A registered user tries to use someone else's address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        addresses = Address.search([
                ('party', '!=', registered_user.party.id),
                ])

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })

            # Set the first address not belonging to the user
            # as billing address
            rv = c.post('/en/checkout/billing-address',
                data={
                    'address': addresses[0].id,
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/billing-address')
            )
            sales = Sale.search([
                ('invoice_address', '=', None)]
            )
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0370_guest_user_use_delivery_as_billing(self):
        '''
        A guest user uses the shipping address as billing address
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

            # Post to delivery-address with flag use_shipment_address
            rv = c.post('/en/checkout/billing-address',
                data={
                    'use_shipment_address': 'True',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(rv.location.endswith('/en/checkout/payment'))

            # Assert that just one address was created
            party, = Party.search([
                ('contact_mechanisms.value', '=', 'new@example.com'),
                ('contact_mechanisms.type', '=', 'email')
            ])
            self.assertTrue(party)
            self.assertEqual(len(party.addresses), 1)

            address, = party.addresses
            self.assertEqual(address.street, 'Musterstr. 26')

            sales = Sale.search([
                ('shipment_address', '=', address.id),
                ('invoice_address', '=', address.id),
            ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0380_registered_user_use_delivery_as_billing(self):
        '''
        A registered user uses the shipping address as billing address
        '''
        pool = Pool()
        Sale = pool.get('sale.sale')
        Address = pool.get('party.address')
        NereidUser = pool.get('nereid.user')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        # The setup creates an address, add another one
        Address.create([{
                    'party': registered_user.party.id,
                    'party_name': 'New Address',
                    }])
        addresses = Address.search([
                ('party', '=', registered_user.party.id),
                ])
        self.assertEqual(len(addresses), 2)

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
                    'email': 'email@example.com',
                    'password': 'password',
                    'checkout_mode': 'account',
                })
            self.assertEqual(rv.status_code, 302)

            # Set the first address as shipping address
            rv = c.post('/en/checkout/shipping-address',
                data={
                    'address': addresses[0].id,
                    })
            self.assertEqual(rv.status_code, 302)

            # Post to delivery-address with flag use_shipment_address
            rv = c.post('/en/checkout/billing-address',
                data={
                    'use_shipment_address': 'True',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/payment'))
            sales = Sale.search([
                    ('shipment_address', '=', addresses[0].id),
                    ('invoice_address', '=', addresses[0].id),
                    ])
            self.assertEqual(len(sales), 1)

    @with_transaction()
    def test_0390_guest_edits_billing_address(self):
        '''
        A guest user wants to edit the billing address in the checkout step
        '''
        pool = Pool()
        Country = pool.get('country.country')
        Checkout = pool.get('nereid.checkout')

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

            # Sign-in and expect the redirect to shipping-address
            rv = c.post('/en/checkout/sign-in',
                data={
                    'email': 'new@example.com',
                    'checkout_mode': 'guest',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/shipping-address'))

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'zip': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
            }
            # Shipping address page gets rendered
            rv = c.post('/en/checkout/shipping-address',
                data=address_data)
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/validate-address'))

            # Post to delivery-address with same flag
            rv = c.post('/en/checkout/billing-address',
                data={
                    'use_shipment_address': 'True',
                    })
            self.assertEqual(rv.status_code, 302)
            self.assertTrue(
                rv.location.endswith('/en/checkout/payment'))

            rv = c.get('/en/checkout/billing-address')
            render_obj = Checkout.billing_address()
            self.assertTrue(render_obj)

            self.assertTrue(render_obj.context['address_form'])
            address_form = render_obj.context['address_form']
            self.assertEqual(address_form.name.data, address_data['name'])
            self.assertEqual(
                address_form.street.data, address_data['street'])
            self.assertEqual(address_form.city.data, address_data['city'])
            self.assertEqual(
                address_form.country.data, address_data['country'])

    # ##################################
    # 400 Test the generation of lson-ld
    # ##################################

    @with_transaction()
    def test_0410_test_sale_json_ld(self):
        '''
        Test the generation of json-ld for sale and sale line
        '''
        pool = Pool()
        Company = pool.get('company.company')
        Sale = pool.get('sale.sale')
        NereidUser = pool.get('nereid.user')
        Uom = pool.get('product.uom')

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

        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        uom, = Uom.search([
                ('name', '=', 'Unit'),
                ])
        party = registered_user.party
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            with Transaction().set_context(company=company.id):
                sale, = Sale.create([{
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
                            'product': product1.id,
                        }])
                    ]}])

                # Test if json-ld is successfully generated for Sale
                self.assertTrue(sale.as_json_ld())

    # ####################################
    # 500 Test the generation of addresses
    # ####################################

    @with_transaction()
    def test_0510_add_address(self):
        '''
        Add an address for the user
        '''
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]
        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # The user has one address from the setup
            self.assertEqual(len(registered_user.party.addresses), 1)

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'zip': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                'phone': '+4917612345678',
                }

            # Create a new address
            response = c.post('/en/create-address',
                data=address_data)
            self.assertEqual(response.status_code, 302)

            # Check if the user has two addresses now
            self.assertEqual(len(registered_user.party.addresses), 2)

            address = registered_user.party.addresses[1]
            self.assertEqual(address.party_name, address_data['name'])
            self.assertEqual(address.street, address_data['street'])
            self.assertEqual(address.zip, address_data['zip'])
            self.assertEqual(address.city, address_data['city'])
            self.assertEqual(address.phone, address_data['phone'])
            self.assertEqual(address.country.id, address_data['country'])
            self.assertEqual(
                address.subdivision.id, address_data['subdivision'])

    @with_transaction()
    def test_0520_edit_address(self):
        '''
        Edit an address for the user
        '''
        pool = Pool()
        Company = pool.get('company.company')
        Country = pool.get('country.country')
        NereidUser = pool.get('nereid.user')
        Address = pool.get('party.address')

        # Setup defaults
        # A gateway sets up a lot of configuration stuff (fiscalyear, chart,
        # etc.)
        website = create_website()
        website.save()
        gateway = create_payment_gateway()
        gateway.save()

        create_countries()
        countries = Country.search([])
        website.countries = countries
        website.save()
        country = countries[0]
        subdivision = country.subdivisions[0]
        registered_user, = NereidUser.search([
                ('email', '=', 'email@example.com'),
                ])
        company, = Company.search([])

        app = self.get_app()
        with app.test_client() as c:
            response = c.post(
                '/en/login',
                data={
                    'email': 'email@example.com',
                    'password': 'password',
                    })
            self.assertEqual(response.status_code, 302)  # Login success

            # The user has one address from the setup
            self.assertEqual(len(registered_user.party.addresses), 1)

            address_data = {
                'name': 'Max Mustermann',
                'street': 'Musterstr. 26',
                'zip': '79852',
                'city': 'Musterstadt',
                'country': country.id,
                'subdivision': subdivision.id,
                'phone': '+4917612345678',
                }

            existing_address = registered_user.party.addresses[0]

            response = c.get('/en/edit-address/%d' % existing_address.id)
            self.assertTrue(
                'ID:%s' % existing_address.id in response.data.decode('utf-8'))

            # POST to the existing address must update the existing address
            response = c.post('/en/edit-address/%d' % existing_address.id,
                data=address_data)
            self.assertEqual(response.status_code, 302)

            # Assert that the user still has only 1 address
            self.assertEqual(len(registered_user.party.addresses), 1)

            address = Address(existing_address.id)
            self.assertEqual(address.party_name, address_data['name'])
            self.assertEqual(address.street, address_data['street'])
            self.assertEqual(address.zip, address_data['zip'])
            self.assertEqual(address.city, address_data['city'])
            self.assertEqual(address.phone, address_data['phone'])
            self.assertEqual(address.country.id, address_data['country'])
            self.assertEqual(
                address.subdivision.id, address_data['subdivision'])


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            NereidCheckoutTestCase))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            NereidCheckoutPaymentTestCase))
    return suite
