def find_in_json(data, obj_id):
    try:
        return data[obj_id]
    except KeyError:
        return ""


def find_id_json(data, obj_id):
    try:
        return data[obj_id]
    except KeyError:
        return ""
