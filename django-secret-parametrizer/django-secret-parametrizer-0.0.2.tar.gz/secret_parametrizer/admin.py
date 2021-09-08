from django.contrib import admin
from .models import SecretParametrizer
# Register your models here.
class SecretParametrizerAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "description",
        "url_to_call",        
    )
    list_filter = ("code","name")
    search_fields = ["name", "code"]

admin.site.register(SecretParametrizer, SecretParametrizerAdmin)