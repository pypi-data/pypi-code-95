import copy
import json
import os
from argparse import ArgumentParser
from importlib import import_module

from channels.management.commands.runserver import Command as ChannelRunserver
from django.apps import apps
from django.conf import settings

from ...models import Api


class Command(ChannelRunserver):
    method_map = {
        'get': 0,
        'post': 1,
        'delete': 2,
        'put': 3,
        'patch': 4
    }

    def add_arguments(self, parser: ArgumentParser):
        parser.add_argument('-o', '--output',
                            help='collect api info to json file, '
                                 'relative path to BASE_DIR, default: BASE_DIR',
                            type=str,
                            required=False)
        parser.add_argument('--todb', help='collect api info to database', action="store_true")
        parser.add_argument('--clear', help='clear api info in database', action="store_true")

    def handle(self, *args, **options):
        output = options.get('output')
        todb = options.get('todb')
        clear = options.get('clear')

        if clear:
            Api.objects.all().delete()

        apis = self.collect_apis(self.get_route_groups())
        if todb:
            objs = []
            for api in apis:
                objs.append(Api(**api))
            Api.objects.bulk_create(objs)

        if output:
            output = os.path.join(settings.BASE_DIR, output, 'api.json')
            with open(output, 'wb') as f:
                f.write(json.dumps(apis, indent=2, ensure_ascii=False).encode())

    def get_route_groups(self):

        route_groups = []
        # 从app config中自动获取url配置
        for app_config in apps.get_app_configs():
            app_url_conf_path = getattr(app_config, "app_url_conf", None)
            if app_url_conf_path is not None:
                app_url_conf = import_module(app_url_conf_path)
                route_group = getattr(app_url_conf, "route_groups", [])
                for item in route_group:
                    item["app_name"] = app_config.name
                route_groups += route_group
                print(f"get from api {app_url_conf_path}")
        return route_groups

    def collect_apis(self, route_groups):
        base_names = []
        apis = []
        for group in route_groups:
            routers = group["routers"]
            assert isinstance(routers, list), f'{group}-{routers} is not list'
            if isinstance(routers, list) and len(routers) > 0:
                for router in routers:
                    registry = router.registry
                    for prefix, viewset, basename in registry:

                        if basename in base_names:
                            raise Exception(f'basename of {viewset.__name__}: "{basename}" is duplicated')

                        base_names.append(basename)

                        lookup = router.get_lookup_regex(viewset)
                        routes = router.get_routes(viewset)

                        for route in routes:
                            mapping = router.get_method_map(viewset, route.mapping)
                            if not mapping:
                                continue
                            # Build the url pattern
                            regex = route.url.format(
                                prefix=prefix,
                                lookup=lookup,
                                trailing_slash=router.trailing_slash
                            )
                            if not prefix and regex[:2] == '^/':
                                regex = '^' + regex[2:]
                            initkwargs = route.initkwargs.copy()
                            initkwargs.update({
                                'basename': basename,
                                'detail': route.detail,
                            })

                            view = viewset.as_view(mapping, **initkwargs)

                            for key, value in view.actions.items():
                                func = getattr(viewset, value)
                                url_name = getattr(func, 'url_name', None)
                                action_name = getattr(func, 'action_name', None)
                                user_default = getattr(func, 'user_default', False)
                                rest_method = getattr(func, 'rest_method', None)
                                if not action_name:
                                    known_actions_name = getattr(viewset, 'known_actions_name', None)
                                    if not known_actions_name:
                                        raise Exception('{} has not attr "known_actions_name"'.format(viewset))

                                    assert isinstance(known_actions_name, dict), '"known_actions_name" is not a dict'

                                    if value != 'partial_update':
                                        action_name = known_actions_name.get(value)
                                        if type(action_name) not in [str, dict]:
                                            raise TypeError('{0} action_name'.format(view.__name__))

                                        if isinstance(action_name, dict):
                                            cp_action_name = copy.deepcopy(action_name)
                                            action_name = cp_action_name.get('name', None)
                                            user_default = cp_action_name.get('user_default', False)
                                            rest_method = cp_action_name.get('rest_method', None)
                                    else:
                                        continue

                                    if not action_name:
                                        raise Exception('"action_name" expect not None, {}'.format(viewset))

                                position = '{}.{}'.format(viewset.__name__, value)
                                method_code = self.method_map.get(str(key).lower())
                                if rest_method is None:
                                    rest_method_code = method_code
                                else:
                                    rest_method_code = self.method_map.get(str(rest_method).lower())

                                if url_name is not None:
                                    base_name = f'{basename}-{url_name}'
                                else:
                                    base_name = f'{basename}-{value}'

                                apis.append({
                                    'regex': regex,
                                    'method': method_code,
                                    'rest_method': rest_method_code,
                                    'name': action_name,
                                    'base_name': base_name,
                                    'position': position,
                                    'group': group.get('name', None),
                                    'user_default': user_default,
                                    'app_name': group.get('app_name', '')
                                })

            # channels = group.get('channels', None)
            # if isinstance(channels, list) and len(channels) > 0:
            #     for channel in channels:
            #         for route in channel:
            #             position = route.callback.__name__
            #             data = {
            #                 'regex': str(route.pattern),
            #                 'protocol': 1,
            #                 'name': route.callback.action_name,
            #                 'method': None,
            #                 'position': position,
            #                 'group': group.get('name', None),
            #                 'user_default': route.callback.user_default,
            #                 'app_name': group.get('app_name', '')
            #             }
            #             apis.append(data)
        return apis
