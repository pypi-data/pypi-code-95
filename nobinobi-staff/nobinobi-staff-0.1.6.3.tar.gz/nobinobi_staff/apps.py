#  Copyright (C) 2020 <Florian Alu - Prolibre - https://prolibre.com
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate, post_save
from django.utils.translation import gettext_lazy as _


def load_group_and_permissions(sender, **kwargs):
    """Load an initial group and its permissions"""
    from django.contrib.auth.models import Group, Permission
    groupe_personnel = Group.objects.get_or_create(
        name='Personnel'
    )[0]
    permissions_names = [
        'can_read_list',
    ]
    permissions = [
        Permission.objects.get(codename=permission_name)
        for permission_name
        in permissions_names
    ]
    for permission in permissions:
        groupe_personnel.permissions.add(permission)


class NobinobiStaffConfig(AppConfig, object):
    name = 'nobinobi_staff'
    verbose_name = _("Staff")
    verbose_name_plural = _("Staffes")

    def ready(self):
        import nobinobi_staff.signals
        # post_migrate.connect(load_fixtures_personal, sender=self)
        # post_migrate.connect(load_group_and_permissions, sender=self)
