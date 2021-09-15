from django.contrib import admin

from appchance_sections.forms import SectionAdminForm


class SectionAdminMixin(admin.ModelAdmin):
    list_display = ("name", "content_name", "widget", "placement", "order", "content_url")
    form = SectionAdminForm
