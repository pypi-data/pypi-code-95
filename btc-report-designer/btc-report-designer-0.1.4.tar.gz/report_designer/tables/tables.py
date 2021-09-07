from report_designer.core.tables import (AbstractTable, CellTypeBoolean, CellTypeCenter,)


class DBTableTable(AbstractTable):
    """
    Таблица списка таблиц базы данных
    """

    def create_header(self, header):
        level_0 = [
            header('Таблицы БД'),
            header('Псевдоним'),
            header('Отображать в конструкторе'),
        ]
        return [level_0]

    def create_cells(self, obj):
        cell = self.cell_class
        return [
            cell(obj.table, cell_type=CellTypeCenter),
            cell(obj.alias, cell_type=CellTypeCenter),
            cell(obj.is_visible, cell_type=CellTypeBoolean),
        ]
