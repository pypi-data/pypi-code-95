from copy import copy

from channels.management.commands.runserver import Command as ChannelRunserver
from django.apps import apps

from ...models import Menu, Api


class Command(ChannelRunserver):
    method_map = {
        'get': 0,
        'post': 1,
        'delete': 2,
        'put': 3,
        'patch': 4
    }

    def add_arguments(self, parser):
        parser.add_argument('--todb', help='collect menu info to database', action="store_true")
        parser.add_argument('--clear', help='clear menu info in database', action="store_true")

    def handle(self, *args, **options):

        todb = options.get('todb')
        clear = options.get('clear')

        if clear:
            Menu.objects.all().delete()

        if todb:
            self.collect_menus()
            self.create_relations()

    def menu_flat(self, nested_menus, father=None):
        flat_menus = {}

        for m in nested_menus:
            sub_menus = m.pop("sub_menu", [])
            if father:
                m["father_id"] = father["id"]
                father_activate = father.get("activate", True)
                if not father_activate:
                    m["activate"] = father_activate
            else:
                m["father_id"] = None
            flat_menus[m["id"]] = m

            if len(sub_menus) > 0:
                flat_menus.update(self.menu_flat(sub_menus, m))
        print(flat_menus)
        return flat_menus

    def collect_menus(self):

        for app_config in apps.get_app_configs():
            app_menus = getattr(app_config, 'menus', [])
            if app_menus is None:
                continue
            leaf_menu = []
            for menu_id, menu in self.menu_flat(app_menus).items():
                copy_menu = copy(menu)
                if menu.get("link", "") == "":
                    try:
                        Menu.objects.update_or_create(id=copy_menu.pop("id", None), **copy_menu)
                    except Exception as e:
                        print(e, copy_menu)
                else:
                    leaf_menu.append(menu)

            # old_menu_to_delete = [m["father_id"] for m in leaf_menu]

            # Menu.objects.filter(father_id__in=old_menu_to_delete).delete()
            # 创建应用的新菜单

            for m in leaf_menu:
                apis = m.pop("apis", [])
                try:
                    instance = Menu.objects.create(**m)
                    api_queryset = Api.objects.filter(base_name__in=apis)
                    if api_queryset.exists():
                        instance.apis.set(api_queryset)
                    else:
                        # 暂时兼容position方式，以后要废弃掉
                        api_queryset = Api.objects.filter(position__in=apis)
                        if api_queryset.exists():
                            instance.apis.set(api_queryset)
                except Exception as e:
                    print(e, m)

    def create_relations(self):
        """
        为了方便使用，将菜单树中每一个节点与所有父节点建立关系。
        :return:
        """
        queryset = Menu.objects.all()

        for q in queryset:
            q.supers.clear()
            supers = []

            def find(_menu):
                if _menu and _menu.father_id:
                    if _menu.father not in supers:
                        supers.append(_menu.father)
                    find(_menu.father)

            find(q)
            if supers:
                q.supers.add(*supers)
