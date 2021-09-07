from django.core.exceptions import FieldDoesNotExist
from django.db.models import (
    QuerySet,
    Prefetch,
    BooleanField,
    Value,
    When,
    Case,
    F,
    CharField,
    Exists,
    OuterRef,
)

from report_designer.choices import InternalType


class BaseIsVisibleQuerySet(QuerySet):
    """
    QuerySet видимых в констркуторе сущностей
    """

    is_visible_field = 'is_visible'

    def is_visible(self):
        """
        Видимые сущности
        """
        return self.filter(**{self.is_visible_field: True})


class TableFieldQuerySet(BaseIsVisibleQuerySet):
    """
    QuerySet полей таблиц БД
    """

    def available_for_pattern(self, pattern):
        """
        Поля доступные для шаблона
        """
        return self.is_visible().filter(db_table__patterns=pattern).distinct()

    def is_relation(self):
        """
        Поля связи
        """
        return self.filter(is_relation=True)

    def is_not_relation(self):
        """
        Поля связи
        """
        return self.filter(is_relation=False)

    def for_pattern_relation(self, db_table, pattern):
        """
        Поля для таблицы
        """
        from .models import DBTable

        fields = self.is_relation().filter(db_table=db_table)
        db_table_model = db_table.table.model_class()

        # Получение параметров целевой таблицы
        app_labels, model_names = [], []
        for bunch in fields.values('pk', 'db_field'):
            try:
                meta = db_table_model._meta.get_field(bunch.get('db_field')).related_model._meta
                app_labels.append(When(pk=bunch.get('pk'), then=Value(meta.app_label)))
                model_names.append(When(pk=bunch.get('pk'), then=Value(meta.model_name)))
            except FieldDoesNotExist as e:
                pass

        # Аннотация параметров целевых таблиц
        fields = fields.annotate(
            app_label=Case(*app_labels, output_field=CharField()),
            model_name=Case(*model_names, output_field=CharField()),
        )

        # Аннотация флага существования таблицы в системе и фильтрация
        pattern_tables = pattern.tables.values_list('pk', flat=True)
        subquery = DBTable.objects.filter(
            table__app_label=OuterRef('app_label'), table__model=OuterRef('model_name'), pk__in=pattern_tables
        )
        return fields.annotate(table_exists=Exists(subquery)).filter(table_exists=True)


class DBTableQuerySet(BaseIsVisibleQuerySet):
    """
    QuerySet таблиц БД
    """

    def available(self, is_relation=False):
        """
        Доступные для выбора таблицы

        Таблицы попадаюбт в выборку:
        - если отображаются в конструкторе
        - если имеют поля, отображаемые в конструкторе
        """
        from report_designer.models import TableField

        tables = self.is_visible().filter(fields__is_visible=True)
        prefetch = Prefetch('fields', TableField.objects.is_visible().filter(is_relation=is_relation))
        return tables.prefetch_related(prefetch).distinct()


class FormatQuerySet(BaseIsVisibleQuerySet):
    """
    QuerySet форматов
    """

    def available_for_field(self, table, field):
        """
        Список допустимых форматов для поля модели
        """
        choice_name = table.model_class()._meta.get_field(field).get_internal_type()
        internal_type = InternalType.get_value_by_internal_type(choice_name)
        return self.filter(internal_type=internal_type)


class PatternFieldQuerySet(QuerySet):
    """
    QuerySet полей шаблона
    """

    def with_relation(self):
        """
        Поля, имеющие связь
        """
        return self.filter(relation__isnull=False)

    def without_relation(self):
        """
        Поля, не имеющие связь
        """
        return self.filter(relation__isnull=True)

    def is_virtual(self):
        """
        Виртуальные поля
        """
        return self.filter(is_virtual=True)

    def is_group(self):
        """
        Виртуальные поля
        """
        return self.filter(is_group=True)

    def with_relation_options(self):
        """
        Поля, с аннотацией существования связи
        """
        relation_exists = Case(
            When(relation__isnull=True, then=Value(False)), default=Value(True), output_field=BooleanField()
        )
        relation_need = Case(
            When(field__db_table=F('pattern__root'), then=Value(False)),
            default=Value(True),
            output_field=BooleanField(),
        )
        return self.annotate(relation_exists=relation_exists, relation_need=relation_need)
