import re
from io import StringIO

from django.db.models import QuerySet
from django.http import QueryDict
from django.utils.html import escape
from django.utils.safestring import mark_safe

from report_designer.core.utils import RenderMixin, format_date


# region Миксины таблиц

class TablePartMethodsMixin:
    """
    Миксин с методами со вспомогательными методами для частей таблиц
    """

    def prepare_attrs(self, attrs: dict, prefix: str = None):
        """
        Подготовка аттрибутов
        """
        prefix = prefix and f'{prefix}-' or ''
        return ' '.join(
            f'{prefix}{key.replace("_", "-")}="{escape(value)}"'
            for key, value in attrs.items()
        )

    def data_attrs(self, attrs: dict):
        """
        Подготовка data-аттрибутов
        :param attrs: Добавляемые аттрибуты
        """
        return self.prepare_attrs(attrs, 'data')


# endregion Миксины таблиц


# region Шапка таблицы

class HeaderItem:
    """
    Ячейка шапки таблицы
    """

    def __init__(self, name, col_span=None, row_span=None, ordering=None, **kwargs):
        """
        :param name: Название ячейки шапки
        :param col_span: Количествозанимаемых колонок
        :param row_span: Количество занимаемых строк
        """
        self.name = name
        self.col_span = col_span
        self.row_span = row_span
        self.ordering = ordering

# endregion Шапка таблицы


# region Строки таблицы


class TableRow(TablePartMethodsMixin):
    """
    Строка таблицы
    """

    base_classes = ''

    def __init__(self, cells, object_id=None, classes='', data=None, **kwargs):
        self.cells = cells or []
        self.object_id = object_id
        self.additional_classes = classes
        self.additional_data = data

    def get_row_classes(self):
        """
        Получение классов для строки
        """
        classes = ' '.join([self.base_classes, self.additional_classes or ''])
        return re.sub(r'\s+', ' ', classes).strip()

    def data(self):
        """
        Data-параметры
        """
        return self.data_attrs(self.additional_data or {})

    def __len__(self):
        return len(self.cells)

    def __iter__(self):
        for cell in self.cells:
            yield cell


# endregion Строки таблицы


# region Ячейки таблицы

class CellType:
    """
    Базовый класс для типов ячеек работующих на основе форматирования значений
    """

    align = 'left'

    def __init__(self, cell):
        self.cell = cell

    def render(self):
        """
        Рендер ячейки в HTML
        """
        # Аттрибуты ячейки
        _cell_attrs = (
            ('class', self.cell.td_classes),
            ('col_span', self.cell.col_span),
            ('rowspan', self.cell.row_span),
            ('style', self.cell.style),
        )
        cell_attrs = ' '.join([f'{key}="{value}"' for key, value in _cell_attrs if value])

        # Аттрибуты ссылки, если есть
        _link_attrs = (
            ('href', self.cell.url),
            ('target', self.cell.target or '_self'),
            ('class', self.cell.link_class),
            ('style', 'display: block;'),
        )
        link_attrs = ' '.join([f'{key}="{value}"' for key, value in _link_attrs if value])
        value_part = ''.join([
            self.cell.url and f'<a {link_attrs} {self.cell.link_html_attrs}>' or '',
            f'<div class="{self.cell.div_classes}">{self._format_value()}</div>',
            self.cell.url and '</a>' or '',
        ])

        # Шаблон ячейки
        template = f'<td {cell_attrs} {self.cell.td_data_attrs}>{value_part}</td>'
        rendered_cell = StringIO()
        rendered_cell.write(template)
        cell_html = rendered_cell.getvalue()
        rendered_cell.close()
        return cell_html

    def _format_value(self):
        """
        Общее форматирование значения ячейки
        """
        return self.cell.value


class CellTypeDefault(CellType):
    """
    Тип ячейки по умолчанию
    """

    align = 'left'
    default_value = '&ndash;'

    def _format_value(self):
        return self.cell.value or self.default_value


class CellTypeCenter(CellTypeDefault):
    """
    Тип ячейки с выравниванием по центру
    """

    align = 'center'


class CellTypeDateTime(CellType):
    """
    Тип ячейки для вывода дат и лет с временем
    """

    align = 'center'

    def _html_format(self):
        return format_date(self.cell.value, format='d.m.Y в H:i') or '&ndash;'


class CellTypeDate(CellTypeCenter):
    """
    Тип ячейки для вывода дат и лет
    """

    align = 'center'

    def _format_value(self):
        return format_date(self.cell.value) or self.default_value


class CellTypeBoolean(CellTypeCenter):
    """
    Тип ячейки для вывода значения "Да"-"Нет"
    """

    def _format_value(self):
        return 'Да' if self.cell.value else 'Нет'


class BaseCell:
    """
    Базовая ячейка таблицы
    """

    def __init__(
        self,
        value,
        align=None,
        col_span=None,
        row_span=None,
        cell_type=CellTypeDefault,
        bold=False,
        background_color=None,
        text_color=None,
        **kwargs,
    ):
        self.value = value
        self.cell_type = cell_type(self)
        self.col_span = col_span
        self.row_span = row_span
        self.background_color = background_color
        self.bold = bold
        self.text_color = text_color

        if not align:
            align = self.cell_type.align
        self.align = align

    def render(self):
        return self.cell_type.render()


class Cell(TablePartMethodsMixin, BaseCell):
    """
    Ячейка таблицы
    """

    def __init__(
        self, value, url=None, css_class=None, html_width=None, target=None, td_classes=None, **kwargs,
    ):
        self.url = url
        self.css_class = css_class
        self.html_width = html_width
        self.target = target

        super().__init__(value, **kwargs)

        self._td_data_attrs = kwargs.get('td_data_attrs', {})
        self._div_classes = kwargs.get('div_classes', '')
        self._link_html_attrs = kwargs.get('link_html_attrs', {})
        self.td_classes = td_classes
        self.link_class = kwargs.get('link_class', '')

    def __str__(self):
        return mark_safe(self.render())

    @property
    def style(self):
        """
        Стили ячейки
        """
        style = ''
        if self.html_width:
            style += f'width:{self.html_width}px;'
        if self.background_color:
            style += f'background-color:#{self.background_color};'
        return style

    @property
    def div_style(self):
        """
        Стили тега обертки значения
        """
        style = ''
        if self.text_color:
            style += f'color:#{self.text_color}; '
        return style

    @property
    def div_classes(self):
        """
        Классы тега обертки значения
        """
        if self.align:
            self._div_classes += f' text-{self.align.lower()}'
        if self.bold:
            self._div_classes += ' font_bold'
        return self._div_classes

    @property
    def td_data_attrs(self):
        """
        Data-атрибуты ячейки
        """
        return self.data_attrs(self._td_data_attrs)

    @property
    def link_html_attrs(self):
        """
        Метод для получения html-атрибутов для ссылки <a></a>
        """
        return self.prepare_attrs(self._link_html_attrs)


# endregion Ячейки таблицы


class AbstractTable(RenderMixin):
    """
    Таблица вывода выборки
    """

    template_name = 'report_designer/core/tables/table.html'

    header_class = HeaderItem
    row_class = TableRow
    cell_class = Cell

    context_object_name = 'table'

    # Аттрибуты таблицы
    base_classes = 'table table-hover'
    empty_message = 'Данные отсутствуют'

    def __init__(
            self,
            queryset: QuerySet,
            # request_get: QueryDict
    ):
        self._queryset = queryset
        # self._request_get = request_get

        # Параметры таблицы
        self._header = []
        self._rows = []

    def create_table(self):
        """
        Создание таблицы
        """
        self._header = self.create_header(self.header_class)
        self.create_body()

    def create_body(self):
        """
        Формирование тела таблицы
        """
        for obj in self.get_queryset():
            row = self.create_row(obj)
            self._add_row(row)

    def create_row(self, obj):
        """
        Формирование строки тела таблицы
        """
        cells = self.create_cells(obj)
        return self.row_class(
            cells, object_id=obj.pk, classes=self.get_row_classes(obj), data=self.get_row_data_attrs(obj),
        )

    def create_header(self, header):
        """
        Создание шапки таблицы
        """
        return []

    def _add_row(self, row):
        """
        Добавление строки
        """
        self._rows.append(row)

    def create_cells(self, obj):
        """
        Создание ячеек строки
        """
        return []

    def get_queryset(self):
        """
        Выборка таблицы
        """
        return self._queryset

    def get_table_classes(self):
        """
        Получение классов для таблицы
        """
        return self.base_classes

    def get_row_classes(self, obj):
        """
        Получение классов для таблицы
        """
        return ''

    def get_row_data_attrs(self, obj):
        """
        Получение data-аттрибутов для строки
        """
        return {}

    @property
    def is_data_exists(self):
        """
        Есть ли данные в таблице
        """
        return bool(self._rows)

    def get_context_data(self):
        context_data = super().get_context_data()
        context_data.update({
            'empty_message': self.empty_message,
            'header': self._header,
            'rows': self._rows,
            'classes': self.get_table_classes(),
        })
        return context_data
