from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as UpstreamUserAdmin
from django.utils.translation import ugettext_lazy as _
from . import models


@admin.register(models.User)
class UserAdmin(UpstreamUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Informations personnelles"),
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            _("Adresse postale"),
            {"fields": ("address", "city", "zip_code", "country")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
