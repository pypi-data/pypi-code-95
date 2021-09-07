from operator import attrgetter

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from .choices import InternalType, AggregateFunctionChoices
from .managers import (
    DBTableQuerySet,
    TableFieldQuerySet,
    FormatQuerySet,
    PatternFieldQuerySet,
)


# region Абстрактные модели


class AbstractRDAuthor(models.Model):
    """
    Абстрактная модель: "Автор"
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Автор'),
        related_name='rd_%(class)ss',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class AbstractRDField(models.Model):
    """
    Абстрактная модель: "Поле"
    """

    name = models.CharField(verbose_name=_('Наименование'), max_length=200)
    alias = models.CharField(verbose_name=_('Псевдоним'), max_length=200, blank=True)
    representation = models.ForeignKey(
        'Format',
        verbose_name=_('Представление'),
        related_name='%(class)s_fields',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True
        ordering = ('-pk',)

    def __str__(self):
        return self.name


# endregion Абстрактные модели


# region Основные модели


class DBTable(models.Model):
    """
    Сущность: Таблица БД
    """

    table = models.ForeignKey(ContentType, verbose_name=_('Таблица'), on_delete=models.CASCADE)
    alias = models.CharField(verbose_name=_('Псевдоним'), max_length=200, unique=True)
    is_visible = models.BooleanField(verbose_name=_('Отображение'), default=True)

    objects = DBTableQuerySet.as_manager()

    class Meta:
        verbose_name = _('Таблица БД')
        verbose_name_plural = _('Таблицы БД')
        ordering = ('-pk',)

    def __str__(self):
        return f'{self.alias} ({self.table.name})'

    @cached_property
    def can_delete(self):
        """
        Проверка: можно ли удалить таблицу
        """
        return not self.patterns.exists()

    def reload_fields(self):
        """
        Актуализация полей таблицы
        """
        # Создание полей таблицы
        fields = []
        for field in self.table.model_class()._meta.get_fields():
            # Проверка связи поля
            related_model = getattr(field, 'related_model', None)
            related_name = getattr(field, 'related_name', None)

            # Получение аттрибутов моделей в зависимости от связи
            if field.is_relation and related_model:
                name = field.verbose_name if hasattr(field, 'verbose_name') else field.remote_field.verbose_name
                name = f'{name} ({related_model._meta.verbose_name})'
            else:
                name = field.verbose_name
            db_field = related_name or field.name
            fields.append(TableField(db_table=self, name=name, db_field=db_field, is_relation=field.is_relation))
        TableField.objects.bulk_create(fields)


class PatternGroup(models.Model):
    """
    Сущность: Группа шаблона
    """

    name = models.CharField(verbose_name=_('Наименование'), max_length=200, unique=True)

    class Meta:
        verbose_name = _('Группа шаблона')
        verbose_name_plural = _('Группы шаблонов')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    @cached_property
    def can_delete(self):
        """
        Проверка: можно ли удалить группу
        """
        return not self.patterns.exists()


class Pattern(AbstractRDAuthor):
    """
    Сущность: Шаблон
    """

    name = models.CharField(verbose_name=_('Наименование'), max_length=200, unique=True)
    updated = models.DateTimeField(verbose_name=_('Дата и время обновления'), auto_now=True)
    groups = models.ManyToManyField('PatternGroup', verbose_name=_('Группы шаблонов'), related_name='patterns')
    root = models.ForeignKey(
        'DBTable',
        verbose_name=_('Основная таблица'),
        related_name='root_table_patterns',
        on_delete=models.CASCADE,
    )
    tables = models.ManyToManyField(
        'DBTable',
        verbose_name=_('Таблицы БД'),
        related_name='patterns',
    )
    is_visible_in_patterns = models.BooleanField(
        verbose_name=_('Отображать в перечне шаблонов при формировании нового шаблона'),
        default=True,
    )

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = _('Шаблоны')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    @cached_property
    def can_delete(self):
        """
        Проверка: можно ли удалить шаблон
        """
        return not self.reports.exists()

    @cached_property
    def field_last_order(self):
        """
        Получение последнего порядкового номера поля в шаблоне
        """
        return self.pattern_fields.aggregate(max_order=Coalesce(Max('order'), -1)).get('max_order') + 1

    @cached_property
    def field_names(self):
        """
        Поля шапки шаблона
        """
        pattern_fields = self.pattern_fields.order_by('order')
        return pattern_fields.annotate(field_name=Coalesce('alias', 'name')).values_list('field_name', flat=True)

    @cached_property
    def field_lookups(self):
        """
        Поля шаблона для выборки
        """
        pattern_fields = self.pattern_fields.order_by('order')
        return list(map(attrgetter('lookup'), pattern_fields))

    @cached_property
    def virtual_fields(self):
        """
        Получение виртуальных полей шаблона
        """
        return self.pattern_fields.exclude(expression__iexact='')


class Format(models.Model):
    """
    Сущность: Формат
    """

    name = models.CharField(verbose_name=_('Наименование в БД'), max_length=200, unique=True)
    internal_type = models.SmallIntegerField(verbose_name=_('Тип поля'), choices=InternalType.CHOICES)
    representation = models.CharField(verbose_name=_('Представление'), max_length=1000)

    objects = FormatQuerySet.as_manager()

    class Meta:
        verbose_name = _('Формат')
        verbose_name_plural = _('Форматы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    @cached_property
    def can_delete(self):
        """
        Проверка: можно ли удалить формат
        """
        return not (self.tablefield_fields.exists() or self.patternfield_fields.exists())


class Report(AbstractRDAuthor):
    """
    Сущность: Отчет
    """

    pattern = models.ForeignKey(
        Pattern,
        verbose_name=_('Шаблон отчета'),
        related_name='reports',
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name=_('Наименование'), max_length=1000, unique=True)
    created = models.DateTimeField(verbose_name=_('Дата и время создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Отчет')
        verbose_name_plural = _('Отчеты')
        ordering = ('-pk',)

    def __str__(self):
        return self.name


class TableField(AbstractRDField):
    """
    Сущность: Поле таблицы БД
    """

    db_table = models.ForeignKey(
        DBTable,
        verbose_name=_('Таблица БД'),
        related_name='fields',
        on_delete=models.CASCADE,
    )
    db_field = models.CharField(verbose_name=_('Поле таблицы БД'), max_length=200)
    is_visible = models.BooleanField(verbose_name=_('Отображение'), default=True)
    is_relation = models.BooleanField(verbose_name=_('Связанное поле'), default=False)

    objects = TableFieldQuerySet.as_manager()

    class Meta(AbstractRDField.Meta):
        verbose_name = _('Поле таблицы БД')
        verbose_name_plural = _('Поля таблиц БД')
        unique_together = (
            'db_table',
            'name',
            'db_field',
        )


class PatternRelationAbstract(models.Model):
    """
    Абстрактная модель связи
    """

    relation = models.ForeignKey(
        'PatternRelation', verbose_name=_('Условие связи'), blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True

    @cached_property
    def relation_lookup(self):
        """
        Путь до поля
        """
        if self.relation:
            return f'__'.join(
                self.relation.get_ancestors(include_self=True).values_list('table_field__db_field', flat=True)
            )


class PatternField(PatternRelationAbstract, AbstractRDField):
    """
    Сущность: Поле шаблона отчета
    """

    pattern = models.ForeignKey(
        Pattern,
        verbose_name=_('Шаблон отчета'),
        related_name='pattern_fields',
        on_delete=models.CASCADE,
    )
    field = models.ForeignKey(
        TableField,
        verbose_name=_('Поле таблицы БД'),
        related_name='pattern_fields',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    expression = models.CharField(verbose_name=_('Выражение'), max_length=2000, blank=True)
    internal_type = models.SmallIntegerField(
        verbose_name=_('Тип поля'),
        choices=InternalType.CHOICES,
        blank=True,
        null=True,
    )
    order = models.PositiveSmallIntegerField(verbose_name=_('Порядковый номер'), default=0)
    is_virtual = models.BooleanField(verbose_name=_('Виртуальное поле'), default=False)
    is_group = models.BooleanField(verbose_name=_('Групповое поле'), default=False)
    is_sort = models.BooleanField(verbose_name=_('Сортировочное поле'), default=False)
    reverse_sort = models.BooleanField(verbose_name=_('Обратная сортировка'), default=False)
    is_aggregate = models.BooleanField(
        verbose_name=_('Агрегированное поле'),
        default=False,
        help_text=_('Аггрегация производится для групповых полей шаблона'),
    )
    aggregate_function = models.CharField(
        verbose_name=_('Функция агрегирования'),
        blank=True,
        null=True,
        max_length=20,
        choices=AggregateFunctionChoices.CHOICES,
    )

    objects = PatternFieldQuerySet.as_manager()

    class Meta(AbstractRDField.Meta):
        verbose_name = _('Поле шаблона отчета')
        verbose_name_plural = _('Поля шаблонов отчетов')
        ordering = ('order', '-pk')

    @property
    def model_field(self):
        """
        Настойщее поле модели
        """
        if self.field:
            table = self.field.db_table.table
            return table.model_class()._meta.get_field(self.field.db_field)

    def get_field_internal_type(self):
        """
        Получение типа поля для полей таблиц
        """
        field = self.model_field
        if field:
            return field.get_internal_type()

    @cached_property
    def lookup(self):
        """
        Полный путь до поля
        """
        return f'__'.join(filter(None, [self.relation_lookup, self.field.db_field]))


class PatternFilter(PatternRelationAbstract):
    """
    Условия выборки
    """

    pattern = models.ForeignKey(
        Pattern,
        verbose_name=_('Шаблон отчета'),
        related_name='pattern_filters',
        on_delete=models.CASCADE,
    )
    relation = models.ForeignKey(
        'PatternRelation', verbose_name=_('Условие связи'), blank=True, null=True, on_delete=models.SET_NULL
    )
    expression = models.CharField(verbose_name=_('Выражение'), max_length=2000, blank=True)

    class Meta:
        verbose_name = _('Условие выборки внутри шаблона')
        verbose_name_plural = _('Условия выборки внутри шаблонов')
        ordering = ('-pk',)

    def __str__(self):
        return f'Условие выборки для {self.pattern}'


class PatternRelation(MPTTModel):
    """
    Связи таблиц внутри шаблона
    """

    pattern = models.ForeignKey(
        Pattern,
        verbose_name=_('Шаблон отчета'),
        related_name='pattern_relations',
        on_delete=models.CASCADE,
    )
    name = models.CharField(verbose_name=_('Наименование'), max_length=200)
    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        verbose_name=_('Родительская связь'),
        on_delete=models.SET_NULL,
    )
    table_field = models.ForeignKey(TableField, verbose_name=_('Поле таблицы'), on_delete=models.CASCADE)
    target = models.ForeignKey(
        DBTable,
        verbose_name=_('Связанная таблица'),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = _('Связь таблиц внутри шаблона')
        verbose_name_plural = _('Связи таблиц внутри шаблонов')
        ordering = ('-pk',)
        unique_together = (
            'pattern',
            'name',
        )

    def __str__(self):
        return self.name

    @cached_property
    def start_table(self):
        """
        Стартовая таблица
        """
        return self.table_field.db_table.alias

    @cached_property
    def end_table(self):
        """
        Конечная таблица
        """
        return self.target.alias


# endregion Основные модели
