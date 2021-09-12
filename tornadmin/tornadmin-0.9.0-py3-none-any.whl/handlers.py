import os
from tornado import web
from tornadmin.sites import site
from tornadmin.utils import get_value


BASE_DIR = os.path.dirname(__file__)


class AdminUser:
    def __init__(self, username, **kwargs):
        self.username = username
        self.full_name = kwargs.get('full_name')
        self.short_name = kwargs.get('short_name')

    def __bool__(self):
        if self.username:
            return True
        return False


class BaseHandler(web.RequestHandler):
    async def prepare(self):
        self.current_user = AdminUser(**site.config['authenticate'](self.request))

        if not self.current_user and getattr(self, 'login_required', True):
            return self.redirect(self.reverse_url('admin:login'))

    def redirect(self, url, *args, **kwargs):
        """Override handler's redirect method to be able to 
        redirect using url names.

        args will be passed to reversing function.
        kwargs will be passed to redirect function.
        """
        if (':' in url):
            # url is a route name
            url = self.reverse_url(url, *args)

        return super().redirect(url, **kwargs)

    def reverse_url(self, name, *args):
        """Override handler's reverse_url to strip question mark
        from the reversed url.
        """

        reversed_url = self.application.reverse_url(name, *[arg for arg in args if arg])
        return reversed_url.strip('?')

    def get_template_path(self):
        return os.path.join(os.path.dirname(__file__), 'templates')

    def get_template_namespace(self):
        namespace = super().get_template_namespace()
        namespace.update({
            'get_value': get_value,
            'admin_site': site
        })
        return namespace

    def static_url(self, path, include_host=None, **kwargs):
        """We override RequestHandler's `static_url` to
        use our own static directory path instead of
        the value from `static_path` appication setting.

        :TODO: Provide a setting called `admin_static_path` so user can
        configure admin static files location.
        """
        if path.startswith('tornadmin'):

            get_url = self.settings.get(
                "static_handler_class", StaticFileHandler
            ).make_static_url

            if include_host is None:
                include_host = getattr(self, "include_host", False)

            if include_host:
                base = self.request.protocol + "://" + self.request.host + self.base_url
            else:
                base = self.base_url

            fake_settings = {
                'static_path': os.path.join(BASE_DIR, 'static'),
            }

            return base + get_url(fake_settings, path, **kwargs)

        else:
            return super().static_url(path, include_host, *args, **kwargs)

    def _static_url(self, path, *args, **kwargs):
        url = super().static_url(path, *args, **kwargs)
        if path.startswith('tornadmin'):
            url = self.base_url + url
        return url


class StaticFileHandler(web.StaticFileHandler):
    def initialize(self):
        super().initialize(path=os.path.join(BASE_DIR, 'static'))


class LoginHandler(BaseHandler):
    login_required = False

    def get(self):
        if self.current_user:
            return self.redirect('admin:index')
        self.write("Login here")


class LogoutHandler(BaseHandler):
    pass


class IndexHandler(BaseHandler):
    def get(self):
        registry = []

        _registry = site.get_registry()

        for key, admin in _registry.items():
            registry.append(admin)

        context = {
            'registry': registry,
        }
        self.render('index.html', **context)


class ListHandler(BaseHandler):
    async def get(self, app_slug, model_slug):
        admin = site.get_registered(app_slug, model_slug)

        context = {
            'admin': admin,
            'headers': admin.get_list_headers(),
            'list_items': await admin.get_list(self),
        }

        self.render('list.html', **context)


class CreateHandler(BaseHandler):
    def get(self, app_slug, model_slug):
        admin = site.get_registered(app_slug, model_slug)
        form_class = admin.get_form(self)
        context = {
            'obj': None,
            'admin': admin,
            'form': form_class(),
        }
        self.render('create.html', **context)

    async def post(self, app_slug, model_slug,):
        admin = site.get_registered(app_slug, model_slug)
        form_class = admin.get_form(self)
        
        data = {}

        for field_name in form_class._fields:
            # NOTE: Implement a multivaluedict to store values in a list
            # instead of using data dictionary
            # because the current way doesn't allow multiple values.
            data[field_name] = self.get_body_argument(field_name, None)

        form = form_class(data=data)

        if form.validate():
            obj = await admin.save_model(self, form)
            self.redirect('admin:detail', app_slug, model_slug, obj.id)
            return

        context = {
            'obj': None,
            'admin': admin,
            'form': form,
        }
        self.render('create.html', **context)



class DetailHandler(BaseHandler):
    async def get(self, app_slug, model_slug, id):
        admin = site.get_registered(app_slug, model_slug)
        form_class = admin.get_form(self)
        obj = await admin.get_object(self, id)
        data = await admin.get_form_data(obj)

        form = form_class(data=data)

        context = {
            'obj': obj,
            'admin': admin,
            'form': form,
        }

        self.render('create.html', **context)

    async def post(self, app_slug, model_slug, id):
        admin = site.get_registered(app_slug, model_slug)
        form_class = admin.get_form(self)
        obj = await admin.get_object(self, id)

        data = {}

        for field_name in form_class._fields:
            # :TODO: Implement a multivaluedict to store values in a list
            # instead of using data dictionary
            # because the current way doesn't allow multiple values.
            data[field_name] = self.get_body_argument(field_name, None)

        form = form_class(data=data)

        if form.validate():
            await admin.save_model(self, form, obj)
            self.redirect('admin:detail', app_slug, model_slug, obj.id)
            return

        context = {
            'obj': obj,
            'admin': admin,
            'form': form,
        }

        self.render('create.html', **context)
