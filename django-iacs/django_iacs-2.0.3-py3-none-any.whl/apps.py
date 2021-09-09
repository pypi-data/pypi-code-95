from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class CommonAppConfig(AppConfig):
    name = None
    app_url_conf = None
    websocket_message_router = None
    dependencies = None
    grpc_services = None
    workers = None
    menus = None

    def check_deps(self):
        if self.dependencies is not None:
            for d in self.dependencies:
                if d not in settings.INSTALLED_APPS:
                    pass

    def load_url_config(self):
        root_urlconf = getattr(settings, 'ROOT_URLCONF', None)
        if root_urlconf:
            # if self.name in settings.INSTALLED_APPS:
            # 加入应用自带的url配置
            if self.app_url_conf is None:
                print(f'{self.name} url config is None, skipped')
            else:
                app_url_conf = import_module(self.app_url_conf)
                django_url_conf = import_module(root_urlconf)
                urlpatterns = getattr(django_url_conf, 'urlpatterns', [])
                urlpatterns += getattr(app_url_conf, 'urlpatterns', None)
                setattr(django_url_conf, 'urlpatterns', urlpatterns)
                #
                # route_groups = getattr(django_url_conf, 'route_groups')
                # route_groups += getattr(app_url_conf, 'route_groups', None)
                # setattr(django_url_conf, 'router_groups', route_groups)
                print(f'{self.name} url config added')
        else:
            print('settings.ROOT_URLCONF is None')

    def load_websocket_message(self):
        """
        加载应用的websocket消息路由
        """
        if self.name in settings.INSTALLED_APPS and self.websocket_message_router:
            ws_router = import_module(self.websocket_message_router)
            root_ws_router = import_module(settings.IACS_SETTINGS["ROOT_WEBSOCKET_MESSAGE_ROUTE"])
            routes = getattr(root_ws_router, 'routes', {})
            routes.update(getattr(ws_router, 'routes', {}))
            setattr(root_ws_router, 'routes', routes)

            print(f'{self.name} websocket routes added')

    def ready(self):
        self.load_url_config()
        self.load_websocket_message()


class IacsConfig(CommonAppConfig):
    default = True
    name = 'iacs'
    app_url_conf = "iacs.urls"
    websocket_message_router = "iacs.websocket_messages"
    menus = settings.IACS_SETTINGS["MENUS"]
