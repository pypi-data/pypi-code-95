# -*- coding: utf-8 -*-
from .cell import Cell
import os, re
from src.utils import my_tools


class Section(object):
    """
    Une section d'un page web
    """

    section_title = ""
    translations = ""
    cells = ""

    def __init__(self, section, page_directory):
        self.id = section["id"]
        self.orig_id = section["origId"]
        self.page_id = section["pageId"]
        self.order_no = section["orderNo"]
        self.border_style = section["borderStyle"]
        self.columns = section["columns"]
        self.view_tab_no = section["viewTabNo"]
        self.page_col_no = section["pageColNo"]
        self.is_collapsable = section["isCollapsable"]
        self.is_default = section["isDefault"]
        self.hide_mobile = section["hideMobile"]
        self.do_not_synch = section["doNotSynch"]
        if hasattr(section, "SectionTitle"):
            self.section_title = section.SectionTitle.cdata
        if hasattr(section, "Translations"):
            if hasattr(section.Translations, "Translation"):
                self.translations = section.Translations.Translation
        if hasattr(section, "PageCells"):
            if hasattr(section.PageCells, "PageCell"):
                self.cells = section.PageCells.PageCell
        dirname = my_tools.mysplit(self.section_title, 50)
        self.section_directory = "{}/{}".format(page_directory, dirname)

    def to_file(self):
        # fichier de propriétés
        if not os.path.exists(self.section_directory.encode('utf-8')):
            os.makedirs(self.section_directory.encode('utf-8'))
        with open("{}/PROPERTIES.md".format(self.section_directory), 'w+', encoding='utf-8') as file:
            # nom de l'objet
            file.write("# {}\n".format(self.section_title))

            # Informations
            file.write("\n\n## Informations\n")
            file.write("- id : {}\n".format(self.id))
            file.write("- origId : {}\n".format(self.orig_id))
            file.write("- pageId : {}\n".format(self.page_id))
            file.write("- orderNo : {}\n".format(self.order_no))
            file.write("- borderStyle : {}\n".format(self.border_style))
            file.write("- columns : {}\n".format(self.columns))
            file.write("- viewTabNo : {}\n".format(self.view_tab_no))
            file.write("- pageColNo : {}\n".format(self.page_col_no))
            file.write("- [{}] isCollapsable\n".format("X" if self.is_collapsable == "true" else " "))
            file.write("- [{}] isDefault\n".format("X" if self.is_default == "true" else " "))
            file.write("- [{}] hideMobile\n".format("X" if self.hide_mobile == "true" else " "))
            file.write("- [{}] doNotSynch\n".format("X" if self.do_not_synch == "true" else " "))

            if self.translations:
                file.write("## Traductions\n")
                file.write("|code|nom|text|\n")
                file.write("|---|---|---|\n")
                for trans in self.translations:
                    file.write("|{}|{}|{}|\n".format(trans["langCode"], trans["fieldName"], trans["text"]))

        if self.cells:
            for cell in self.cells:
                new_cell = Cell(cell, self.section_directory)
                new_cell.to_file()
