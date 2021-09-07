from report_designer.core.tables import AbstractTable, CellTypeCenter, CellTypeBoolean


class FormatTable(AbstractTable):
    """
    Таблица списка форматов
    """

    def create_header(self, header):
        level_0 = [
            header('Наименование'),
            header('Тип поля'),
            header('Представление'),
        ]
        return [level_0]

    def create_cells(self, obj):
        cell = self.cell_class
        return [
            cell(obj.name, cell_type=CellTypeCenter),
            cell(obj.get_internal_type_display(), cell_type=CellTypeCenter),
            cell(obj.representation, cell_type=CellTypeCenter),
        ]
