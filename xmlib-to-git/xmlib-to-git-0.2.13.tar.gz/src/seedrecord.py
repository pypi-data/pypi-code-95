import json
import os, re
from src.utils import my_json, my_tools
this_dir, this_filename = os.path.split(__file__)


class SeedRecord(object):
    """

    """

    def __init__(self, data_object, app_dir):
        self.id = data_object["id"]
        self.obj_def_id = data_object["objDefId"]
        self.fields = data_object.Field
        self.obj_name = ""

        # obj_dict
        json_dict = os.path.join(this_dir, "utils", "objects_dict.json")
        file_dict = json.load(open(json_dict))
        obj = my_json.find_id_json(file_dict, self.obj_def_id)
        try:
            if obj:
                self.obj_name = my_tools.mysplit(obj["name"])
        except Exception as err:
            print(err)

        self.seed_dir = self.portal_dir = "{}/seeds".format(app_dir)

        if not os.path.exists(self.portal_dir.encode('utf-8')):
            os.makedirs(self.portal_dir.encode('utf-8'))

    def to_file(self):
        if self.obj_name:
            file = open("{}/{}.md".format(self.portal_dir, self.obj_name), 'a+', encoding='utf-8')
            with file:
                file.write("\n* {} : \n".format(self.id))
                for field in self.fields:
                    file.write("\t* {} : {}\n".format(field["name"], field.cdata))
