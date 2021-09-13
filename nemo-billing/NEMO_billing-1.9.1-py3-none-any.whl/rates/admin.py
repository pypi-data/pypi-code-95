from django import forms
from django.contrib import admin
from django.contrib.admin import register

from NEMO_billing.rates.models import RateType, Rate, RateLog, RateCategory


@register(RateType)
class RateTypeAdmin(admin.ModelAdmin):
    list_display = ("type", "category_specific", "item_specific")
    readonly_fields = ("type",)


class RateAdminForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = "__all__"


@register(Rate)
class RateAdmin(admin.ModelAdmin):
    form = RateAdminForm
    list_display = ("get_item", "type", "category", "amount", "flat", "minimum_charge")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "type":
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj: Rate, form, change):
        obj.save_with_user(request.user)

    def delete_model(self, request, obj: Rate):
        obj.delete_with_user(request.user)

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)


@register(RateLog)
class RateLogAdmin(admin.ModelAdmin):
    list_display = ("id", "action", "user", "date", "get_content_object_display")
    list_filter = ["action"]
    date_hierarchy = "date"

    def get_content_object_display(self, rate_log: RateLog):
        content_object = rate_log.content_object
        if not content_object:
            content_object = "Staff Charge"
        return content_object

    get_content_object_display.admin_order_field = "content_type"  # Allows column order sorting
    get_content_object_display.short_description = "Item"  # Renames column head

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(RateCategory)
