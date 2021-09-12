from tornado import web


class SideNav(web.UIModule):
    def render(self, admin_site):
        """menu structure:

            {
                app_name: [ModelAdmin1, ModelAdmin2, ...],
                ...
            }
        """
        menu = {}

        _registry = admin_site.get_registry()

        for key, admin in _registry.items():
            if admin.app not in menu:
                menu[admin.app] = []

            menu[admin.app].append(admin)

        return self.render_string('modules/side-nav.html', menu=menu)
