from flask import Flask, Request, Response

from regia.utils import SingleTon
from regia.container import Mapping


class Application(SingleTon, Flask):

    def __init__(self, *args, **kwargs):
        self.app_path: set = kwargs.pop('app_path', set())
        super(Application, self).__init__(*args, **kwargs)

    def setup(self, config):
        config.render(**self.default_config)
        from django.conf import settings
        settings.configure(config)
        self.config = config
        self._register_mapping()
        self.patch_json()
        self.auto_find_app_path()

    def _register_mapping(self):
        """注册路由模块"""
        mapping = Mapping()
        for item in mapping:
            options = item.pop('options', {})
            self.add_url_rule(**item, **options)

    @staticmethod
    def patch_json():
        try:
            import simplejson as json
        except ImportError:
            import json
        Request.json_module = json
        Response.json_module = json

    def auto_find_app_path(self):
        from regia.utils import import_string
        for path in self.app_path:
            import_string(path)


# 单例全局的application
def get_wsgi_application():
    app = Application(__name__)
    return app
