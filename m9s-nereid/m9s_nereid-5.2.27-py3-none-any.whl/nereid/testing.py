# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import inspect
import os
import jinja2
import unittest

from contextlib import contextmanager

from werkzeug.exceptions import abort
from secure_cookie.session import FilesystemSessionStore
from flask.globals import _request_ctx_stack

from nereid import Nereid, current_app
from nereid.sessions import Session
from nereid.contrib.locale import Babel

from trytond import backend
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.tests.test_tryton import ModuleTestCase

from .templating import LazyRenderer

Pool.start()
DB_NAME = os.environ['DB_NAME']
DB = backend.get('Database')(DB_NAME)
Pool.test = True
POOL = Pool(DB_NAME)


class NereidTestApp(Nereid):
    """
    A Nereid app which works by removing transaction handling around the wsgi
    app
    """

    # Setting to run specific functions defined in test cases as methods
    dispatch_function_as_method = False

    def __init__(self, **config):
        super(NereidTestApp, self).__init__(**config)
        self.config['WTF_CSRF_ENABLED'] = False

    @property
    def root_transaction(self):
        """
        There is no need of a separate root transaction as everything could
        be loaded in the transaction context provided in the test case
        """
        @contextmanager
        def do_nothing():
            yield
        return do_nothing()

    def load_backend(self):
        """
        Use the global pool
        """
        global DB, POOL
        self._database = DB.connect()
        self._pool = POOL

    def dispatch_request(self):
        """
        Skip the transaction handling and call the _dispatch_request
        """

        req = _request_ctx_stack.top.request
        if req.routing_exception is not None:
            self.raise_routing_exception(req)

        rule = req.url_rule
        # if we provide automatic options for this URL and the
        # request came with the OPTIONS method, reply automatically
        if getattr(rule, 'provide_automatic_options', False) \
           and req.method == 'OPTIONS':
            return self.make_default_options_response()

        Website = current_app.pool.get('nereid.website')
        website = Website.get_from_host(req.host)
        locale = website.get_current_locale(req)

        _request_ctx_stack.top.website = website.id
        _request_ctx_stack.top.locale = locale.id

        # pop locale if specified in the view_args
        req.view_args.pop('locale', None)
        active_id = req.view_args.pop('active_id', None)

        return self._dispatch_request(req, locale.language.code, active_id)

    def _dispatch_request(self, req, language, active_id):
        """
        Implement the nereid specific testing _dispatch
        """
        with Transaction().set_context(language=language):

            # otherwise dispatch to the handler for that endpoint
            if req.url_rule.endpoint in self.view_functions:
                meth = self.view_functions[req.url_rule.endpoint]
            else:
                model, method = req.url_rule.endpoint.rsplit('.', 1)
                meth = getattr(Pool().get(model), method)

            # Provide the ability to run specific functions
            # in test cases as methods
            if not inspect.isfunction(meth) or self.dispatch_function_as_method:
                # static or class method
                result = meth(**req.view_args)
            else:
                # instance method, extract active_id from the url
                # arguments and pass the model instance as first argument
                model = Pool().get(req.url_rule.endpoint.rsplit('.', 1)[0])
                i = model(active_id)
                try:
                    i.rec_name
                except UserError:
                    # The record may not exist anymore which results in
                    # a read error
                    current_app.logger.debug(
                        "Record %s doesn't exist anymore." % i)
                    abort(404)
                result = meth(i, **req.view_args)

            if isinstance(result, LazyRenderer):
                result = (str(result), result.status, result.headers)

            return result

def get_app(**options):
    app = NereidTestApp()
    if 'SECRET_KEY' not in options:
        options['SECRET_KEY'] = 'secret-key'
    app.config.update(options)
    app.config['DATABASE_NAME'] = DB_NAME
    app.config['DEBUG'] = True
    app.session_interface.session_store = \
        FilesystemSessionStore('/tmp', session_class=Session)

    # loaders is usually lazy loaded
    # Pre-fetch it so that the instance attribute _loaders will exist
    app.jinja_loader.loaders

    # Initialise the app now
    app.initialise()

    # Load babel as its a required extension anyway
    Babel(app)
    return app


class NereidTestCase(unittest.TestCase):

    @property
    def _templates(self):
        if hasattr(self, 'templates'):
            return self.templates
        return {}

    def get_app(self, **options):
        app = get_app(**options)
        app.jinja_loader._loaders.insert(0, jinja2.DictLoader(self._templates))
        return app


class NereidModuleTestCase(NereidTestCase, ModuleTestCase):
    '''
    Provide a simple Mixin for usage in module tests
    '''
    pass
