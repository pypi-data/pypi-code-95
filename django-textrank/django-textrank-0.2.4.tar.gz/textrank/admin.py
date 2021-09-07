#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.contrib import admin
from textrank import models


class WeightInline(admin.StackedInline):
    model = models.Weight
    extra = 0


class GroupAdmin(admin.ModelAdmin):
    # save_as = True
    date_hierarchy = 'updated'
    list_display = (
        'name', 'is_active', 'updated', 'last_editor', 'id',
    )
    list_filter = ['is_active', 'updated']
    search_fields = ['name']


class KeywordAdmin(admin.ModelAdmin):
    save_as = True
    date_hierarchy = 'updated'
    list_display = (
        'word', 'is_active', 'updated', 'last_editor', 'id',
    )
    list_filter = ['is_active', 'updated']
    search_fields = ['word']
    inlines = [WeightInline]


class WeightAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated'
    list_display = (
        'keyword', 'value', 'group', 'updated', 'last_editor', 'id',
    )
    list_filter = ['group__is_active', 'keyword__is_active', 'updated']
    search_fields = ['group__name', 'keyword__word']

    def get_queryset(self, *args, **kwargs):
        qs = super().get_queryset(*args, **kwargs)
        return qs.select_related('group', 'keyword')


register = admin.site.register
register(models.Group, GroupAdmin)
register(models.Keyword, KeywordAdmin)
register(models.Weight, WeightAdmin)
