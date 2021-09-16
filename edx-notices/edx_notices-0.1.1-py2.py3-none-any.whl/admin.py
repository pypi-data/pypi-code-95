"""Admin pages for the notices app."""
from django.contrib import admin

from .models import AcknowledgedNotice, Notice, TranslatedNoticeContent


# Unregistered because we only want these CRUD-ed through the Notice Admin
class TranslatedNoticeContentAdmin(admin.TabularInline):
    model = TranslatedNoticeContent


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    inlines = [TranslatedNoticeContentAdmin]


@admin.register(AcknowledgedNotice)
class AcknowledgedNoticeAdmin(admin.ModelAdmin):
    pass
