# -*- coding: utf-8 -*-

import os, re
from .section import Section
from src.utils import my_tools


class WebPage(object):
    """
    Défini une page Rollase (webpage)
    """
    sections = ""

    def __init__(self, webpage, webpagedef_dir):
        self.id = webpage["id"]
        self.orig_id = webpage["origId"]
        self.page_def_id = webpage["pageDefId"]
        self.is_base_version = webpage["isBasedVersion"]
        self.is_login_only = webpage["isLoginOnly"]
        self.name = webpage.PageName.cdata
        if hasattr(webpage, "PageSections"):
            self.sections = webpage.PageSections.PageSection
        dirname = my_tools.mysplit(self.name, 50)
        self.page_dir = "{}/{}".format(webpagedef_dir, dirname)

    def to_file(self):
        if not os.path.exists(self.page_dir.encode('utf-8')):
            os.makedirs(self.page_dir.encode('utf-8'))
        # fichier de propriétés
        if not os.path.exists(self.page_dir.encode('utf-8')):
            os.makedirs(self.page_dir.encode('utf-8'))
        file = open("{}/PROPERTIES.md".format(self.page_dir), 'w+', encoding='utf-8')
        with file:
            # nom de l'objet
            file.write("# {}\n".format(self.name))
            file.write("- id : {}\n".format(self.id))
            file.write("- origId : {}\n".format(self.orig_id))
            file.write("- pageDefId : {}\n".format(self.page_def_id))
            file.write("- isBasedVersion : {}\n".format(self.is_base_version))
            file.write("- isLoginOnly : {}\n".format(self.is_login_only))

        if self.sections:
            for section in self.sections:
                new_section = Section(section, self.page_dir)
                new_section.to_file()
