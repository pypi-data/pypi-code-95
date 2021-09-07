from django.utils.translation import ugettext_lazy as _


class InternalType:
    """
    Тип поля
    """

    AUTO_FIELD = 0
    BIG_AUTO_FIELD = 1
    BINARY_FIELD = 2
    BOOLEAN_FIELD = 3
    CHAR_FIELD = 4
    DATE_FIELD = 5
    DATE_TIME_FIELD = 6
    DECIMAL_FIELD = 7
    DURATION_FIELD = 8
    FILE_FIELD = 9
    IMAGE_FIELD = 10
    FILE_PATH_FIELD = 11
    FLOAT_FIELD = 12
    INTEGER_FIELD = 13
    BIG_INTEGER_FIELD = 14
    GENERIC_IP_ADDRESS_FIELD = 15
    NULL_BOOLEAN_FIELD = 16
    POSITIVE_INTEGER_FIELD = 17
    POSITIVE_SMALL_INTEGER_FIELD = 18
    SLUG_FIELD = 19
    SMALL_INTEGER_FIELD = 20
    TEXT_FIELD = 21
    TIME_FIELD = 22
    URL_FIELD = 23
    UUID_FIELD = 24

    # Соотношение значений с реальными полями
    INTERNAL_TYPES = (
        (AUTO_FIELD, 'AutoField'),
        (BIG_AUTO_FIELD, 'BigAutoField'),
        (BINARY_FIELD, 'BinaryField'),
        (BOOLEAN_FIELD, 'BooleanField'),
        (CHAR_FIELD, 'CharField'),
        (DATE_FIELD, 'DateField'),
        (DATE_TIME_FIELD, 'DateTimeField'),
        (DECIMAL_FIELD, 'DecimalField'),
        (DURATION_FIELD, 'DurationField'),
        (FILE_FIELD, 'FileField'),
        (IMAGE_FIELD, 'ImageField'),
        (FILE_PATH_FIELD, 'FilePathField'),
        (FLOAT_FIELD, 'FloatField'),
        (INTEGER_FIELD, 'IntegerField'),
        (BIG_INTEGER_FIELD, 'BigIntegerField'),
        (GENERIC_IP_ADDRESS_FIELD, 'GenericIPAddressField'),
        (NULL_BOOLEAN_FIELD, 'NullBooleanField'),
        (POSITIVE_INTEGER_FIELD, 'PositiveIntegerField'),
        (POSITIVE_SMALL_INTEGER_FIELD, 'PositiveSmallIntegerField'),
        (SLUG_FIELD, 'SlugField'),
        (SMALL_INTEGER_FIELD, 'SmallIntegerField'),
        (TEXT_FIELD, 'TextField'),
        (TIME_FIELD, 'TimeField'),
        (URL_FIELD, 'URLField'),
        (UUID_FIELD, 'UUIDField'),
    )

    CHOICES = (
        (AUTO_FIELD, _('Автоинкрементное')),
        (BIG_AUTO_FIELD, _('Автоинкрементное (64-битное)')),
        (BINARY_FIELD, _('Бинарное')),
        (BOOLEAN_FIELD, _('Логическое')),
        (CHAR_FIELD, _('Строковое')),
        (DATE_FIELD, _('Дата')),
        (DATE_TIME_FIELD, _('Дата и время')),
        (DECIMAL_FIELD, _('Десятичное с фиксированной точностью')),
        (DURATION_FIELD, _('Период времени (в микросекундах)')),
        (FILE_FIELD, _('Файл')),
        (IMAGE_FIELD, _('Изображение')),
        (FILE_PATH_FIELD, _('Путь до файла')),
        (FLOAT_FIELD, _('Число с плавающей точкой')),
        (INTEGER_FIELD, _('Целочисленное')),
        (BIG_INTEGER_FIELD, _('Целочисленное (64-битное)')),
        (GENERIC_IP_ADDRESS_FIELD, _('IP адрес')),
        (NULL_BOOLEAN_FIELD, _('Логическое с нулевым значением')),
        (POSITIVE_INTEGER_FIELD, _('Положительное целочисленное')),
        (POSITIVE_SMALL_INTEGER_FIELD, _('Положительное целочисленное (16-битное)')),
        (SLUG_FIELD, _('Название-метка')),
        (SMALL_INTEGER_FIELD, _('Целочисленное (16-битное)')),
        (TEXT_FIELD, _('Текстовое')),
        (TIME_FIELD, _('Время')),
        (URL_FIELD, _('URL')),
        (UUID_FIELD, _('UUID')),
    )

    @classmethod
    def get_internal_type(cls, choice_name: int):
        return dict(cls.INTERNAL_TYPES).get(choice_name, choice_name)

    @classmethod
    def get_value_by_internal_type(cls, choice_name: int):
        return dict(map(reversed, cls.INTERNAL_TYPES)).get(choice_name, choice_name)

    @classmethod
    def get_display_value(cls, choice_name: int):
        return dict(cls.CHOICES).get(choice_name, choice_name)


class AggregateFunctionChoices:
    """
    Функции агрегирования
    """

    SUM = 'sum'
    MEAN = 'mean'
    MAX = 'max'
    MIN = 'min'

    ITEMS = (
        SUM,
        MEAN,
        MAX,
        MIN,
    )

    CHOICES = (
        (SUM, _('Сумма')),
        (MEAN, _('Среднее')),
        (MAX, _('Максимальное')),
        (MIN, _('Минимальное')),
    )
