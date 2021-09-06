import abc

from django.contrib.auth.models import Group, Permission, _user_get_permissions, _user_has_perm, _user_has_module_perms
from django.db import models

from django.utils.translation import gettext_lazy as _


class PermissionWithoutPrimitivesMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    it is a copy of PermissionsMixin but with the difference that the mixin adds only the groups and permissions fields,
    while the "is_superuser" field is not added.

    In order to work, the merge of models needs to define "is_superuser" and "is_active" fields
    """

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_user_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has directly.
        Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'user')

    def get_group_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        groups. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, 'group')

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, 'all')

    def get_is_active_field_name(self) -> str:
        """
        boolean field of this model representing whether the user is active or not
        """
        return "active"

    def get_is_superuser_field_name(self) -> str:
        """
        boolean field of this model representing whether the user is a superuser
        """
        return "superuser"

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if getattr(self, self.get_is_active_field_name()) and getattr(self, self.get_is_superuser_field_name()):
            return True

        # Otherwise we need to check the backends.
        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if getattr(self, self.get_is_active_field_name()) and getattr(self, self.get_is_superuser_field_name()):
            return True

        return _user_has_module_perms(self, app_label)