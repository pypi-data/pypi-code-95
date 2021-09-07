from django.contrib import admin

from .models import (
    Pattern,
    PatternGroup,
    DBTable,
    Format,
    Report,
    TableField,
    PatternField,
    PatternRelation,
    PatternFilter,
)


@admin.register(DBTable)
class DBTableAdmin(admin.ModelAdmin):
    """
    Сущность "Таблица БД" в административной панели
    """

    list_display = (
        'table',
        'alias',
        'is_visible',
    )
    search_fields = ('alias',)
    list_filter = ('is_visible',)
    list_display_links = (
        'table',
        'alias',
    )


@admin.register(PatternGroup)
class PatternGroupAdmin(admin.ModelAdmin):
    """
    Сущность "Группа шаблона" в административной панели
    """

    list_display = ('name',)
    search_fields = ('name',)
    list_display_links = list_display


@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    """
    Сущность "Шаблон" в административной панели
    """

    list_display = (
        'name',
        'author',
        'updated',
        'is_visible_in_patterns',
    )
    search_fields = ('name',)
    autocomplete_fields = (
        'tables',
        'groups',
        'root',
    )
    list_filter = ('is_visible_in_patterns',)
    list_display_links = ('name',)


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
    """
    Сущность "Формат" в административной панели
    """

    list_display = (
        'name',
        'internal_type',
    )
    search_fields = ('name',)
    list_display_links = ('name',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """
    Сущность "Отчет" в административной панели
    """

    list_display = (
        'name',
        'author',
        'created',
    )
    search_fields = ('name',)
    autocomplete_fields = ('pattern',)
    list_display_links = ('name',)


@admin.register(TableField)
class TableFieldAdmin(admin.ModelAdmin):
    """
    Сущность "Поле таблицы БД" в административной панели
    """

    list_display = (
        'name',
        'alias',
        'db_table',
        'db_field',
        'is_visible',
    )
    search_fields = (
        'name',
        'alias',
    )
    autocomplete_fields = (
        'db_table',
        'representation',
    )
    list_filter = ('is_visible',)
    list_display_links = ('name',)


@admin.register(PatternField)
class PatternFieldAdmin(admin.ModelAdmin):
    """
    Сущность "Поле таблицы БД" в административной панели
    """

    list_display = (
        'name',
        'alias',
        'pattern',
        'field',
        'order',
    )
    search_fields = (
        'name',
        'alias',
        'pattern__name',
        'field__name',
    )
    autocomplete_fields = (
        'pattern',
        'field',
        'representation',
    )
    list_display_links = ('name',)


@admin.register(PatternRelation)
class PatternRelationAdmin(admin.ModelAdmin):
    """
    Сущность "Связь таблиц внутри шаблона" в административной панели
    """

    list_display = (
        'pk',
        'pattern',
        'name',
        'target',
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    autocomplete_fields = (
        'pattern',
        'table_field',
        'target',
    )


@admin.register(PatternFilter)
class PatternRelationAdmin(admin.ModelAdmin):
    """
    Сущность "Условия выборки" в административной панели
    """

    list_display = (
        'pk',
        'pattern',
        'expression',
    )
    list_display_links = (
        'pattern',
        'expression',
    )
    search_fields = ('pattern__name',)
    autocomplete_fields = (
        'pattern',
        'relation',
    )
