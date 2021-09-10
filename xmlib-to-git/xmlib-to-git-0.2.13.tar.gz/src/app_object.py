# -*- coding: utf-8 -*-
import json
import os, re
from src.field import *
from src.app_view import View
from src.app_event import Event
from src.utils import my_json, my_tools
this_dir, this_filename = os.path.split(__file__)


class Object(object):

    """
    définition d'un object
    comporte liste de 'fields'
    """

    description = ""
    is_managed = ""
    def_process = ""
    audit_view = ""
    audit_create = ""
    audit_delete = ""
    audit_edit = ""
    enable_reports = ""
    show_tags = ""
    goog_synch = ""
    translations = ""
    relations = ""
    views = ""
    events = ""
    menus = ""
    is_localized = ""

    def __init__(self, data, app_directory):
        self.id = data["id"]
        self.orig_id = data["origId"]
        self.name = my_tools.mysplit(data.SingularName.cdata)
        self.def_name = data["objDefName"]
        self.is_system = data["isSystem"]
        self.is_auditable = data["isAuditable"]
        self.is_viewable = data["isViewable"]
        self.is_flagdable = data["isFlaggable"]
        self.is_dependent = data["isDependent"]
        self.is_deployed = data["isDeployed"]

        if hasattr(data, "Description"):
            self.description = data.Description.cdata
        if hasattr(data, "Props"):
            if hasattr(data.Props, "isManaged"):
                self.is_managed= data.Props.isManaged.cdata
            if hasattr(data.Props, "defProcess"):
                self.def_process = data.Props.defProcess.cdata
            if hasattr(data.Props, "auditView"):
                self.audit_view = data.Props.auditView.cdata
            if hasattr(data.Props, "auditCreate"):
                self.audit_create = data.Props.auditCreate.cdata
            if hasattr(data.Props, "auditDelete"):
                self.audit_delete= data.Props.auditDelete.cdata
            if hasattr(data.Props, "auditEdit"):
                self.audit_edit = data.Props.auditEdit.cdata
            if hasattr(data.Props, "enableReports"):
                self.enable_reports = data.Props.enableReports.cdata
            if hasattr(data.Props, "showTags"):
                self.show_tags = data.Props.showTags.cdata
            if hasattr(data.Props, "googSynch"):
                self.goog_synch = data.Props.googSynch.cdata
            if hasattr(data.Props, "isLocalized"):
                self.is_localized = data.Props.isLocalized.cdata
        if hasattr(data, "Translations"):
            if hasattr(data.Translations, "Translation"):
                self.translations = data.Translations.Translation
        if hasattr(data, "RelationshipDefs"):
            if hasattr(data.RelationshipDefs, "RelationshipDef"):
                self.relations = data.RelationshipDefs.RelationshipDef
        if hasattr(data, "ListViews"):
            self.views = data.ListViews.ListView
        if hasattr(data, "Events"):
            self.events = data.Events.Event

        self.fields = data.DataFieldDefs.DataFieldDef

        self.obj_directory = "{}/objects/{}".format(app_directory, self.def_name)

        # id -> origin id
        json_path = os.path.join(this_dir, "utils", "id_dict.json")
        file_id = json.load(open(json_path))
        obj = my_json.find_id_json(file_id, self.id)
        if not obj:
            file_id[self.id] = self.orig_id

        jsontest = json.dumps(file_id)
        with open(json_path, "w", encoding='utf-8') as f:
            f.write(jsontest)

        # obj_dict
        json_dict = os.path.join(this_dir, "utils", "objects_dict.json")
        file_dict = json.load(open(json_dict))
        obj = my_json.find_id_json(file_dict, self.id)
        if not obj:
            inner_data = {"origId": self.orig_id, "name": self.name, "defName": self.def_name}
            file_dict[self.id] = inner_data
            file_dict[self.orig_id] = inner_data

        jsontest = json.dumps(file_dict)
        with open(json_dict, "w", encoding='utf-8') as f:
            f.write(jsontest)

    def create(self):
        """
        Ecrit dans des fichiers les paramètres de l'obejt
        - PROPERTIES.md avec les infos techniques
        - RELATIONSHIP.md avec les relations
        - VIEWS.md avec les définitions des view
        - TRANSLATIONS.yml pour les traductions de l'objet
        - un dossier par champ dans le dossier fields
        - un dossier par déclencheur dans le dossier triggers
        :return:

        """
        if not os.path.exists(self.obj_directory.encode('utf-8')):
            os.makedirs(self.obj_directory.encode('utf-8'))

        self.do_properties_file()

        if self.relations:
            self.do_relationship_file()

        if self.views:
            self.do_views_file()

        if self.translations:
            self.do_translations_file()

        if self.events:
            self.create_events()

        self.create_fields()


    def do_properties_file(self):
        # fichier de propriétés
        with open("{}/PROPERTIES.md".format(self.obj_directory), 'w+', encoding='utf-8') as file:
            # nom de l'objet
            file.write("# {}\n".format(self.name))
            # Description
            if self.description:
                file.write("## Description\n")
                file.write(self.description)
            # Informations
            file.write("\n\n## Informations\n")
            file.write("- id : {}\n".format(self.id))
            file.write("- origId : {}\n".format(self.orig_id))
            file.write("- objDef : {}\n".format(self.def_name))
            # Déploiement
            file.write("\nInfos déploiement :\n")
            file.write("- [{}] isSystem \n".format("X" if self.is_system == "true" else " "))
            file.write(
                "- [{}] isAuditable\n".format("X" if self.is_auditable == "true" else " "))
            file.write("- [{}] isViewable\n".format("X" if self.is_viewable == "true" else " "))
            file.write("- [{}] isFlaggable\n".format("X" if self.is_flagdable == "true" else " "))
            file.write("- [{}] isDependent\n".format("X" if self.is_dependent == "true" else " "))
            file.write("- [{}] isDeployed\n".format("X" if self.is_deployed == "true" else " "))
            # Propriétés
            file.write("\nPropriétés :\n")
            if self.is_managed:
                file.write("- [{}] isManaged \n".format("X" if self.is_managed == "true" else " "))
            if self.def_process:
                file.write(
                    "- [{}] defProcess\n".format("X" if self.def_process == "1" else " "))
            if self.audit_view:
                file.write("- [{}] auditView\n".format("X" if self.audit_view == "true" else " "))
            if self.audit_create:
                file.write("- [{}] auditCreate\n".format("X" if self.audit_create == "true" else " "))
            if self.audit_delete:
                file.write("- [{}] auditDelete\n".format("X" if self.audit_delete == "true" else " "))
            if self.audit_edit:
                file.write("- [{}] auditEdit\n".format("X" if self.audit_edit == "true" else " "))
            if self.enable_reports:
                file.write("- [{}] enableReports\n".format("X" if self.enable_reports == "true" else " "))
            if self.show_tags:
                file.write("- [{}] showTags\n".format("X" if self.show_tags == "true" else " "))
            if self.goog_synch:
                file.write("- [{}] googSync\n".format("X" if self.goog_synch == "true" else " "))
            if self.is_localized:
                file.write("- [{}] isLocalized\n".format("X" if self.is_localized == "true" else " "))

    def do_relationship_file(self):
        # fichier des relations
        file = open("{}/RELATIONSHIP.md".format(self.obj_directory), 'w+', encoding='utf-8')
        with file:
            file.write("## Relations\n")
            sens_relation = "1 -- 1"
            for relation in self.relations:
                # 1 -- 1
                if relation["isMultiple"] == "false" and relation["isMultiple2"] == "false":
                    sens_relation = "1 -- 1"

                # 1 -- N
                if relation["isMultiple"] == "false" and relation["isMultiple2"] == "true":
                    sens_relation = "1 -- N"

                # N -- 1
                if relation["isMultiple"] == "true" and relation["isMultiple2"] == "false":
                    sens_relation = "N -- 1"

                # N -- N
                if relation["isMultiple"] == "true" and relation["isMultiple2"] == "true":
                    sens_relation = "1 -- 1"

                file.write("- {} : \n\t * [x] {}({}) `{}` {}({})\n".format(
                    relation["relName"],
                    relation["singularName1"],
                    relation["objDef1"],
                    sens_relation,
                    relation["singularName2"],
                    relation["objDef2"]
                ))

    def do_views_file(self):
        path = "{}/views".format(self.obj_directory)
        if not os.path.exists(path.encode('utf-8')):
            os.makedirs(path.encode('utf-8'))
        for view in self.views:
            new_view = View(view, path)
            new_view.to_file()

    def do_translations_file(self):
        file = open("{}/TRANSLATIONS.md".format(self.obj_directory), 'w+', encoding='utf-8')
        with file:
            file.write("## Traductions\n")
            file.write("|code|nom|text|\n")
            file.write("|---|---|---|\n")
            for trans in self.translations:
                file.write("|{}|{}|{}|\n".format(trans["langCode"], trans["fieldName"], trans["text"]))

    def create_events(self):
        # créer un dossier events + nouveaux events
        path = "{}/events".format(self.obj_directory)
        if not os.path.exists(path.encode('utf-8')):
            os.makedirs(path.encode('utf-8'))
        for event in self.events:
            new_event = Event(event, path)
            new_event.to_file()

    def create_fields(self):
        # créer un dossier fields + nouveaux fields
        path = "{}/fields".format(self.obj_directory)
        if not os.path.exists(path.encode('utf-8')):
            os.makedirs(path.encode('utf-8'))
        for field_data in self.fields:
            # FieldLong
            if "FieldLong" in field_data["dataClassName"]:
                field = LongField(field_data, path)
            # FieldLongArr
            elif "FieldLongArr" in field_data["dataClassName"]:
                field = LongArrField(field_data, path)
            else:
                field = BaseField(field_data, path)
            if field != "":
                field.to_file()
                field.set_properties()
                if field.validation_script:
                    field.create_validation_script()
