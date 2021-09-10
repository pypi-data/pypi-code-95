from django.contrib import admin
from . import models


@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "enabled",
        "order",
    )

    list_filter = ("enabled",)
