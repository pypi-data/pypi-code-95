# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import hashlib
import random
import string
import urllib.request
import urllib.parse
import urllib.error
import base64
import warnings
import pytz

from sql.conditionals import Coalesce
from sql.operators import Concat, Equal

from flask_wtf import FlaskForm as Form, RecaptchaField
from wtforms import StringField, SelectField, validators, PasswordField
from flask_login import logout_user, AnonymousUserMixin, login_url, \
    login_user
from werkzeug.utils import redirect
from werkzeug.exceptions import abort

from nereid import request, url_for, render_template, login_required, flash, \
    jsonify, route, current_website, current_user
from nereid.ctx import has_request_context
from nereid.globals import current_app
from nereid.signals import registration
from nereid.templating import render_email

from trytond.model import (ModelView, ModelSQL, DeactivableMixin, fields,
    Exclude)
from trytond.pool import Pool
from trytond.pyson import Eval, Bool, Not
from trytond.transaction import Transaction
from trytond.config import config
from trytond.rpc import RPC
from trytond.res.user import CRYPT_CONTEXT, PasswordError
from trytond.sendmail import sendmail_transactional, SMTPDataManager

from itsdangerous import URLSafeSerializer, TimestampSigner, SignatureExpired, \
    BadSignature, TimedJSONWebSignatureSerializer
from nereid.contrib.locale import make_lazy_gettext

try:
    import bcrypt
except ImportError:
    bcrypt = None


_ = make_lazy_gettext('nereid')

_from = config.get('email', 'from', default='no-reply@localhost')


class RegistrationForm(Form):
    "Simple Registration form"
    name = StringField(_('Name'), [validators.DataRequired(), ])
    email = StringField(_('e-mail'), [validators.DataRequired(), validators.Email()])  # noqa
    password = PasswordField(_('Password'), [
        validators.DataRequired(),
        validators.EqualTo('confirm', message=_('Passwords must match'))])
    confirm = PasswordField(_('Confirm Password'),
        [validators.DataRequired(), ],
        )

    if config.has_option('nereid', 're_captcha_public_key') and \
            config.has_option('nereid', 're_captcha_private_key'):
        captcha = RecaptchaField(
            public_key=config.get('nereid', 're_captcha_public_key'),
            private_key=config.get('nereid', 're_captcha_private_key'),
            secure=True
        )


class NewPasswordForm(Form):
    """
    Form to set a new password
    """
    password = PasswordField(_('New Password'), [
        validators.DataRequired(),
        validators.EqualTo('confirm', message=_('Passwords must match'))])
    confirm = PasswordField(_('Repeat Password'))


class ChangePasswordForm(NewPasswordForm):
    """
    Form to change the password
    """
    old_password = PasswordField(_('Old Password'), [validators.DataRequired()])


STATES = {
    'readonly': Not(Bool(Eval('active'))),
}


class ProfileForm(Form):
    """User Profile Form"""
    name = StringField(
        'Name', [validators.DataRequired(), ],
        description="Your name"
    )
    timezone = SelectField(
        'Timezone',
        choices=[(tz, tz) for tz in pytz.common_timezones],
        coerce=str, description="Your timezone"
    )
    email = StringField(
        'Email', [validators.DataRequired(), validators.Email()],
        description="Your Login Email. This cannot be edited."
    )


class ResetAccountForm(Form):
    """Reset Account Form"""
    email = StringField(
        'Email', [validators.DataRequired(), validators.Email()],
        description="Your Login Email."
    )


class NereidUser(DeactivableMixin, ModelSQL, ModelView):
    """
    Nereid Users
    """
    __name__ = "nereid.user"
    _rec_name = 'name'

    party = fields.Many2One('party.party', 'Party', required=True,
        ondelete='CASCADE')
    name = fields.Char('Name')
    email = fields.Char("E-Mail", select=1)
    password_hash = fields.Char('Password Hash')
    password = fields.Function(
        fields.Char('Password'), 'get_password', setter='set_password')
    # The company of the website(s) to which the user is affiliated. This
    # allows websites of the same company to share authentication/users. It
    # does not make business or technical sense to have website of multiple
    # companies share the authentication.
    #
    # .. versionchanged:: 0.3
    #     Company is mandatory
    company = fields.Many2One('company.company', 'Company', required=True)
    timezone = fields.Selection(
        [(x, x) for x in pytz.common_timezones], 'Timezone', translate=False)
    email_verified = fields.Boolean("Email Verified")

    # .. versionchanged:: 5.2
    #     Remove deprecated display_name

    @classmethod
    def __setup__(cls):
        super(NereidUser, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('email_exclude',
                Exclude(table, (table.email, Equal), (table.company, Equal),
                    where=table.active == True),
                'nereid.msg_user_email_unique'),
            ]
        cls.__rpc__.update({
            'match_password': RPC(readonly=True, instantiate=0),
        })

    @classmethod
    def __register__(cls, module_name):
        cursor = Transaction().connection.cursor()
        super(NereidUser, cls).__register__(module_name)
        table = cls.__table_handler__(module_name)

        # Migration from 4.0
        if table.column_exist('password') and table.column_exist('salt'):
            sqltable = cls.__table__()
            password_hash_new = Concat('sha1$', Concat(sqltable.password,
                Concat('$', Coalesce(sqltable.salt, ''))))
            cursor.execute(*sqltable.update(
                columns=[sqltable.password_hash],
                values=[password_hash_new]))
            table.drop_column('password')
            table.drop_column('salt')
        # Migration from 5.2.23: Replace Unique by Exclude constraint
        table.drop_constraint('unique_email_company')

    @classmethod
    def search_rec_name(cls, name, clause):
        return ['OR',
            ('party',) + tuple(clause[1:]),
            ('name',) + tuple(clause[1:]),
            ('email',) + tuple(clause[1:]),
        ]

    @staticmethod
    def default_email_verified():
        return False

    @staticmethod
    def default_active():
        """
        If the user gets created from the web the activation should happen
        through the activation link. However, users created from tryton
        interface are activated by default
        """
        if has_request_context():
            return False
        return True

    def get_password(self, name):
        return 'x' * 10

    @classmethod
    def set_password(cls, users, name, value):
        pool = Pool()
        User = pool.get('res.user')

        if value == 'x' * 10:
            return

        if Transaction().user and value:
            User.validate_password(value, users)

        to_write = []
        for user in users:
            to_write.extend([[user], {
                        'password_hash': cls.hash_password(value),
                        }])
        cls.write(*to_write)

    @classmethod
    def hash_password(cls, password):
        '''Hash given password in the form
        <hash_method>$<password>$<salt>...'''
        if not password:
            return ''
        return CRYPT_CONTEXT.hash(password)

    @classmethod
    def check_password(cls, password, hash_):
        if not hash_:
            return False, None
        try:
            return CRYPT_CONTEXT.verify_and_update(password, hash_)
        except ValueError:
            hash_method = hash_.split('$', 1)[0]
            warnings.warn(
                "Use of deprecated hash method %s" % hash_method,
                DeprecationWarning)
            valid = getattr(cls, 'check_' + hash_method)(password, hash_)
            if valid:
                new_hash = CRYPT_CONTEXT.hash(password)
            else:
                new_hash = None
            return valid, new_hash

    @classmethod
    def hash_sha1(cls, password):
        salt = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        salted_password = password + salt
        if isinstance(salted_password, str):
            salted_password = salted_password.encode('utf-8')
        hash_ = hashlib.sha1(salted_password).hexdigest()
        return '$'.join(['sha1', hash_, salt])

    @classmethod
    def check_sha1(cls, password, hash_):
        if isinstance(password, str):
            password = password.encode('utf-8')
        hash_method, hash_, salt = hash_.split('$', 2)
        salt = salt or ''
        if isinstance(salt, str):
            salt = salt.encode('utf-8')
        assert hash_method == 'sha1'
        return hash_ == hashlib.sha1(password + salt).hexdigest()

    @classmethod
    def hash_bcrypt(cls, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        hash_ = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
        return '$'.join(['bcrypt', hash_])

    @classmethod
    def check_bcrypt(cls, password, hash_):
        if isinstance(password, str):
            password = password.encode('utf-8')
        hash_method, hash_ = hash_.split('$', 1)
        if isinstance(hash_, str):
            hash_ = hash_.encode('utf-8')
        assert hash_method == 'bcrypt'
        return hash_ == bcrypt.hashpw(password, hash_)

    def match_password(self, password):
        """
        Checks if 'password' is the same as the current users password.

        :param password: The password of the user
        :return: True or False
        """
        valid, new_hash = self.__class__.check_password(
            password, self.password_hash)
        if valid:
            if new_hash:
                current_app.logger.debug(
                    "Update password hash for nereid user ID %s", self.id)
                with Transaction().new_transaction() as transaction:
                    with transaction.set_user(0):
                        self.password_hash = new_hash
                        self.save()
            return True
        return False

    @classmethod
    def _format_email(cls, users):
        for user in users:
            if user.email:
                email = user.email.lower()
                if email != user.email:
                    user.email = email
        cls.save(users)

    @classmethod
    def create(cls, vlist):
        users = super(NereidUser, cls).create(vlist)
        cls._format_email(users)
        return users

    @classmethod
    def write(cls, *args):
        super(NereidUser, cls).write(*args)
        users = sum(args[0:None:2], [])
        cls._format_email(users)

    def serialize(self, purpose=None):
        """
        Return a JSON serializable object that represents this record
        """
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
        }

    @staticmethod
    def default_timezone():
        return "UTC"

    @staticmethod
    def default_company():
        return Transaction().context.get('company') or False

    @property
    def _signer(self):
        return TimestampSigner(current_app.secret_key)

    @property
    def _serializer(self):
        return URLSafeSerializer(current_app.secret_key)

    def _get_sign(self, salt):
        """
        Returns a timestampsigned, url_serialized sign  with a salt
        'verification'.
        """
        return self._signer.sign(self._serializer.dumps(self.id, salt=salt))

    def get_email_verification_link(self, **options):
        """
        Returns an email verification link for the user
        """
        return url_for(
            'nereid.user.verify_email',
            sign=self._get_sign('verification'),
            active_id=self.id,
            **options
        )

    def get_activation_link(self, **options):
        """
        Returns an activation link for the user
        """
        return url_for(
            'nereid.user.activate',
            sign=self._get_sign('activation'),
            active_id=self.id,
            **options
        )

    def get_reset_password_link(self, **options):
        """
        Returns a password reset link for the user
        """
        return url_for(
            'nereid.user.new_password',
            sign=self._get_sign('reset-password'),
            active_id=self.id,
            **options
        )

    @classmethod
    def build_response(cls, message, response, xhr_status_code):
        """
        Method to handle response for jinja and XHR requests.

        message: Message to show as flash and send as json response.
        response: redirect or render_template method.
        xhr_status_code: Status code to be sent with json response.
        """
        if request.is_xhr or request.is_json:
            return jsonify(message=str(message)), xhr_status_code
        flash(message)
        return response

    @route("/verify-email/<int:active_id>/<sign>", methods=["GET"],
        readonly=False)
    def verify_email(self, sign, max_age=24 * 60 * 60):
        """
        Verifies the email and redirects to home page. This is a method in
        addition to the activate method which activates the account in addition
        to verifying the email.
        """
        try:
            unsigned = self._serializer.loads(
                self._signer.unsign(sign, max_age=max_age),
                salt='verification'
            )
        except SignatureExpired:
            return self.build_response(
                _('The verification link has expired'),
                redirect(url_for('nereid.website.home')), 400
            )
        except BadSignature:
            return self.build_response(
                _('The verification token is invalid!'),
                redirect(url_for('nereid.website.home')), 400
            )
        else:
            if self.id == unsigned:
                self.email_verified = True
                self.save()
                return self.build_response(
                    _('Your email has been verified!'),
                    redirect(url_for('nereid.website.home')), 200
                )
            else:
                return self.build_response(
                    _('The verification token is invalid!'),
                    redirect(url_for('nereid.website.home')), 400
                )

    @staticmethod
    def get_registration_form():
        """
        Returns a registration form for use in the site

        .. tip::

            Configuration of re_captcha

            Remember to forward X-Real-IP in the case of Proxy servers

        """
        # Add re_captcha if the configuration has such an option
        if config.has_option('nereid', 're_captcha_public_key'):
            registration_form = RegistrationForm(
                captcha={'ip_address': request.remote_addr}
            )
        else:
            registration_form = RegistrationForm()

        return registration_form

    @classmethod
    @route("/registration", methods=["GET", "POST"])
    def registration(cls):
        """
        Invokes registration of an user
        """
        pool = Pool()
        Party = pool.get('party.party')
        ContactMechanism = pool.get('party.contact_mechanism')

        registration_form = cls.get_registration_form()

        if registration_form.validate_on_submit():
            emails = cls.search([
                ('email', '=', registration_form.email.data.lower()),
                ('company', '=', current_website.company.id),
            ])
            if emails:
                message = _(
                    'A registration already exists with this email. '
                    'Please contact customer care'
                )
                if request.is_xhr or request.is_json:
                    return jsonify(message=str(message)), 400
                else:
                    flash(message)
            else:
                party = Party(name=registration_form.name.data)
                party.addresses = []
                party.contact_mechanisms = [
                    ContactMechanism(
                        type="email",
                        value=registration_form.email.data
                    )
                ]
                party.save()
                nereid_user = cls(**{
                    'party': party.id,
                    'name': registration_form.name.data,
                    'email': registration_form.email.data,
                    'password': registration_form.password.data,
                    'company': current_website.company.id,
                }
                )
                # Catch exceptions raised by password validation
                try:
                    nereid_user.save()
                except PasswordError as e:
                    return cls.build_response(e,
                        render_template('registration.jinja',
                            form=registration_form), 400)
                registration.send(nereid_user)
                nereid_user.send_activation_email()
                message = _(
                    'Registration Complete. Check your email for activation'
                )
                if request.is_xhr or request.is_json:
                    return jsonify(message=str(message)), 201
                else:
                    flash(message)
                return redirect(
                    request.args.get('next', url_for('nereid.website.home'))
                )

        if registration_form.errors and (request.is_xhr or request.is_json):
            return jsonify({
                'message': str(_('Form has errors')),
                'errors': registration_form.errors,
            }), 400

        return render_template('registration.jinja', form=registration_form)

    def send_email(self, message):
        """
        Generic method to call sendmail_transactional
        """
        datamanager = SMTPDataManager()
        Transaction().join(datamanager)
        if self.email:
            sendmail_transactional(_from, self.email, message,
                datamanager=datamanager)

    def send_activation_email(self):
        """
        Send an activation email to the user

        :param nereid_user: The browse record of the user
        """
        email_message = render_email(
            _from,
            self.email, _('Account Activation'),
            text_template='emails/activation-text.jinja',
            html_template='emails/activation-html.jinja',
            nereid_user=self
        )
        self.send_email(email_message)

    def get_magic_login_link(self, **options):
        """
        Returns a direct login link for user
        """
        return url_for(
            'nereid.user.magic_login',
            sign=self._get_sign('magic-login'),
            active_id=self.id,
            **options
        )

    @classmethod
    @route('/send-magic-link/<email>', methods=['GET'], readonly=False)
    def send_magic_login_link(cls, email):
        """
        Send a magic login email to the user
        """
        try:
            nereid_user, = cls.search([
                ('email', '=', email.lower()),
                ('company', '=', current_website.company.id),
            ])
        except ValueError:
            # This email was not found so, let user know about this
            message = "No user with email %s was found!" % email
            current_app.logger.debug(message)
        else:
            message = "Please check your mail and follow the link"
            email_message = render_email(
                _from,
                email, _('Magic Signin Link'),
                text_template='emails/magic-login-text.jinja',
                html_template='emails/magic-login-html.jinja',
                nereid_user=nereid_user
            )
            nereid_user.send_email(email_message)

        return cls.build_response(
            message, redirect(url_for('nereid.website.home')), 200
        )

    @route(
        "/magic-login/<int:active_id>/<sign>",
        methods=["GET"], readonly=False
    )
    def magic_login(self, sign, max_age=5 * 60):
        """
        Let the user log in without password if the token
        is valid (less than 5 min old)
        """
        try:
            unsigned = self._serializer.loads(
                self._signer.unsign(sign, max_age=max_age),
                salt='magic-login'
            )
        except SignatureExpired:
            return self.build_response(
                'This link has expired',
                redirect(url_for('nereid.checkout.sign_in')), 400
            )
        except BadSignature:
            return self.build_response(
                'Invalid login link',
                redirect(url_for('nereid.checkout.sign_in')), 400
            )
        else:
            if not self.id == unsigned:
                current_app.logger.debug('Invalid link')
                abort(403)

            login_user(self.load_user(self.id))
            # TODO: Set this used token as expired to prevent using
            # it more than once
            return self.build_response(
                'You have been successfully logged in',
                redirect(url_for('nereid.website.home')), 200
            )

    @classmethod
    @route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password(cls):
        """
        Changes the password

        .. tip::
            On changing the password, the user is logged out and the login page
            is thrown at the user
        """
        form = ChangePasswordForm()

        if request.method == 'POST' and form.validate():
            if current_user.match_password(form.old_password.data):
                # Catch exceptions raised by password validation
                try:
                    cls.write([current_user], {'password': form.password.data})
                except PasswordError as e:
                    return cls.build_response(e,
                        render_template('change-password.jinja',
                            change_password_form=form), 400)
                logout_user()
                return cls.build_response(
                    _('Your password has been successfully changed! '
                        'Please login again'),
                    redirect(url_for('nereid.website.login')), 200
                )
            else:
                return cls.build_response(
                    _('The current password you entered is invalid'),
                    render_template(
                        'change-password.jinja', change_password_form=form
                    ), 400
                )

        if form.errors and (request.is_xhr or request.is_json):
            return jsonify(errors=form.errors), 400

        return render_template(
            'change-password.jinja', change_password_form=form
        )

    @route("/new-password/<int:active_id>/<sign>", methods=["GET", "POST"])
    def new_password(self, sign, max_age=24 * 60 * 60):
        """Create a new password

        This is intended to be used when a user requests for a password reset.
        The link sent out to reset the password will be a timestamped sign
        which is validated for max_age before allowing the user to set the
        new password.
        """
        form = NewPasswordForm()
        if form.validate_on_submit():
            try:
                unsigned = self._serializer.loads(
                    self._signer.unsign(sign, max_age=max_age),
                    salt='reset-password')
            except SignatureExpired:
                return self.build_response(
                    _('The password reset link has expired'),
                    redirect(url_for('nereid.website.login')), 400)
            except BadSignature:
                return self.build_response(
                    _('Invalid reset password code'),
                    redirect(url_for('nereid.website.login')), 400)
            else:
                if not self.id == unsigned:
                    current_app.logger.debug('Invalid reset password code')
                    abort(403)

            # Catch exceptions raised by password validation
            try:
                self.write([self], {'password': form.password.data})
            except PasswordError as e:
                return self.build_response(e,
                    render_template('new-password.jinja', password_form=form,
                        sign=sign, user=self), 400)
            return self.build_response(
                _('Your password has been successfully changed! '
                'Please login again'),
                redirect(url_for('nereid.website.login')), 200)

        elif form.errors:
            if request.is_xhr or request.is_json:
                return jsonify(error=form.errors), 400
            flash(_('Passwords must match'))

        return render_template(
            'new-password.jinja', password_form=form, sign=sign, user=self
        )

    @route("/activate-account/<int:active_id>/<sign>", methods=["GET"],
        readonly=False)
    def activate(self, sign, max_age=24 * 60 * 60):
        """A web request handler for activation of the user account. This
        method verifies the email and if it succeeds, activates the account.

        If your workflow requires a manual approval of every account, override
        this to not activate an account, or make a no op out of this method.

        If all what you require is verification of email, `verify_email` method
        could be used.
        """
        try:
            unsigned = self._serializer.loads(
                self._signer.unsign(sign, max_age=max_age),
                salt='activation'
            )
        except SignatureExpired:
            flash(_("The activation link has expired"))
        except BadSignature:
            flash(_("The activation token is invalid!"))
        else:
            if self.id == unsigned:
                self.active = True
                self.email_verified = True
                self.save()
                flash(_('Your account has been activated. Please login now.'))
            else:
                flash(_('Invalid Activation Code'))

        return redirect(url_for('nereid.website.login'))

    @classmethod
    @route("/reset-account", methods=["GET", "POST"])
    def reset_account(cls):
        """
        Reset the password for the user.

        .. tip::
            This does NOT reset the password, but just creates an activation
            code and sends the link to the email of the user. If the user uses
            the link, he can change his password.
        """
        form = ResetAccountForm()
        if form.validate_on_submit():
            try:
                nereid_user, = cls.search([
                    ('email', '=', form.email.data.lower()),
                    ('company', '=', current_website.company.id),
                ])
            except ValueError:
                return cls.build_response(
                    _('Invalid email address'),
                    render_template('reset-password.jinja'),
                    400
                )
            nereid_user.send_reset_email()
            return cls.build_response(
                _('An email has been sent to your account for resetting'
                ' your credentials'),
                redirect(url_for('nereid.website.login')), 200
            )
        elif form.errors:
            if request.is_xhr or request.is_json:
                return jsonify(error=form.errors), 400
            flash(_('Invalid email address.'))

        return render_template('reset-password.jinja')

    def send_reset_email(self):
        """
        Send an account reset email to the user

        :param nereid_user: The browse record of the user
        """
        email_message = render_email(
            _from,
            self.email, _('Account Password Reset'),
            text_template='emails/reset-text.jinja',
            html_template='emails/reset-html.jinja',
            nereid_user=self
        )
        self.send_email(email_message)

    @classmethod
    def authenticate(cls, email, password):
        """Assert credentials and if correct return the
        browse record of the user.

        .. versionchanged:: 3.0.4.0

            Does not check if the user account is active or not as that
            is not in the scope of 'authentication'.

        .. versionchanged:: 5.2.27

            Only search in active accounts. A user could have made several
            attempts to get a login and just confirmed (activated) one of them.
            Instead of silently aborting it must be possible to use this valid
            account.

        :param email: email of the user
        :param password: password of the user
        :return:
            Browse Record: Successful Login
            None: User cannot be found or wrong password
        """
        if not (email and password):
            return None
        users = cls.search([
                ('email', '=', email.lower()),
                ('company', '=', current_website.company.id),
                ])
        if not users:
            current_app.logger.debug("No user with email %s" % email)
            return None
        if len(users) > 1:
            current_app.logger.debug('%s has too many accounts' % email)
            return None
        user, = users
        if user.match_password(password):
            return user

    @classmethod
    def load_user(cls, user_id):
        """
        Implements the load_user method for Flask-Login

        :param user_id: Unicode ID of the user
        """
        try:
            with Transaction().set_context(active_test=False):
                user, = cls.search([('id', '=', int(user_id))])
        except ValueError:
            return None

        # Instead of returning the active record returned in the above search
        # we are creating a new record here. This is because the returned
        # active record seems to carry around the context setting of
        # active_test and any nested lookup from the record will result in
        # records being fetched which are inactive.
        return cls(int(user_id))

    @classmethod
    def load_user_from_request(cls, request):
        """
        Implements the request_loader method for Flask-Login

        :param request: the request
        """
        # First, try to login using the api_key url arg
        # TODO: Implement evtl. the former token loader removed in
        # cecdd2e5bbf80f0b7b391b551f36a1413673dd3c
        # (Migration of the module)

        # api_key = request.args.get('api_key')
        # if api_key:
        #     user = load_user_from_api_key
        #     if user:
        #         return user

        # Basic authentication
        api_key = request.headers.get('Authorization')
        if api_key:
            api_key = api_key.replace('Basic ', '', 1)
            try:
                api_key = base64.b64decode(api_key).decode('utf-8')
            except TypeError:
                pass
            user = cls.authenticate(*api_key.split(':', 1))
            if user and user.is_active:
                return user

    @classmethod
    def unauthorized_handler(cls):
        """
        This is called when the user is required to log in.

        If the request is XHR, then a JSON message with the status code 401
        is sent as response, else a redirect to the login page is returned.
        """
        if request.is_xhr:
            rv = jsonify(message=str(_('Bad credentials')))
            rv.status_code = 401
            return rv
        return redirect(
            login_url(current_app.login_manager.login_view, request.url)
        )

    @property
    def is_authenticated(self):
        """
        Returns True if the user is authenticated, i.e. they have provided
        valid credentials. (Only authenticated users will fulfill the criteria
        of login_required.)
        """
        return bool(self.id)

    @property
    def is_active(self):
        return bool(self.active)

    @property
    def is_anonymous(self):
        return not self.id

    def get_id(self):
        return str(self.id)

    @staticmethod
    def get_gravatar_url(email, **kwargs):
        """
        Return a gravatar url for the given email

        :param email: e-mail of the user
        :param https: To get a secure URL
        :param default: The default image to return if there is no profile pic
                        For example a unisex avatar
        :param size: The size for the image
        """
        if kwargs.get('https', request.scheme == 'https'):
            url = 'https://secure.gravatar.com/avatar/%s?'
        else:
            url = 'http://www.gravatar.com/avatar/%s?'
        url = url % hashlib.md5(email.lower().encode('utf-8')).hexdigest()

        params = []
        default = kwargs.get('default', None)
        if default:
            params.append(('d', default))

        size = kwargs.get('size', None)
        if size:
            params.append(('s', str(size)))

        return url + urllib.parse.urlencode(params)

    def get_profile_picture(self, **kwargs):
        """
        Return the url to the profile picture of the user.

        The default implementation fetches the profile image of the user from
        gravatar using :meth:`get_gravatar_url`
        """
        return self.get_gravatar_url(self.email, **kwargs)

    @staticmethod
    def aslocaltime(naive_date, local_tz_name=None):
        """
        Returns a localized time using `pytz.astimezone` method.

        :param naive_date: a naive datetime (datetime with no timezone
                           information), which is assumed to be the UTC time.
        :param local_tz_name: The timezone in which the date has to be returned
        :type local_tz_name: string

        :return: A datetime object with local time
        """

        utc_date = pytz.utc.localize(naive_date)

        if not local_tz_name:
            return utc_date

        local_tz = pytz.timezone(local_tz_name)
        if local_tz == pytz.utc:
            return utc_date

        return utc_date.astimezone(local_tz)

    def as_user_local_time(self, naive_date):
        """
        Returns a date localized in the user's timezone.

        :param naive_date: a naive datetime (datetime with no timezone
                           information), which is assumed to be the UTC time.
        """
        return self.aslocaltime(naive_date, self.timezone)

    @classmethod
    @route("/me", methods=["GET", "POST"])
    @login_required
    def profile(cls):
        """
        User profile
        """
        user_form = ProfileForm(obj=current_user)
        if user_form.validate_on_submit():
            cls.write(
                [current_user], {
                    'name': user_form.name.data,
                    'timezone': user_form.timezone.data,
                }
            )
            flash('Your profile has been updated.')

        if request.is_xhr or request.is_json:
            return jsonify(current_user.serialize())

        return render_template(
            'profile.jinja', user_form=user_form, active_type_name="general"
        )


class NereidAnonymousUser(AnonymousUserMixin, ModelView):
    """
    Nereid Anonymous User Object
    """
    __name__ = "nereid.user.anonymous"

    def get_profile_picture(self, **kwargs):
        """
        Returns the default gravatar mystery man silouette
        """
        User = Pool().get('nereid.user')
        kwargs['default'] = 'mm'
        return User.get_gravatar_url("does not matter", **kwargs)
