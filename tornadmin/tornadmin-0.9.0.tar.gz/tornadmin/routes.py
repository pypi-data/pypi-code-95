import re
from tornado.routing import Rule, PathMatches
from tornadmin import handlers


class StartMatches(PathMatches):
    """Matches the start of a path with the given pattern.
    """
    def __init__(self, path_pattern):
        super().__init__(path_pattern)
        # PathMatches appends a '$' symbol to the pattern
        # so we recompile the pattern without the symbol
        self.regex = re.compile(path_pattern)


class EndMatchesFactory:
    """It returns a callable instance.

    The purpose of this class is to avoid having to pass
    the base admin url to every route.
    """
    def __init__(self, base_url):
        if (base_url.endswith('/')):
            base_url = base_url[:-1]

        self.base_url = base_url

    def __call__(self, path_pattern):
        if not path_pattern.startswith('/'):
            path_pattern = '/' + path_pattern

        path = r'%s%s' % (self.base_url, path_pattern)

        if path.endswith('/'):
            path += '?'

        return PathMatches(path)


def AdminRouter(base_url):
    handlers.BaseHandler.base_url = base_url

    EndMatches = EndMatchesFactory(base_url)

    routes = [
        (r'login/?', handlers.LoginHandler, 'login'),
        (r'logout/?', handlers.LogoutHandler, 'logout'),
        (r'', handlers.IndexHandler, 'index'),
        (r'(?P<app_slug>[\w-]+)/(?P<model_slug>[\w-]+)/?', handlers.ListHandler, 'list'),
        (r'(?P<app_slug>[\w-]+)/(?P<model_slug>[\w-]+)/add/?', handlers.CreateHandler, 'create'),
        (r'(?P<app_slug>[\w-]+)/(?P<model_slug>[\w-]+)/(?P<id>[\w-]+)/?', handlers.DetailHandler, 'detail'),
        (r'static/(.*)', handlers.StaticFileHandler, 'static'),
    ]

    return (
        StartMatches(r'%s' % base_url),
        [
            Rule(EndMatches(route[0]),
            route[1],
            None,
            'admin:%s' % route[2]) for route in routes
        ]
    )
