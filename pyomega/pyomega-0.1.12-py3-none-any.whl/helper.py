import os
import json
import copy
from datetime import datetime


def deserialize_json(method, _json):
    try:
        return json.loads(_json)
    except Exception as e:
        get_error(method, e)


def decode_json(method, js):
    try:
        return js.decode("utf-8")
    except Exception as e:
        get_error(method, e)


def get_error(method, *args, **kwargs):
    error_string = ""

    if "statusCode" in kwargs:
        if "URL" in kwargs:
            error_string += "\nURL: {}".format(kwargs["URL"])

        if "payload" in kwargs:
            error_string += "\nPayload: {}".format(kwargs["payload"])

        error_string += "\nstatusCode: {}".format(kwargs["statusCode"])
        error_string += "\nBody: {}".format(kwargs["body"])

    else:
        for i in args:
            error_string += "\n{}".format(i)

    raise SystemExit("{} ERROR:\n{}".format(method.upper(), error_string))


def get_response(code, body):
    if type(body) in [dict, list]:
        return {
            "statusCode": code,
            "body": json.dumps(body),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": code,
            "body": body
        }


def get_debug_msg(*args):
    msg = "*** debug ***\n"
    for i in args:
        msg += str(i) + ", "
    msg = msg[:-2]
    msg += "\n*************"
    print(font_formatter("italic", (font_formatter("white", msg))))


def font_formatter(n, s):
    # https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python/50025330

    code = {
        "green": 92,
        "red": 91,
        "italic": 3,
        "white": 37,
        "blue": 34
    }
    value = "\033[" + str(code[n]) + "m" + s + "\033[0m"
    return value


def get_config():
    with open(os.path.dirname(__file__) + "/../config.json", "r") as read_file:
        config = json.load(read_file)
        config = copy.deepcopy(config)
        read_file.close()
    return config


def get_stage():
    if "ENV" in os.environ:
        stage = os.environ["ENV"]
    else:
        stage = "local"
    return stage


def get_now_str(config):
    time_format = config["time_format"]
    now = datetime.strftime(datetime.now(), time_format)

    return now


def in_list(a, b):
    for item in a:
        if item in b:
            pass
        else:
            return False
    return True


def validate_not_nullable(required, payload):
    for i in required:
        if i in payload:
            if not payload[i]:
                return False
    return True


def in_required_list(required, payload):
    for item in required:
        if item in payload and payload[item]:
            continue
        else:
            return {
                "error": item
            }
    return {}


def in_allowed_list(allowed, payload):
    for item in payload:
        if item not in allowed:
            return {
                "error": item
            }
    return {}


def if_empty(object):
    for key, value in object.items():
        if value == "" or value == [] or value == {}:
            return True
    return False


def validate_str_input(payload):
    for key, value in payload.items():
        if not value:
            return False
        else:
            if type(value) is not str:
                return False
    return True


def object_mapper(object, result):
    mapped_object = {}
    x = 0
    for key in object:
        if key not in ["created_at", "updated_at"]:
            mapped_object[key] = result[x]
            x += 1

    return mapped_object


def is_json(object):
    try:
        json_object = json.loads(object)
        for x, y in json_object.items():
            pass
    except:
        return False
    return True


def is_list_of_jsons(payload):
    try:
        for item in payload:
            if is_json(json.dumps(item)) is True:
                continue
            else:
                return False
        return True
    except:
        return False


def make_instert_string(object, table):  ## TO BE DELETED

    fileds = ""
    values = ""

    for name, value in object.items():
        if type(value) == str:
            value = value.replace("'", "''")
        fileds = fileds + name + ", "

        if type(value) is dict:
            if value == {} or value == "":
                values = values + "'{}', "

            else:
                string = json.dumps(value)
                string = string.replace("'", "''")
                value = json.loads(string)
                values = values + "'" + json.dumps(value) + "', "

        elif type(value) is list:

            if value == [] or type(value[0]) == str:
                value = json.dumps(value).replace('"', "'")
                values = values + " ARRAY" + value + "::text[], "
            else:
                pass

        elif type(value) is bool:

            values = values + str(value) + ", "

        else:
            values = values + "'" + value + "', "

    insert_string = (
            "INSERT INTO " + table + " (" + (fileds[:-2])
            + ") VALUES (" + values[:-2] + ")")

    insert_string = insert_string.replace("'", "\'")

    print("INSERT STRING: " + insert_string)

    return insert_string


def make_insert_string_v2(object, table_name, on_conflict):
    fields = ""
    values = ""

    for name, value in object.items():

        fields += name + ", "

        if type(value) is str:
            value = value.replace("'", "''")
            values += "'" + value + "', "

        elif type(value) is dict:

            if value == {} or value == "":
                values += "'{}', "

            else:
                string = json.dumps(value)
                string = string.replace("'", "''")
                value = json.loads(string)
                values += "'" + json.dumps(value) + "', "

        elif type(value) is list:

            if value == [] or type(value[0]) is str:
                value = json.dumps(value).replace('"', "'")
                values += " ARRAY" + value + "::text[], "
            else:
                pass

        elif type(value) is bool:

            values += str(value) + ", "

        elif value is None:

            values += "NULL, "

        else:
            values = values + "'" + value + "', "

    insert_string = "INSERT INTO " + table_name
    insert_string += " (" + (fields[:-2]) + ")"
    insert_string += " VALUES (" + values[:-2] + ")"
    insert_string += " ON CONFLICT (" + on_conflict + ")"
    insert_string += " DO NOTHING"

    insert_string = insert_string.replace("'", "\'")

    print("INSERT STRING: " + insert_string)

    return insert_string


def make_update_string(object, table, key, key_value):
    string = ""

    for name, value in object.items():
        if name != key:
            if type(value) == str:
                value = value.replace("'", "''")

            if type(value) == dict:
                if value == {} or value == "":
                    string = string + name + " = '{}', "
                else:
                    string = string + name + " = '" + json.dumps(value) + "', "

            elif type(value) is list:

                if is_list_of_jsons(value) is True and value != []:
                    value = json.dumps(value).replace("[", "{'").replace("]", "'}")
                    string = string + " " + value + ", "

                else:
                    value = json.dumps(value).replace("[", "{").replace("]", "}")
                    string = string + name + " = '" + value + "', "

            else:
                string = string + name + " = '" + value + "', "

    update_string = (
            "UPDATE " + table + " SET " + string[:-2]
            + " WHERE " + key + " = '" + key_value + "'"
    )

    update_string = update_string.replace("'", "\'")
    print("UPDATE STRING: " + update_string)

    return update_string


def make_update_string_v2(payload, table, key, key_value):
    string = ""

    for name, value in payload.items():
        if name != key:
            if type(value) == str:
                value = value.replace("'", "''")

            if type(value) == dict:
                if not value:
                    string = string + name + " = '{}', "
                else:
                    string = string + name + " = '" + json.dumps(value) + "', "

            elif type(value) is list:
                value = [item.replace("'", "''") for item in value]

                if is_list_of_jsons(value) is True and value != []:
                    value = json.dumps(value).replace("[", "{'").replace("]", "'}")
                    string = string + " " + value + ", "

                else:
                    value = json.dumps(value).replace("[", "{").replace("]", "}")
                    string = string + name + " = '" + value + "', "

            elif type(value) is bool:
                string += name + " = " + str(value) + ", "

            elif value is None:
                string = string + name + " =  NULL, "

            else:
                string = string + name + " = '" + value + "', "

    update_string = (
            "UPDATE " + table + " SET " + string[:-2]
            + " WHERE " + key + " = '" + key_value + "'"
    )

    update_string = update_string.replace("'", "\'")
    print("UPDATE STRING: " + update_string)

    return update_string


def make_insert_string_v3(payload: dict, table: str):

    _keys = "{}".format("".join("{}, ".format(e) for e in list(payload.keys())))[:-2]
    _values = ""

    _val = []
    for _v in payload.values():

        if isinstance(_v, str):
            _val.append(_v.replace("'", "''"))

        elif isinstance(_v, int):
            _val.append(_v)

        elif isinstance(_v, dict):

            if not _v:
                _val.append("'{}'")

            else:
                _v = json.dumps(_v)
                _v = _v.replace("'", "''")
                _val.append(json.dumps(_v).replace('"{', "{").replace('}"', "}").replace("\\", ""))

        elif isinstance(_v, list):
            if not _v:
                _val.append("{}")
            else:
                _val.append(str(_v).replace("'", '"').replace("[", "{").replace("]", "}"))

        elif isinstance(_v, bool):
            _val.append("{}".format(_v))

        elif not _v:
            _val.append("NULL")

        else:
            raise ValueError("Unsupported value type: '{}'".format(type(_v)))

    _values = "{}".format("".join("'{}', ".format(e) for e in list(_val)))[:-2].replace("'NULL'", "NULL")

    _query = "INSERT INTO {table} ({keys}) VALUES ({values}) ON CONFLICT (campaign_id) DO NOTHING".format(
        table=table,
        keys=_keys,
        values=_values)

    return _query