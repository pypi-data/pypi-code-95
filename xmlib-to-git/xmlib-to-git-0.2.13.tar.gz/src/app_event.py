# -*- coding: utf-8 -*-
import binascii
import os, re
import base64
from src.utils import my_tools


class Event(object):
    """
    Define an event
    """
    script = ""

    def __init__(self, event, dir):
        self.id = event["id"]
        self.orig_id = event["origId"]
        self.order = event["orderNo"]
        self.obj_def = event["objDef"]
        self.config_id = event["configId"]
        self.name = event["name"]
        self.on_what = event["onWhat"] # sur quel origId d'un objet
        self.relative_to_id = event["relativeToId"]
        self.delay = event["delay"]
        self.template_id = event["templateId"]
        self.change_field_id = event["changeFieldId"]
        self.id_deployed = event["isDeployed"]
        dirname = my_tools.mysplit(self.name)
        self.event_dir = "{}/{}".format(dir, dirname)
        self.properties = event.__dict__
        if hasattr(event, "ConditionB64"):
            self.script = event.ConditionB64.cdata
        if hasattr(event, "Props"):
            self.props = event.Props.__dict__

    def to_file(self):
        # properties file
        if not os.path.exists(self.event_dir.encode('utf-8')):
            os.makedirs(self.event_dir.encode('utf-8'))
        file = open("{}/PROPERTIES.md".format(self.event_dir), 'w+', encoding='utf-8')
        with file:
            # nom de l'objet
            file.write("# {}\n".format(self.name))
            # Informations
            file.write("\n\n## Informations\n")
            file.write("- id : {}\n".format(self.id))
            file.write("- origId : {}\n".format(self.orig_id))
            file.write("- objDef : {}\n".format(self.obj_def))
            file.write("- configId : {}\n".format(self.id))
            file.write("- onWhat : {}\n".format(self.orig_id)) # TODO : trouver le nom dans un dict
            file.write("- relativeTo : {}\n".format(self.relative_to_id)) # TODO: idem
            file.write("- delay : {}\n".format(self.delay))
            file.write("- templateId : {}\n".format(self.template_id)) # TODO: idem
            file.write("- changeField : {}\n".format(self.change_field_id)) # TODO: idem


            # Properties
            file.write("\n\n## Properties\n")
            for el in self.properties["children"]:
                if(el.__dict__["_name"] != "ConditionB64") and (el.__dict__["_name"] != "Props"):
                    file.write("- {} : {}\n".format(el.__dict__["_name"], el.__dict__["cdata"]))

            if self.props:
                for el in self.props["children"]:
                    if el.__dict__["_name"] == "template":
                        self.template( el.__dict__["cdata"])
                    else:
                        file.write("- {} : {}\n".format(el.__dict__["_name"], el.__dict__["cdata"]))

        if self.script:
            file = open("{}/script.js".format(self.event_dir), 'w+', encoding='utf-8')
            with file:
                file_content = base64.b64decode(self.script).decode("UTF-8", "ignore")
                file.write(file_content)

    def template(self, text):
        template = open("{}/template.js".format(self.event_dir), 'w+', encoding='utf-8')
        with template:
            try:
                template_content = base64.b64decode(text).decode("UTF-8", "ignore")
                template.write(template_content)
            except binascii.Error:
                template.write(text)
            except ValueError:
                template.write(text)

