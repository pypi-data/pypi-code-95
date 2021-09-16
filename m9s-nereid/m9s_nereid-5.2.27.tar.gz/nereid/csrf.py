# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from flask import request
from flask_wtf.csrf import CSRFProtect, generate_csrf


__all__ = ['NereidCsrfProtect']


class NereidCsrfProtect(CSRFProtect):

    def init_app(self, app):
        """
        Reimplementation of CsrfProtect.init_app

        By default `init_app` is strictly for Flask and depend on
        `app.view_functions` to `exempt csrf`. But nereid works on
        `request.endpoint`, hence changed the method just to respect
        `request.endpoint` not `app.view_functions`
        """
        app.extensions['csrf'] = self
        app.jinja_env.globals['csrf_token'] = generate_csrf
        app.config.setdefault(
            'WTF_CSRF_HEADERS', ['X-CSRFToken', 'X-CSRF-Token']
        )
        app.config.setdefault('WTF_CSRF_SSL_STRICT', True)
        app.config.setdefault('WTF_CSRF_ENABLED', True)
        app.config.setdefault('WTF_CSRF_CHECK_DEFAULT', True)
        app.config['WTF_CSRF_METHODS'] = set(app.config.get(
            'WTF_CSRF_METHODS', ['POST', 'PUT', 'PATCH', 'DELETE']
        ))
        app.config.setdefault('WTF_CSRF_FIELD_NAME', 'csrf_token')
        app.config.setdefault(
            'WTF_CSRF_HEADERS', ['X-CSRFToken', 'X-CSRF-Token']
        )
        app.config.setdefault('WTF_CSRF_TIME_LIMIT', 3600)
        app.config.setdefault('WTF_CSRF_SSL_STRICT', True)

        # expose csrf_token as a helper in all templates
        @app.context_processor
        def csrf_token():
            return dict(csrf_token=generate_csrf)

        @app.before_request
        def csrf_protect():
            if not app.config['WTF_CSRF_ENABLED']:
                return

            if not app.config['WTF_CSRF_CHECK_DEFAULT']:
                return

            if request.method not in app.config['WTF_CSRF_METHODS']:
                return

            if not request.endpoint:
                return

            if request.blueprint in self._exempt_blueprints:
                return

            if request.endpoint in self._exempt_views:
                return

            self.protect()
