# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import urllib.request
import urllib.parse
import urllib.error
import unittest
import base64
import json

from unittest.mock import patch, ANY, Mock

import trytond.tests.test_tryton
from trytond.tests.test_tryton import USER, with_transaction
from trytond.transaction import Transaction
from trytond.config import config
from trytond.pool import Pool
from nereid.testing import NereidTestCase
from nereid.testing import POOL as pool

from .test_common import setup_objects

from trytond.model.modelsql import SQLConstraintError
from trytond.modules.nereid import user as user_module
from trytond.sendmail import (
    sendmail_transactional, sendmail, SMTPDataManager, get_smtp_server)
import smtplib

FROM = 'no-reply@localhost'


class TestAuth(NereidTestCase):
    """
    Test Authentication Layer
    """
    def setUp(self):
        super(TestAuth, self).setUp()
        reset_from = config.get('email', 'from')
        config.set('email', 'from', FROM)
        self.addCleanup(lambda: config.set('email', 'from', reset_from))

        trytond.tests.test_tryton.activate_module('nereid')
        setup_objects(self)
        self.templates = {
            'home.jinja': '{{get_flashed_messages()}}',
            'login.jinja':
            '{{ login_form.errors }} {{get_flashed_messages()}}',
            'registration.jinja':
            '{{ form.errors }} {{get_flashed_messages()}}',
            'reset-password.jinja': '{{get_flashed_messages()}}',
            'change-password.jinja':
            '''{{ change_password_form.errors }}
            {{get_flashed_messages()}}''',
            'address-edit.jinja': 'Address Edit {{ form.errors }}',
            'address.jinja': '',
            'account.jinja': '',
            'profile.jinja': '{{ current_user.name }}',
            'emails/activation-text.jinja': 'activation-email-text',
            'emails/activation-html.jinja': 'activation-email-html',
            'emails/reset-text.jinja': 'reset-email-text',
            'emails/reset-html.jinja': 'reset-email-html',
            }

    def setup_defaults(self):
        """
        Setup the defaults
        """
        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            }])
        self.party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        self.company, = self.company_obj.create([{
            'party': self.party,
            'currency': usd,
            }])

        en, = self.language_obj.search([('code', '=', 'en')])
        currency, = self.currency_obj.search([('code', '=', 'USD')])
        locale, = self.nereid_website_locale_obj.create([{
            'code': 'en',
            'language': en,
            'currency': currency,
            }])
        self.nereid_website_obj.create([{
            'name': 'localhost',
            'company': self.company,
            'application_user': USER,
            'default_locale': locale,
            }])

    def get_template_source(self, name):
        """
        Return templates
        """

        return self.templates.get(name)

    @patch('trytond.sendmail.get_smtp_server')
    @with_transaction()
    def test_0010_register(self, get_smtp_server):
        """
        Registration must create a new party
        """
        get_smtp_server.return_value = server = Mock()
        self.setup_defaults()
        app = self.get_app()
        #with patch.object(smtplib, 'SMTP') as SMTP:
        #    SMTP.return_value = server = Mock()
        #with patch.object(
        #        trytond_sendmail, 'sendmail_transactional') as sendmail1, \
            #        patch.object(trytond_sendmail, 'SMTPDataManager') as dm1, \
            #        app.test_client() as c:
        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                patch.object(smtplib, 'SMTP') as SMTP, \
                app.test_client() as c:
            SMTP.return_value = server2 = Mock()
            get_smtp_server.return_value = server1 = Mock()

            response = c.get('/registration')
            self.assertEqual(response.status_code, 200)   # GET Request

            email_user = 'regd_user@m9s.biz'
            data = {
                'name': 'Registered User',
                'email': email_user,
                'password': 'password'
            }
            # Post with missing password
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 200)  # Form rejected

            # Test that NO email was sent
            sendmail.assert_not_called()

            data['confirm'] = 'password'
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 302)

            # Test if an email was sent
            sendmail.assert_called_once_with(
                FROM, email_user, ANY,
                datamanager=ANY)
            _, _, msg = sendmail.call_args[0]
            self.assertEqual(msg['From'], FROM)
            self.assertEqual(msg['Subject'], 'Account Activation')
            self.assertEqual(msg['To'], email_user)
            self.assertEqual(msg.get_content_type(), 'multipart/alternative')
            self.assertEqual(
                msg.get_payload(0).get_payload(), 'activation-email-text')

        parties = self.party_obj.search([('name', '=', data['name'])])

        self.assertEqual(len(parties), 1)
        self.assertEqual(len(parties[0].contact_mechanisms), 1)
        self.assertEqual(parties[0].contact_mechanisms[0].type, 'email')
        self.assertEqual(parties[0].contact_mechanisms[0].value,
            'regd_user@m9s.biz')

        with Transaction().set_context(active_test=False):
            self.assertEqual(self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())], count=True), 1)

        # Try to register the same user again (no activated user yet)
        response = c.post('/registration', data=data)
        self.assertEqual(response.status_code, 302)
        with Transaction().set_context(active_test=False):
            self.assertEqual(self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())], count=True), 2)

        # Activate one of the users
        with Transaction().set_context(active_test=False):
            user1, user2 = self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower())
                    ])
        user1.active = True
        user1.save()
        # Account of user1 must be active
        self.assertTrue(user1.active)
        self.assertEqual(self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower()),
                    ], count=True), 1)

        # Try to activate the second user
        user2.active = True
        with self.assertRaises(SQLConstraintError) as cm:
            user2.save()
        self.assertEqual(cm.exception.code, 1)
        self.assertTrue("Email must be unique in a company" in
            cm.exception.message)

        # Try to register the same user again (activated user present)
        response = c.post('/registration', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("A registration already exists with this email" in
            response.data.decode('utf-8'))

    @patch('trytond.sendmail.get_smtp_server')
    @with_transaction()
    def test_0012_register_json(self, get_smtp_server):
        """
        Registration must create a new party.

        Same as registration test but with json data
        """
        get_smtp_server.return_value = server = Mock()
        self.setup_defaults()
        app = self.get_app()

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            response = c.get('/registration')
            self.assertEqual(response.status_code, 200)   # GET Request

            data = {
                'name': 'Registered User',
                'email': 'regd_user@m9s.biz',
                'password': 'password'
                }
            # Post with missing password
            response = c.post('/registration',
                data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, 400)  # Form rejected

            data['confirm'] = 'password'
            response = c.post('/registration',
                data=json.dumps(data),
                content_type='application/json')
            self.assertEqual(response.status_code, 201)

        self.assertEqual(self.party_obj.search([('name', '=', data['name'])],
                count=True), 1)

        with Transaction().set_context(active_test=False):
            self.assertEqual(self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())], count=True), 1)

        # Try to register the same user again (no activated user yet)
        response = c.post('/registration',
            data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)

        # Activate one of the users
        with Transaction().set_context(active_test=False):
            user1, user2 = self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower())
                    ])
        user1.active = True
        user1.save()
        # Account of user1 must be active
        self.assertTrue(user1.active)
        self.assertEqual(self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower()),
                    ], count=True), 1)

        # Try to register the same user again (activated user present)
        response = c.post('/registration',
            data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertTrue("A registration already exists with this email" in
            response.data.decode('utf-8'))

    @with_transaction()
    def test_0015_match_password(self):
        """
        Assert that matching of password works
        """
        usd, = self.currency_obj.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
            }])
        party, = self.party_obj.create([{
            'name': 'MBSolutions',
            }])
        company, = self.company_obj.create([{
            'party': party,
            'currency': usd,
            }])
        registered_user_party = self.party_obj(name='Registered User')
        registered_user_party.save()
        registered_user, = self.nereid_user_obj.create([{
            'party': registered_user_party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': company,
            }])
        self.assertTrue(registered_user.match_password('password'))

    @with_transaction()
    def test_0018_verify_email(self):
        """
        Check that the verification of email is working
        """
        self.setup_defaults()
        app = self.get_app()

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            data = {
                'name': 'Registered User',
                'email': 'regd_user@m9s.biz',
                'password': 'password',
                'confirm': 'password',
            }
            data['confirm'] = 'password'
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 302)

            with Transaction().set_context(active_test=False):
                registered_user, = self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())])
            self.assertFalse(registered_user.email_verified)

            # Verify the email with invalid code
            invalid_code = "thisisinvalidcode"
            response = c.get('/verify-email/%s/%s' %
                (registered_user.id, invalid_code))
            self.assertEqual(response.status_code, 302)
            self.assertFalse(registered_user.email_verified)

            # verify the email
            response = c.get(registered_user.get_email_verification_link())
            self.assertEqual(response.status_code, 302)

            # Email should now be verified
            self.assertTrue(registered_user.email_verified)

    @with_transaction()
    def test_0020_activation(self):
        """
        Activation must happen before login is possible
        """
        self.setup_defaults()
        app = self.get_app()

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            data = {
                'name': 'Registered User',
                'email': 'regd_user@m9s.biz',
                'password': 'password',
                'confirm': 'password',
                }
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 302)

            with Transaction().set_context(active_test=False):
                registered_user, = self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())])
            self.assertFalse(registered_user.active)

            # Login should fail since there is activation code
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password'],
                    })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "Your account has not been activated yet"
                in response.data.decode('utf-8'))

            # Activate the account
            response = c.get(registered_user.get_activation_link())
            self.assertEqual(response.status_code, 302)
            registered_user = self.nereid_user_obj(registered_user.id)

            # The account must be active
            self.assertTrue(registered_user.active)
            # Email should be verified
            self.assertTrue(registered_user.email_verified)

            # Login should work
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password'],
                    })
            registered_user = self.nereid_user_obj(registered_user.id)
            self.assertEqual(response.status_code, 302)

    @with_transaction()
    def test_0030_change_password(self):
        """
        Check password changing functionality
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            # try the page without login
            response = c.get('/change-password')
            self.assertEqual(response.status_code, 302)

            # try the post without login
            response = c.post('/change-password',
                data={
                    'password': data['password'],
                    'confirm': data['password'],
                    })
            self.assertEqual(response.status_code, 302)

            # Login now
            response = c.post(
                '/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    })
            self.assertEqual(response.status_code, 302)

            # send wrong password confirm
            response = c.post('/change-password',
                data={
                    'password': 'new-password',
                    'confirm': 'password',
                    })
            self.assertEqual(response.status_code, 200)
            self.assertTrue("Passwords must match"
                in response.data.decode('utf-8'))

            # send wrong password confirm as XHR
            response = c.post('/change-password',
                data={
                    'password': 'new-password',
                    'confirm': 'password',
                    }, headers={'X-Requested-With': 'XMLHTTPRequest'})
            res = json.loads(response.data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(res['errors']['password'][0],
                "Passwords must match")
            self.assertEqual(res['errors']['old_password'][0],
                "This field is required.")

            # send correct password confirm but not old password
            response = c.post('/change-password',
                data={
                    'password': 'new-password',
                    'confirm': 'new-password'
                    })
            self.assertEqual(response.status_code, 200)

            # send correct password confirm but incorrect old password
            response = c.post('/change-password',
                data={
                    'old_password': 'passw',
                    'password': 'new-password',
                    'confirm': 'new-password'
                    })
            self.assertEqual(response.status_code, 200)
            self.assertTrue("The current password you entered is invalid"
                in response.data.decode('utf-8'))

            # send correct password confirm but incorrect old password as XHR
            response = c.post('/change-password',
                data={
                    'old_password': 'passw',
                    'password': 'new-password',
                    'confirm': 'new-password'
                    }, headers={'X-Requested-With': 'XMLHTTPRequest'})
            res = json.loads(response.data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(res['message'],
                "The current password you entered is invalid")

            response = c.post('/change-password',
                data={
                    'old_password': data['password'],
                    'password': 'new-password',
                    'confirm': 'new-password'
                    })
            self.assertEqual(response.status_code, 302)
            response = c.get('/')

            # Login now using new password
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'new-password'
                    })
            self.assertEqual(response.status_code, 302)

            # Change password with XHR
            response = c.post('/change-password',
                data={
                    'old_password': 'new-password',
                    'password': 'password',
                    'confirm': 'password'
                    }, headers={'X-Requested-With': 'XMLHTTPRequest'})
            res = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(res['message'],
                'Your password has been successfully changed! '
                    'Please login again',)

    @with_transaction()
    def test_0040_reset_account(self):
        """
        Allow resetting password of the user
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        regd_user, = self.nereid_user_obj.create([data.copy()])

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:

            # Try reset without login and page should render
            response = c.get('/reset-account')
            self.assertEqual(response.status_code, 200)

            # Try resetting password through email
            response = c.post('/reset-account',
                data={
                    'email': data['email'],
                    })
            self.assertEqual(response.status_code, 302)

            response = c.post('/reset-account',
                data={
                    'email': data['email'],
                    },
                headers={'X-Requested-With': 'XMLHTTPRequest'})
            self.assertEqual(response.status_code, 200)

            rv = c.post('/reset-account',
                data={
                    'email': 'made_up_email@test.com',
                    }, headers={'X-Requested-With': 'XMLHTTPRequest'})
            self.assertEqual(rv.status_code, 400)
            self.assertEqual(json.loads(rv.data),
                {'message': 'Invalid email address'})

            # A successful login after requesting activation code should
            # not do anything but just allow login
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password'],
                    })
            self.assertEqual(response.status_code, 302)

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            # Try to reset again - with good intentions
            response = c.post('/reset-account',
                data={
                    'email': data['email'],
                    })
            self.assertEqual(response.status_code, 302)

            # Try to reset password with invalid code
            invalid_code = 'thisistheinvalidcode'
            response = c.post(
                '/new-password/%s/%s' % (regd_user.id, invalid_code),
                data={
                    'password': 'reset-password',
                    'confirm': 'reset-password'
                    })
            self.assertEqual(response.status_code, 302)

            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'reset-password'
                    })
            self.assertEqual(response.status_code, 200)  # Login rejected

            # Reset password with valid code, but too simple password
            response = c.post(regd_user.get_reset_password_link(),
                data={
                    'password': 'aaaaaaaaa',
                    'confirm': 'aaaaaaaaa'
                    })
            self.assertEqual(response.status_code, 200) # Login rejected

            # Reset password with valid code, but complex password
            response = c.post(regd_user.get_reset_password_link(),
                data={
                    'password': 'rEset-paSswoRd',
                    'confirm': 'rEset-paSswoRd'
                    })
            self.assertEqual(response.status_code, 302)

            regd_user = self.nereid_user_obj(regd_user.id)

            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'wrong-password'
                    })
            self.assertEqual(response.status_code, 200)     # Login rejected

            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'rEset-paSswoRd'
                    })
            self.assertEqual(response.status_code, 302)     # Login approved

        with app.test_client() as c:
            # Try to reset again - with bad intentions

            # Bad request because there is no email
            response = c.post(
                '/reset-account', data={},
                headers={'X-Requested-With': 'XMLHTTPRequest'})
            self.assertEqual(response.status_code, 400)

            response = c.post('/reset-account', data={})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                'Invalid email address' in response.data.decode('utf-8'))

            # Bad request because there is empty email
            response = c.post('/reset-account', data={'email': ''})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                'Invalid email address' in response.data.decode('utf-8'))

        data = {
            'party': party,
            'name': 'User without email',
            'email': '',
            'password': 'password',
            'company': self.company,
            }
        email_less_user, = self.nereid_user_obj.create([data.copy()])
        with app.test_client() as c:
            # Bad request because there is empty email
            # this is a special case where there is an user
            # with empty email
            response = c.post('/reset-account', data={'email': ''})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                'Invalid email address' in response.data.decode('utf-8'))

    @with_transaction()
    def test_0050_logout(self):
        """
        Check for logout
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            response = c.get("/account")
            self.assertEqual(response.status_code, 302)

            # Login and check again
            response = c.post(
                '/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    })
            self.assertEqual(response.status_code, 302)

            response = c.get("/account")
            self.assertEqual(response.status_code, 200)

            response = c.get("/logout")
            self.assertEqual(response.status_code, 302)

            response = c.get("/account")
            self.assertEqual(response.status_code, 302)

    @with_transaction()
    def test_0070_gravatar(self):
        """
        Check if the gravatar is returned by the profile picture
        """
        self.setup_defaults()
        app = self.get_app()

        self.templates['home.jinja'] = """
        {{ current_user.get_profile_picture() }}
        """

        with app.test_client() as c:
            response = c.get('/')
            self.assertTrue(
                'http://www.gravatar.com/avatar/' in response.data.decode('utf-8'))

    @with_transaction()
    def test_0090_profile(self):
        """
        Test the profile functionality
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            response = c.get('/me')
            self.assertEqual(response.status_code, 302)

            # Login and check again
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    })
            response = c.get('/me')
            self.assertEqual(response.data.decode('utf-8'), data['name'])

            # Change the name of the user
            response = c.post('/me',
                data={
                    'name': 'Regd User',
                    'timezone': 'UTC',
                    'email': 'cannot@m9s.biz',
                    })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data.decode('utf-8'), 'Regd User')

    @with_transaction()
    def test_0110_user_management(self):
        """
        ensure that the cookie gets cleared if the user in session
        is invalid.
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            # Login and check again
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    })
            response = c.get('/me')
            self.assertEqual(response.data.decode('utf-8'), data['name'])

            # Delete the user
            self.nereid_user_obj.delete([nereid_user])

            response = c.get('/me')
            self.assertEqual(response.status_code, 302)

    @with_transaction()
    def test_200_basic_authentication(self):
        """
        Test if basic authentication works
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            # Login without any auth
            response = c.get('/me')
            self.assertEqual(response.status_code, 302)

            # Login with wrong basic auth
            basic_auth = base64.b64encode(b'email@example.com:oops')
            response = c.get('/me',
                headers={
                    'Authorization': 'Basic ' +
                    basic_auth.decode('utf-8').strip('\r\n')
                    })
            self.assertEqual(response.status_code, 302)

            # Send the same request with correct basic authentication
            basic_auth = base64.b64encode(b'email@example.com:password')
            response = c.get('/me',
                headers={
                    'Authorization': 'Basic ' + basic_auth.decode(
                        'utf-8').strip('\r\n')
                    })
            self.assertEqual(response.data.decode('utf-8'), data['name'])

    @with_transaction()
    def test_205_basic_authentication_with_separator(self):
        """
        Test if basic authentication works with a separator in the password
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'pass:word',
            'company': self.company,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            # Login without any auth
            response = c.get('/me')
            self.assertEqual(response.status_code, 302)

            # Send the same request with correct basic authentication
            basic_auth = base64.b64encode(b'email@example.com:pass:word')
            response = c.get('/me',
                headers={
                    'Authorization': 'Basic ' + basic_auth.decode(
                        'utf-8').strip('\r\n')
                    })
            self.assertEqual(response.data.decode('utf-8'), data['name'])

    @with_transaction()
    def test_207_login_basic_authentication_and_active_field(self):
        """
        Check if the active field stop the user from logging in.
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'pass:word',
            'company': self.company,
            'active': False,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            # Send the same request with correct basic authentication
            basic_auth = base64.b64encode(b'email@example.com:pass:word')
            headers = {
                'Authorization': 'Basic ' + basic_auth.decode(
                    'utf-8').strip('\r\n')
                }

            # By default user accounts are active. So login should
            # work.
            response = c.get('/me', headers=headers)
            self.assertEqual(response.status_code, 302)

        nereid_user.active = True
        nereid_user.save()

        with app.test_client() as c:
            # Send the same request with correct basic authentication
            basic_auth = base64.b64encode(b'email@example.com:pass:word')
            headers = {
                'Authorization': 'Basic ' + basic_auth.decode(
                    'utf-8').strip('\r\n')
                }

            # By default user accounts are active. So login should
            # work.
            response = c.get('/me', headers=headers)
            self.assertEqual(response.status_code, 200)

    @with_transaction()
    def test_0400_auth_xhr_wrong(self):
        """
        Ensure that auth in XHR sends the right results
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            self.assertEqual(c.get('/me').status_code, 302)

            rv = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'wrong'
                    },
                headers={
                    'X-Requested-With': 'XMLHTTPRequest'
                    })
            self.assertEqual(rv.status_code, 401)
            self.assertEqual(json.loads(rv.data),
                {'message': 'Bad credentials'})
            self.assertEqual(c.get('/me').status_code, 302)

    @with_transaction()
    def test_0410_auth_xhr_valid(self):
        """
        Ensure that auth in XHR sends the right results
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
        }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            self.assertEqual(c.get('/me').status_code, 302)

            rv = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    },
                headers={
                    'X-Requested-With': 'XMLHTTPRequest'
                    })
            self.assertEqual(rv.status_code, 200)
            data = json.loads(rv.data)

            self.assertTrue(data['success'])
            self.assertTrue('user' in data)

            self.assertEqual(c.get('/me').status_code, 200)

    @with_transaction()
    def test_0430_remember_me(self):
        """
        Ensure that remember me in login is working
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        nereid_user, = self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            response = c.post('/login',
                data={
                    'email': data['email'], 'password': data['password'],
                    'remember': ''
                    })
            self.assertEqual(response.status_code, 302)

            response = c.get('/me')
            self.assertEqual(response.status_code, 200)

            with c.session_transaction() as sess:
                sess.clear()

            response = c.get("/me")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(urllib.parse.unquote(response.location),
                    'http://localhost/login?next=/me')

            response = c.post('/login',
                data={
                    'email': data['email'], 'password': data['password'],
                    'remember': 'True'
                    })
            self.assertEqual(response.status_code, 302)

            response = c.get("/me")
            self.assertEqual(response.status_code, 200)

            with c.session_transaction() as sess:
                sess.clear()

            response = c.get("/me")
            self.assertEqual(response.status_code, 200)

    @with_transaction()
    def test_0450_login_with_case_sensitive_emails(self):
        """
        Check for login with case sensitive emails
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        self.nereid_user_obj.create([data.copy()])

        with app.test_client() as c:
            response = c.get("/account")
            self.assertEqual(response.status_code, 302)

            # Login with original email
            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': data['password']
                    })
            self.assertEqual(response.status_code, 302)

            response = c.get("/account")
            self.assertEqual(response.status_code, 200)

            response = c.get("/logout")
            self.assertEqual(response.status_code, 302)

            # Logged out user cannot open account page
            response = c.get("/account")
            self.assertEqual(response.status_code, 302)

            # Login with emails in upper case
            response = c.post('/login',
                data={
                    'email': data['email'].upper(),
                    'password': data['password']
                    })
            self.assertEqual(response.status_code, 302)

            response = c.get("/account")
            self.assertEqual(response.status_code, 200)

            response = c.get("/logout")
            self.assertEqual(response.status_code, 302)

    @patch('trytond.sendmail.get_smtp_server')
    @with_transaction()
    def test_0500_register_with_case_sensitive_emails(self, get_smtp_server):
        """
        Registration with case sensitive emails should not be allowed
        """
        get_smtp_server.return_value = server = Mock()
        self.setup_defaults()
        app = self.get_app()

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            response = c.get('/registration')
            self.assertEqual(response.status_code, 200)   # GET Request

            data = {
                'name': 'Registered User',
                'email': 'regd_user@m9s.biz',
                'password': 'password',
                'confirm': 'password'
                }
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 302)

        parties = self.party_obj.search([('name', '=', data['name'])])

        self.assertEqual(len(parties), 1)
        self.assertEqual(len(parties[0].contact_mechanisms), 1)
        self.assertEqual(parties[0].contact_mechanisms[0].type, 'email')
        self.assertEqual(parties[0].contact_mechanisms[0].value,
            'regd_user@m9s.biz')

        with Transaction().set_context(active_test=False):
            self.assertEqual(self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())],
                    count=True), 1)

        # User try to register with same email in different case.
        with app.test_client() as c:
            data['email'] = data['email'].upper()
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 302)
        # Email should be coerced to lower case
        with Transaction().set_context(active_test=False):
            self.assertEqual(self.nereid_user_obj.search(
                    [('email', '=', data['email'].lower())],
                    count=True), 2)

        # Activate one of the users
        with Transaction().set_context(active_test=False):
            user1, user2 = self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower())
                    ])
        user1.active = True
        user1.save()
        # Account of user1 must be active
        self.assertTrue(user1.active)
        self.assertEqual(self.nereid_user_obj.search([
                    ('email', '=', data['email'].lower()),
                    ], count=True), 1)

        # Try to register again with same email in different case.
        with app.test_client() as c:
            data['email'] = data['email'].upper()
            response = c.post('/registration', data=data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(
                "A registration already exists with this email" in
                response.data.decode('utf-8'))

    @with_transaction()
    def test_0550_reset_password_with_case_sensitive_emails(self):
        """Test reset password works with case sensitive emails as well
        """
        self.setup_defaults()
        app = self.get_app()

        party, = self.party_obj.create([{'name': 'Registered user'}])
        data = {
            'party': party,
            'name': 'Registered User',
            'email': 'email@example.com',
            'password': 'password',
            'company': self.company,
            }
        regd_user, = self.nereid_user_obj.create([data.copy()])

        with patch.object(
                user_module, 'sendmail_transactional') as sendmail, \
                patch.object(user_module, 'SMTPDataManager') as dm, \
                app.test_client() as c:
            # Reset email with original email
            response = c.post('/reset-account',
                data={
                    'email': data['email'],
                    })
            self.assertEqual(response.status_code, 302)

            # Reset password with valid code
            response = c.post(regd_user.get_reset_password_link(),
                data={
                    'password': 'rEset-paSswoRd',
                    'confirm': 'rEset-paSswoRd'
                    })
            self.assertEqual(response.status_code, 302)

            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'rEset-paSswoRd'
                    })
            self.assertEqual(response.status_code, 302)     # Login approved

            # Reset email with case sensitive email
            response = c.post('/reset-account',
                data={
                    'email': data['email'].upper(),
                    })
            self.assertEqual(response.status_code, 302)

            # Reset password with valid code
            response = c.post(regd_user.get_reset_password_link(),
                data={
                    'password': 'new-password',
                    'confirm': 'new-password'
                    })
            self.assertEqual(response.status_code, 302)

            response = c.post('/login',
                data={
                    'email': data['email'],
                    'password': 'new-password'
                    })
            self.assertEqual(response.status_code, 302)     # Login approved


def suite():
    "Nereid Authentication test suite"
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAuth))
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

