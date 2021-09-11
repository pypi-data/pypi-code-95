from cliff.show import ShowOne

from django.conf import settings

from enough.common import openstack


class CreateTestSubdomain(ShowOne):
    "Create and delegate a test subdomain, if possible"

    def take_action(self, parsed_args):
        h = openstack.Heat(settings.CONFIG_DIR)
        r = h.create_test_subdomain(self.app.options.domain)
        columns = ('name',)
        data = (r,)
        return (columns, data)
