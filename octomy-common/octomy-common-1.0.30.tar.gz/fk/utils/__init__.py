from dateutil.relativedelta import relativedelta
from urllib.parse import urlparse
import hashlib
import os
import json
import mmap
import base64
import random
import datetime
import time
import requests
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

_requests_session_instance = None


def redact(val, minimum=20):
    total = len(val)
    scramble_n = max(minimum, total - 3)
    show_n = max(min(total - minimum, 3), 0)
    out = val[0:show_n] + "*" * (scramble_n)
    return out


def file_contains_str(filename, str):
    return file_contains_bytes(filename, str.encode("utf-8"))


def file_contains_bytes(filename, bytes):
    # mmap does not work for empty files
    if os.stat(filename).st_size == 0:
        return False
    with open(filename, "rb", 0) as file, mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s:
        if s.find(bytes) != -1:
            return True
    return False


# Merge two dictionaries
def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res


# Determine if given URL is valid
def is_url_valid(url):
    try:
        result = urlparse(url)
        # 		if not result.scheme:
        # 			print ("No scheme")
        # 		if not result.netloc:
        # 			print ("No netloc")
        # 		if not result.path:
        # 			print ("No path")
        # 		if not result.scheme in ['http', 'https']:
        # 			print ("Scheme invalid")

        return all([result.scheme, result.netloc]) and result.scheme in ["http", "https"]
        # result.netloc,
    except:
        return False


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test


# Create a hash hex digest from string
def hashstr(str):
    sha256 = hashlib.sha256()
    sha256.update(str.encode("utf-8"))
    return sha256.hexdigest().upper()


def hashfile(fn):
    file = open(fn, "r+")
    size = os.path.getsize(fn)
    sha256 = hashlib.sha256()
    sha256.update(mmap.mmap(file.fileno(), size))
    return sha256.update(mmap.mmap(file.fileno(), size))


# Turn invalid string into naive URL by prepending schema and appending path
def decorate_url(url):
    if not is_url_valid(url):
        url = "http://{url}/".format(url=url)
    return url


# Return dict with url split into components as appropriate for storing in database
def split_url(url_full):
    ret = {"url_hostname": "", "url_schema": "", "url_path": "", "url_query": "", "url_fragment": ""}
    try:
        parts = urlparse(url_full)
        if parts.netloc is not None:
            ret["url_hostname"] = parts.netloc
        if parts.scheme is not None:
            ret["url_schema"] = parts.scheme
        if parts.path is not None:
            ret["url_path"] = parts.path
        if parts.query is not None:
            ret["url_query"] = parts.query
        if parts.port is not None:
            ret["url_port"] = parts.port
        if parts.fragment is not None:
            ret["url_fragment"] = parts.fragment
    except Exception as e:
        # print(f"ERROR SPLITTING URL: {e}")
        pass
    return ret


def flatten_headers(headers):
    out = ""
    for k, v in headers.items():
        out += f"'{k}'='{v}'\n"
    return out


def verify_input_files(input_options):
    input_files = []
    notes = []
    if input_options:
        for file in input_options:
            note = "[OK]"
            if not os.path.exists(file):
                note = "[MISSING, Skipped]"
            elif not os.path.isfile(file):
                note = "[NOT A FILE, Skipped]"
            elif os.access(file, os.R_OK):
                note = "[NOT READABLE, Skipped]"
            else:
                input_files.append(file)
            notes.append(f' "{file}"   {note}')
        return input_files, notes
    else:
        return None, None


def verify_output_file(output_file):
    valid_output_file = None
    if output_file:
        output_path = os.path.dirname(os.path.realpath(output_file))
        os.makedirs(output_path, exist_ok=True)
        note = "[OK]"
        if not os.path.exists(output_path):
            note = "[PATH MISSING]"
        elif os.access(output_file, os.W_OK):
            note = "[NOT WRITABLE]"
        else:
            valid_output_file = output_file
    return valid_output_file, note


# Look at result from scrape and produce a dictionary with relevant data or error output
def get_data_for_scrape_result(result):
    http_status_code = result.get("http_status_code", 500)
    reason = result.get("reason", "")
    print(f"SCRAPING COMPLETED {http_status_code}, {reason}")

    data = None
    error = ""
    ok = True
    if http_status_code != 200:
        error = f"http code {http_status_code} with reason {reason}"
        ok = False
    else:
        headers = result.get("headers", "")
        page_source = result.get("page_source", "")
        if not page_source:
            error = "no page_source"
            ok = False
        else:
            data = None
            try:
                data = json.loads(page_source)
            except Exception as e:
                error = f"json parse failed for {page_source[:100]} with {e}"
                ok = False
            if ok:
                t = __builtins__.type(data)
                if not data:
                    error = f"json parse returned no data"
                    ok = False
                # elif t is not '<class \'dict\'>':
                # 	error=f"json parse returned not dict ({t})"
                # 	ok=False
    return data, ok, error


attrs = ["millenia", "centuries", "decades", "years", "months", "days", "hours", "minutes", "seconds"]

human_readable = lambda delta: ["%d %s" % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1]) for attr in attrs if getattr(delta, attr)]


def human_delta(td_object: datetime.timedelta, max: int = 0):
    ms = int(td_object.total_seconds() * 1000)
    if ms == 0:
        return "0 ms"
    sign = ""
    if ms < 0:
        ms = -ms
        sign = "-"
    # fmt: off
    periods = [
        ("year",  1000 * 60 * 60 * 24 * 365),
        ("month", 1000 * 60 * 60 * 24 * 30),
        ("day",   1000 * 60 * 60 * 24),
        ("hr",    1000 * 60 * 60),
        ("min",   1000 * 60),
        ("sec",   1000),
        ("ms", 1)
    ]
    # fmt: on

    strings = []
    ct: int = 0
    for period_name, period_ms in periods:
        if ms > period_ms:
            period_value, ms = divmod(ms, period_ms)
            # has_s = "s" if period_value > 1 else ""
            # strings.append("%s %s%s" % (period_value, period_name, has_s))
            strings.append(f"{period_value} {period_name}")
            ct += 1
            if max > 0 and ct > max:
                break
    return sign + ", ".join(strings)  # + f"({td_object}, {ms})"


def human_bytesize(bytes: int, max: int = 0):
    if bytes == 0:
        return "0 bytes"
    if bytes < 0:
        return "negative bytes (error)"
    # fmt: off
    KiB=1024
    periods = [
        ("PiB", KiB*KiB*KiB*KiB*KiB),
        ("TiB", KiB*KiB*KiB*KiB),
        ("GiB", KiB*KiB*KiB),
        ("MiB", KiB*KiB),
        ("KiB", KiB),
        ("bytes", 1)
    ]
    # fmt: on

    strings = []
    ct: int = 0
    for period_name, period_bytes in periods:
        if bytes > period_bytes:
            period_value, bytes = divmod(bytes, period_bytes)
            # has_s = "s" if period_value > 1 else ""
            # strings.append("%s %s%s" % (period_value, period_name, has_s))
            strings.append(f"{period_value} {period_name}")
            ct += 1
            if max > 0 and ct > max:
                break
    return ", ".join(strings)  # + f"({td_object}, {bytes})"


# Make washee conform strictly to structure of washer
def wash_dict(washee, washer):
    out = {}
    for k, v in washer.items():
        if k in washee:
            if isinstance(v, dict):
                if isinstance(washee[k], dict):
                    out[k] = wash_dict(washee[k], v)
            else:
                if not isinstance(washee[k], dict):
                    out[k] = washee[k]
    return out


def random_str(l):
    return base64.b64encode(os.urandom(l))


def print_process_info():
    if hasattr(os, "getppid"):
        print(f"Parent process:{os.getppid()}")
    print(f"Process id:{os.getpid()}")


def sleep(time_sec):
    time.sleep(time_sec)
    # await asyncio.sleep async


def read_file(fname, strip=True):
    fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    data = ""
    if os.path.exists(fn):
        with open(fn, encoding="utf-8") as f:
            data = f.read()
            data = data.strip() if strip else data
            # logger.info(f"Got data '{data}' from '{fn}'")
    else:
        logger.error(f"Could not find file {fn} relative to working directory {os.getcwd()}")
    return data


def write_file(fn, data, strip=True):
    with open(fn, "w") as f:
        f.write(data.strip() if strip else data)


def debug_imports():
    import logging
    import pprint
    import sys
    import os

    l = logging.getLogger(__name__)
    l.error(f"PATH: {sys.path}")
    l.error(f"PREFIX: {sys.prefix}")
    l.error(f"ENV: {pprint.pformat(os.environ)}")

    import pkg_resources

    installed_packages = {d.project_name: d.version for d in pkg_resources.working_set}
    l.error(f"MODULES:{pprint.pformat(installed_packages)}")

    import pkgutil

    for m in pkgutil.iter_modules(path=None):
        l.error(f"MODULE: {m.name}")

    def explore_package(module_name):
        loader = pkgutil.get_loader(module_name)
        if not loader:
            l.error(f"No loader for {module_name}")
        elif not loader.filename:
            l.error(f"No filename for {module_name}")
        else:
            for sub_module in pkgutil.walk_packages([loader.filename]):
                _, sub_module_name, _ = sub_module
                qname = module_name + "." + sub_module_name
                l.error(qname)
                explore_package(qname)

    explore_package("fk")
    explore_package("batch")

    import time

    time.sleep(die_sec)
    sys.exit(6)





def requests_session():
    global _requests_session_instance
    if not _requests_session_instance:
        _requests_session_instance = requests.Session()
        # fmt:off
        headers = {
              "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.85 Safari/537.36"
            , "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
            , "Cache-Control": "no-cache"
            , "Pragma": "no-cache"
        }
        # fmt:on
        _requests_session_instance.headers.update(headers)
    return _requests_session_instance
