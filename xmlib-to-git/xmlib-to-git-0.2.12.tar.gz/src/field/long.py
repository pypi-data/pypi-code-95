# -*- coding: utf-8 -*-
from .core import BaseField


class LongField(BaseField):
    """ Classe pour les champs de type File
            - Infos
            - DisplayLabel
            - Description
            - traductions
            - propriétés (liste d'éléments Props)
        """

    def to_file(self):
        super().to_file()

        with open("{}/PROPERTIES.md".format(self.field_dir), 'a+', encoding='utf-8') as file:
            file.write("## List Item\n")
            file.write("|id|origId|orderNo|source|name|code|mainItemId|isDefault|\n")
            file.write("|---|---|---|---|---|---|---|---|\n")
            for list_item in self.list_items:
                file.write("|{}|{}|{}|{}|{}|{}|{}|{}|\n".format(
                    list_item["id"],
                    list_item["origId"],
                    list_item["orderNo"],
                    list_item["source"],
                    list_item["name"],
                    list_item["code"],
                    list_item["mainItemId"],
                    list_item["isDefault"]
                ))
