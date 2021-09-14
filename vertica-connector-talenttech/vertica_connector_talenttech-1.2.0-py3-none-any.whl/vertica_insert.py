import json


def myconverter(o):
    return o.__str__()


def write_list_as_json_str(fields_json, rows):
    if fields_json is not None:
        for r in rows:
            for field_json in fields_json:
                if r[field_json] is not None:
                    try:
                        r[field_json] = json.loads(r[field_json])
                    except TypeError:
                        continue
    return "\n".join([json.dumps(dict(r), default=myconverter) or "{}" for r in rows])


def insert(
    vertica_cnx, target, fields, fields_json, data, enforcelength="ABORT ON ERROR"
):
    if enforcelength is not None:
        enforcelength = "ENFORCELENGTH " + enforcelength
    else:
        enforcelength = ""
    copy_statement = (
        u"COPY {0} ({1}) FROM STDIN PARSER FJSONPARSER( "
        u" RECORD_TERMINATOR=E'\n', flatten_maps=false) {2}"
    ).format(target, ",".join(['"' + v + '"' for v in fields]), enforcelength)
    data_str = write_list_as_json_str(fields_json, data)
    cursor = vertica_cnx.cursor()
    cursor.copy(copy_statement, data_str)
    cursor.close()
