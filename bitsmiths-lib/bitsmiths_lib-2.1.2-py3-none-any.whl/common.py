# **************************************************************************** #
#                           This file is part of:                              #
#                                BITSMITHS                                     #
#                           https://bitsmiths.co.za                            #
# **************************************************************************** #
#  Copyright (C) 2015 - 2021 Bitsmiths (Pty) Ltd.  All rights reserved.        #
#   * https://bitbucket.org/bitsmiths_za/bitsmiths                             #
#                                                                              #
#  Permission is hereby granted, free of charge, to any person obtaining a     #
#  copy of this software and associated documentation files (the "Software"),  #
#  to deal in the Software without restriction, including without limitation   #
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
#  and/or sell copies of the Software, and to permit persons to whom the       #
#  Software is furnished to do so, subject to the following conditions:        #
#                                                                              #
#  The above copyright notice and this permission notice shall be included in  #
#  all copies or substantial portions of the Software.                         #
#                                                                              #
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL     #
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  #
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
#  DEALINGS IN THE SOFTWARE.                                                   #
# **************************************************************************** #

import os.path
import hashlib
import re
import logging

from . import Pod, PodAsync


RE_EMAIL_MATCH = re.compile(r'[^@]+@[^@]+\.[^@]+')
RE_SMS_MATCH   = re.compile(r'(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+')


def hash_password(email: str, passwd: str):
    """
    One way hash the email and password.

    :param email: Client's email address.
    :param passwd: Unhashed pasword.
    :return: The hashed password
    """
    hm = hashlib.md5()
    ps = '%s%s' % (passwd, email)
    hm.update(bytes(ps, 'utf8'))

    return hm.hexdigest()


def human_size(size_bytes: int):
    """
    Format a size in bytes into a 'human' file size, e.g. bytes, KB, MB, GB, TB, PB
    Note that bytes/KB will be reported in whole numbers but MB and above will have greater precision
    e.g. 1 byte, 43 bytes, 443 KB, 4.3 MB, 4.43 GB, etc

    :param size_bytes: The size in bytes.
    :return: The friendly human readable version.
    """
    if size_bytes == 1:
        return "1 byte"

    suffixes_table = [('bytes', 0), ('KB', 0), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2)]

    num = float(size_bytes)

    for suffix, precision in suffixes_table:
        if num < 1024.0:
            break
        num /= 1024.0

    if precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=precision))

    return "%s %s" % (formatted_size, suffix)


def dest_addr_valid_email(addr: str):
    """
    Validates that the email address is valid.

    :param addr: The email address to validate.
    :return: True if valid else false.
    """
    if str != type(addr):
        return False

    if len(addr) <= 3:
        return False

    if not RE_EMAIL_MATCH.match(addr):
        return False

    return True


def dest_addr_valid_sms(addr: str, minLength: int = 9):
    """
    Validates that the sms number is valid.

    :param addr: The sms number to validate.
    :param minLength: The min length for the sms number
    :return: True if valid else false.
    """
    if str != type(addr):
        return False

    if len(addr) < 9:
        return False

    if not RE_SMS_MATCH.match(addr):
        return False

    return True


def read_dict(dic: dict,
              key: str,
              ttype: type = None,
              parent: str = '',
              req_vals: list = None,
              optional: bool = False) -> object:
    """
    Reads from the dictionary.

    :param dic: The dictionary to validate.
    :param key: The key to check exists.
    :param ttype: The type the key has to be, if None this is ignored.
    :param parent: Optional the parent of the dicionary to help with error logging.
    :param req_vals: An option list of values, if not None, the key value has to be one of these values.
    :param optional: If True, the value does not have to exist, None is returned in this case.
    :return: The value of 'key'.
    """
    if dic is None or type(dic) != dict:
        raise Exception('Dictionary input not a dictionary, parent [%s%s]' % (parent, key))

    if ttype   is None:
        if key not in dic:
            if not optional:
                raise Exception('Dictionary invalid, key [%s%s] not found' % (parent, key))

            return None

        return dic[key]

    val = dic.get(key)

    if val is None:
        if optional:
            return val

        raise Exception('Dictionary invalid, key [%s%s] not found' % (parent, key))

    if ttype is not None and type(val) != ttype :
        try:
            val      = ttype(val)
            dic[key] = val
        except Exception:
            raise Exception('Dictionary invalid, key [%s%s] value [%s] is the incorrect type.  Expected [%s] and got [%s]' % (
                parent, key, val, str(ttype ) , str(type(val))))

    if req_vals is not None and val not in req_vals:
        raise Exception('Dictionary invalid, key [%s%s] value [%s] not valid.  Value must be one of: %s' % (
            parent, key, val, str(req_vals)))

    return val


def get_logger(opts: object = None) -> logging.Logger:
    """
    Trys to get the best possible logger.

    :param opts: (str/list/Logger) either string (logger name) or list of strings to get a logger for.
    :return: The logger object.
    """
    if not opts:
        return logging.getLogger()

    logger = None

    if type(opts) == str:
        logger = logging.getLogger(opts)
    elif type(opts) == list:
        for x in opts:
            if type(x) != str:
                continue

            if x in logging.Logger.manager.loggerDict:
                logger = logging.getLogger(x)

                if logger:
                    return logger

    elif isinstance(opts, logging.Logger):
        logger = opts

    if logger:
        return logger

    return logging.getLogger()


def xml_2_dict(xmlStr: str, strip_namespaces: bool = False) -> dict:
    """
    Traverse the given XML element tree to convert it into a dictionary.

    :param xmlStr: The xml to read.
    :param strip_name_spaces: If true, strips the namespaces from the elements if there are any.
    :return: The result
    """
    import xml.etree.ElementTree

    element_tree = xml.etree.ElementTree.fromstring(xmlStr)

    def internal_iter(tree, accum: dict, getTag) -> dict:
        """
        Recursively iterate through the elements of the tree accumulating
        a dictionary result.

        :param tree: (xml.etree.ElementTree) Tree to read from
        :param accum: Dictionary into which data is accumulated
        :pram  getTag: (function) Function to get the tag name.
        :return: The accum.
        """
        if tree is None:
            return accum

        if tree.getchildren():
            tree_tag = getTag(tree.tag)
            accum[tree_tag] = {}
            for each in tree.getchildren():
                result   = internal_iter(each, {}, getTag)
                each_tag = getTag(each.tag)
                if each_tag in accum[tree_tag]:
                    if not isinstance(accum[tree_tag][each_tag], list):
                        accum[tree_tag][each_tag] = [
                            accum[tree_tag][each_tag]
                        ]
                    accum[tree_tag][each_tag].append(result[each_tag])
                else:
                    accum[tree_tag].update(result)
        else:
            accum[getTag(tree.tag)] = tree.text

        return accum

    def tag_ns(tag):
        return tag

    def tag_no_ns(tag):
        pos = tag.find('}')

        if pos > 0:
            return tag[pos + 1:]

        return tag

    x = internal_iter(element_tree, {}, tag_no_ns if strip_namespaces else tag_ns)

    if len(x) == 1:
        for key, item in x.items():
            return item

    return x


def plain_text_2_dict(plaint_txt: str) -> dict:
    """
    Converts plain text to python dictionary using x.z=y format.

    :param plaint_txt: The plain text to read.
    :return: The result.
    """
    res = {}

    for line in plaint_txt.split('\n'):
        parts = line.strip().split('=')
        if len(parts) != 2:
            continue

        ns = parts[0].strip()

        if ns == '':
            continue

        ns  = ns.split('.')
        obj = res

        for n in ns[:-1]:
            if n == '':
                continue

            if not obj.get(n):
                obj[n] = {}

            obj = obj[n]

        obj[ns[-1]] = parts[1].strip()

    return res


def read_dict_from_str(str_type: str, data_str: str):
    """
    Converts a string in specific data format to a  python dictionary.

    :param str_type: The type data string: plaint text, json, yaml, xml.
    :param data_str: The data string in question.
    :return: The dictionary
    """
    if str_type.lower() == 'json':
        import json
        return json.loads(data_str)
    elif str_type.lower() in ['yml', 'yaml']:
        import yaml
        return yaml.safe_load(data_str)
    elif str_type.lower() == 'xml':
        return xml_2_dict(data_str)
    elif str_type.lower() in ['text', 'plain', 'plain text']:
        return plain_text_2_dict(data_str)
    else:
        raise Exception('Dictionary string type [%s] not expected.' % str_type)


def read_config_dict_from_file(config_file: str) -> dict:
    """
    Reads the specified config file into a dictionary

    :param config_file: The path to the config file.
    :return: The config as a dictionary.
    """
    if not os.path.exists(config_file):
        raise Exception('Config file [%s] not found.' % config_file)

    ext = os.path.splitext(config_file)[1].lower()

    if ext in ['.yml', '.yaml']:
        with open(config_file, 'rt') as fh:
            return read_dict_from_str('yml', fh.read())

    if ext in ['.json']:
        with open(config_file, 'rt') as fh:
            return read_dict_from_str('json', fh.read())

    if ext in ['.xml']:
        with open(config_file, 'rt') as fh:
            return read_dict_from_str('xml', fh.read())

    if ext in ['.txt', '.ini', '.text']:
        with open(config_file, 'rt') as fh:
            return read_dict_from_str('text', fh.read())

    raise Exception('Unexpected file type [%s] when reading config [%s].' % (ext, config_file))


def md5_checksum(file_path: str) -> str:
    """
    Gets the md5 checksum for a file.

    :param file_path: The file to do the md5 checksum on.
    :return: The md5 checksum.
    """
    with open(file_path, 'rb') as fh:
        m = hashlib.md5()

        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)

        return m.hexdigest()


def sql_run(pod, sql: str):
    """
    Run a custom sql command.

    :param pod: The pod to use.
    :param sql: The sql to run.
    """
    stmnt = None

    try:
        dbcon = pod.dbcon
        stmnt = dbcon.statement('sql_run', 2)
        stmnt.sql(sql)
        dbcon.execute(stmnt)
    finally:
        del stmnt


def sql_fetch(pod: "Pod", sql: str, one: bool = False) -> "list|dict":
    """
    Run a custom sql command.  Returns the result

    :param pod: The pod to use.
    :param sql: The sql to run.
    :param one: If true only return the first row as a dictionary, else return list of dicts.
    :return: List or dictionary results. or a single dict, or None if nothing found
    """
    stmnt = None
    res   = None

    try:
        dbcon = pod.dbcon
        stmnt = dbcon.statement('sql_fetch', 1)
        stmnt.sql(sql)
        dbcon.execute(stmnt)

        while dbcon.fetch(stmnt):
            row = {}
            idx = 0

            for col in stmnt.columns:
                row[col] = stmnt.result[idx]
                idx      += 1

            if one:
                res = row
                break

            if not res:
                res = []

            res.append(row)

    finally:
        del stmnt

    return res


async def asql_run(apod: PodAsync, sql: str):
    """
    Run a custom sql command.

    :param pod: The async pod to use.
    :param sql: The sql to run.
    """
    stmnt = None

    try:
        dbcon = apod.dbcon
        stmnt = await dbcon.statement('asql_run', 2)
        stmnt.sql(sql)
        await dbcon.execute(stmnt)
    finally:
        del stmnt


async def asql_fetch(apod: PodAsync, sql: str, one: bool = False) -> "list|dict":
    """
    Run a custom sql command. Returns the result

    :param apod: The async pod to use.
    :param sql: The sql to run.
    :param one: If true only return the first row as a dictionary, else return list of dicts.
    :return: List or dictionary results. or a single dict, or None if nothing found
    """
    stmnt = None
    res   = None

    try:
        dbcon = apod.dbcon
        stmnt = await dbcon.statement('sqlFetch', 1)
        stmnt.sql(sql)
        await dbcon.execute(stmnt)

        while await dbcon.fetch(stmnt):
            row = {}
            idx = 0

            for col in stmnt.columns:
                row[col] = stmnt.result[idx]
                idx      += 1

            if one:
                res = row
                break

            if not res:
                res = []

            res.append(row)

    finally:
        del stmnt

    return res


def import_dyn_pluggin(mpath: str, module_only: bool = False, raise_errors: bool = False) -> tuple:
    """
    Import a dynamic module.

    :param mpath: Fully qaualified pluging path, eg: sysX.cust_generators.firebird.Firebird
    :param module_only: If this is true, then it donly imports the module, does not expect the last path object
                          to be a attribute.
    :param raise_errors: If true, raises exceptions instead of return them.
    :return: (type, exception), if failure returns (None, Exception) else (type, None).
    """
    import importlib

    try:
        if module_only:
            obj = importlib.import_module(mpath)
        else:
            mparts = mpath.split('.')

            if len(mparts) == 1:
                raise Exception('Module path not valid, no path seperation.')

            from_list = '.'.join(mparts[0:-1])

            mod = importlib.import_module(from_list)
            obj = getattr(mod, mparts[-1])

    except Exception as x:
        if raise_errors:
            raise

        return None, x

    return obj, None
