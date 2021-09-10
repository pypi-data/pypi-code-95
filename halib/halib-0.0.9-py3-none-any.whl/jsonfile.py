import json


def read(file):
    with open(file) as f:
        data = json.load(f)
        return data


def write(data_dict, outfile):
    with open(outfile, 'w') as json_file:
        json.dump(data_dict, json_file)
