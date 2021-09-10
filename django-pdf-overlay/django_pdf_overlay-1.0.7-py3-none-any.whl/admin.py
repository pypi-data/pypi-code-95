from django.contrib import admin

from .models import Document


@admin.register(Document)
class GeneralAdmin(admin.ModelAdmin):
    pass
