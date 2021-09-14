import webtest

from pyramid.config import Configurator
from cubicweb.devtools.webtest import CubicWebTestTC


ACCEPTED_ORIGINS = ["example.com"]


class TestApp(webtest.TestApp):
    def __init__(self, *args, admin_login, admin_password, **kwargs):
        super().__init__(*args, **kwargs)
        self.admin_login = admin_login
        self.admin_password = admin_password
        self._ident_cookie = None

    def reset(self):
        super().reset()
        self._ident_cookie = None

    def post(
        self,
        route,
        params=None,
        do_not_grab_the_crsf_token=False,
        do_not_inject_origin=False,
        form_with_csrf_token_url="/login",
        form_number=0,
        **kwargs,
    ):
        if params is None:
            params = {}
        if self._ident_cookie:
            if "headers" in kwargs and "Cookie" not in kwargs["headers"]:
                kwargs["headers"]["Cookie"] = self._ident_cookie
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Cookie": self._ident_cookie}

        if (
            isinstance(params, dict)
            and not do_not_grab_the_crsf_token
            and "csrf_token" not in params
        ):
            if form_with_csrf_token_url is None:
                form_with_csrf_token_url = route

            csrf_token = self.get_csrf_token(
                form_with_csrf_token_url=form_with_csrf_token_url,
                form_number=form_number,
            )

            # "application/json" doesn't submit token in form params but as header value
            if kwargs.get("headers", {}).get("Content-Type") != "application/json":
                if "csrf_token" not in params:
                    params["csrf_token"] = csrf_token
            else:
                if "headers" in kwargs:
                    kwargs["headers"]["X-CSRF-Token"] = csrf_token
                else:
                    kwargs["headers"] = {"X-CSRF-Token": csrf_token}

        if not do_not_inject_origin:
            if "headers" in kwargs and "Origin" not in kwargs["headers"]:
                kwargs["headers"]["Origin"] = "https://" + ACCEPTED_ORIGINS[0]
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Origin": "https://" + ACCEPTED_ORIGINS[0]}

        return super().post(route, params, **kwargs)

    def get_csrf_token(self, form_with_csrf_token_url="/login", form_number=0):
        get_form = self.get(form_with_csrf_token_url)

        if "html" not in get_form.content_type:
            raise Exception(
                f"Error while trying to get the form at url {form_with_csrf_token_url}, it "
                f"returns a response with a content type of {get_form.content_type} while a "
                "content type with 'html' in it is expected.\n\n"
                "Maybe you need to use this function parameters 'form_with_csrf_token_url' or "
                "'do_not_grab_the_crsf_token'?"
            )

        form = get_form.forms[form_number]
        return form.fields["csrf_token"][0].value

    def get(self, route, *args, **kwargs):
        if self._ident_cookie:
            if "headers" in kwargs and "Cookie" not in kwargs["headers"]:
                kwargs["headers"]["Cookie"] = self._ident_cookie
            elif "headers" not in kwargs:
                kwargs["headers"] = {"Cookie": self._ident_cookie}

        return super().get(route, *args, **kwargs)

    def login(self, user=None, password=None):
        """Log the current http session for the provided credential

        If no user is provided, admin connection are used.
        """
        if user is None:
            user = self.admin_login
            password = self.admin_password
        if password is None:
            password = user

        response = self.post("/login", {"__login": user, "__password": password})

        assert response.status_int == 303

        self._ident_cookie = response.headers["Set-Cookie"]
        assert self._ident_cookie

        return response


class _BasePyramidCWTest(CubicWebTestTC):
    settings = {}

    @classmethod
    def init_config(cls, config):
        super().init_config(config)
        config.global_set_option("anonymous-user", "anon")
        config.in_debug_mode = True

    def _generate_pyramid_config(self):
        settings = {
            "cubicweb.bwcompat": False,
            "cubicweb.session.secret": "test",
        }
        settings.update(self.settings)
        pyramid_config = Configurator(settings=settings)

        pyramid_config.registry["cubicweb.repository"] = self.repo
        pyramid_config.include("cubicweb.pyramid")

        self.includeme(pyramid_config)
        self.pyr_registry = pyramid_config.registry

        return pyramid_config

    def includeme(self, config):
        config.registry.settings["pyramid.csrf_trusted_origins"] = ACCEPTED_ORIGINS


class PyramidCWTest(_BasePyramidCWTest):
    def setUp(self):
        # Skip CubicWebTestTC setUp
        super().setUp()
        settings = {
            "cubicweb.bwcompat": False,
            "cubicweb.session.secret": "test",
        }
        settings.update(self.settings)
        pyramid_config = Configurator(settings=settings)

        pyramid_config.registry["cubicweb.repository"] = self.repo
        pyramid_config.include("cubicweb.pyramid")

        self.includeme(pyramid_config)
        self.pyr_registry = pyramid_config.registry
        self.webapp = TestApp(
            pyramid_config.make_wsgi_app(),
            extra_environ={"wsgi.url_scheme": "https"},
            admin_login=self.admlogin,
            admin_password=self.admpassword,
        )
