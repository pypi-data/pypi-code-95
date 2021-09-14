import json

from caeops.global_settings import PROJECT_ROOT

filename = PROJECT_ROOT + "/src/config.json"


# Data to be written
# TODO This is redundant remove this and replace its usages with requestlib.py
class Storage:
    def __init__(self):
        print("---------init---------")
        dictionary = {}

        # Serializing json
        json_object = json.dumps(dictionary)

        # Writing to sample.json
        # with open(filename, "w") as outfile:
        #     outfile.write(json_object)

    def read(self):
        with open(filename) as outfile:
            data = json.load(outfile)
            return data

    def write(self, data):
        with open(filename, "w") as outfile:
            json.dump(data, outfile)
