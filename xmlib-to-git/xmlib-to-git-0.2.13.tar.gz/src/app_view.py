# -*- coding: utf-8 -*-

import os, re
from src.utils import my_tools


class View(object):
    """

    """

    properties = ""

    def __init__(self, view, path):
        self.id = view["id"]
        self.orig_id = view["origId"]
        self.order = view["orderNo"]
        self.def_id = view["objDefId"]
        self.is_system = view["isSystem"]
        self.name = view.ViewName.cdata
        self.properties = view.Props.__dict__
        self.columns = view.Columns.cdata.replace("\n","")
        dirname = my_tools.mysplit(self.name)
        self.view_dir = "{}/{}".format(path, dirname)

    def to_file(self):
        # fichier de propriétés
        if not os.path.exists(self.view_dir.encode('utf-8')):
            os.makedirs(self.view_dir.encode('utf-8'))
        file = open("{}/PROPERTIES.md".format(self.view_dir), 'w+', encoding='utf-8')
        with file:
            # nom de l'objet
            file.write("# {}\n".format(self.name))
            # Informations
            file.write("\n\n## Informations\n")
            file.write("- id : {}\n".format(self.id))
            file.write("- origId : {}\n".format(self.orig_id))
            file.write("- orderNo : {}\n".format(self.orig_id))
            file.write("- objDefName : {}\n".format(self.def_id))
            file.write("- isSystem : {}\n".format(self.is_system))

            # Propriétés
            if self.properties:
                file.write("\n\n## Properties\n")
                for el in self.properties["children"]:
                    file.write("- {} : {}\n".format(el.__dict__["_name"], el.__dict__["cdata"]))

            #Colonnes
            file.write("\n\n## Columns\n")
            for col in self.columns.split(","):
                if col and col != " ":
                    file.write("- {}\n".format(col))


