import base64
import itertools
import json
import logging
import os
import pathlib
import re
import sys
import threading
import time
import zlib
from copy import deepcopy
from glob import glob
from operator import itemgetter
from subprocess import Popen, PIPE

import arrow
import netifaces
import ntplib
import psutil
from arrow import Arrow
from iba_install.lib.ddenode import get_local_dde_node, get_dde_node, get_dde_app
from iba_install.lib.ddenode import get_local_node_id as _get_local_node_id
from infi.caching import cached_function
from infi.storagemodel.vendor.infinidat.shortcuts import get_infinidat_native_multipath_block_devices

from infiniguard_health.infiniguard_sysconfig import get_lab_mode_from_iguard_sysconfig

_logger = logging.getLogger(__name__)
threading_lock = threading.Lock()

HOST_COMMAND_TIMEOUT_SECONDS = 30
INFINIDAT_INSTALL_FOLDER = '/opt/infinidat'
IBOX_NODE_1_ADDRESS = '9.151.140.1'


class MgmtIPsException(Exception):
    pass


class BootVolumeResolvingException(Exception):
    pass


class HostCommandException(Exception):
    pass


class UtilityNotFound(Exception):
    pass


def dict_data_extractor(data, path):
    """ Returns the value instructed by the path.
        :param path: The path for traversing the dict, unix-like (/path/key).
        :type path: string

        :param data: Dictionary holding data.
        :type data: dict

        :return: data dependent
        """
    paths = (int(p) if p.isdigit() else p for p in path.split('/') if p)
    for p in paths:
        try:
            data = data[p]
        except TypeError:
            raise KeyError("Wrong path: {}, the key {} is invalid!".format(path, p))
    return data


def fill_list_lens_in_path(data, path_template):
    """ Checks for '[]' in path (which stands for list) and replaces it with
        the size of the list (nested object in dict) for full path identification of keys.
        :param path_template: The path for traversing the dict, unix-like (/path/key).
        :type path_template: string

        :param data: Dictionary holding data.
        :type data: dict

        :return: string
        """
    path = '/'
    for key in path_template.split('/')[1:]:
        try:
            if key == '[]':
                path += str(len(dict_data_extractor(data, path)) - 1)
            else:
                path += key
                dict_data_extractor(data, path)
        except KeyError:
            raise KeyError("Wrong path: {}, the key {} is invalid!".format(path, key))
        path += '/'
    return '/'.join([str(int(p) + 1) if p.isdigit() else p for p in path.split('/')])[:-1]


def multiplex_path_by_list_indexes(path):
    """ Checks for indexes in path (which stands for the size of the list at the current path in dict)
        and produces the paths to all items of the list(s).
        :param path: The path for traversing the dict, unix-like (/path/key).
        :type path: string

        :return: list
        """
    sub_path = re.sub(r'\/\d+\/?', '/{}/', path)
    items = itertools.product(*(range(int(d)) for d in re.findall(r'\/(\d+)\/?', path)))
    return (sub_path.format(*ds) for ds in items)


def get_values(data, path):
    """ Traverses the path and returns all possible values.
        :param path: The path for traversing the dict, unix-like (/path/key).
        :type path: string

        :param data: Dictionary holding data.
        :type data: dict

        :return: dict {path: value}
        """
    with_lens = fill_list_lens_in_path(data, path)
    return {path: dict_data_extractor(data, path) for path in multiplex_path_by_list_indexes(with_lens)}


def parent_dir(path):
    """ Returns 'parent directory'.
        Example: /root/parent/child -> /root/parent
        :param path: A path represented unix-like (/path/key).
        :type path: string

        :return: string
        """
    return '/'.join(path.split('/')[:-1])


def dict_traversal(data, key, value=None):
    """ Traverses the dictionary and returns all paths that match to the given key and value.
        :param data: Dictionary holding data.
        :type data: dict

        :param key:
        :type key: string

        :param value:
        :type value: string (optional)

        :return: list
        """
    results = []

    def _inner_dict_traversal(data, key, value, res, path='/'):
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, dict):
                    _inner_dict_traversal(item, key, value, res, path + str(index) + '/')
            return res
        else:
            for k in data.keys():
                if k == key:
                    if value is None:
                        res.append(path + k)
                    else:
                        if data[k] == value:
                            res.append(path + k)
                else:
                    if isinstance(data[k], dict):
                        _inner_dict_traversal(data[k], key, value, res, path + k + '/')
                    elif isinstance(data[k], list):
                        for index, item in enumerate(data[k]):
                            if isinstance(item, dict):
                                _inner_dict_traversal(item, key, value, res, path + k + '/' + str(index) + '/')
            return res

    return _inner_dict_traversal(data, key, value, results)


def reformat_key(key, trans_dict):
    for replace_from, replace_to in trans_dict.items():
        key = key.replace(replace_from, replace_to)
    return key


def _clean_xml_key(key):
    return reformat_key(key, {'@': '', '#': '', 'class': 'class_name'})


def _clean_xml_keys(d):
    if isinstance(d, dict):
        for k in d:
            if isinstance(d[k], dict):
                _clean_xml_keys(d[k])
            if isinstance(d[k], list):
                for e in d[k]:
                    _clean_xml_keys(e)
            if '@' in k or '#' in k:
                d[_clean_xml_key(k)] = d[k]
                del d[k]
    return d


def _cmd_(command, timeout):
    try:
        p = Popen(command, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
        stdout, stderr = p.communicate(timeout=timeout)
    except OSError as e:
        raise UtilityNotFound(command[0], repr(e))
    except Exception as e:
        return -1, None, repr(e)
    return p.returncode, stdout.decode(), stderr.decode()


def host_command(command, timeout=HOST_COMMAND_TIMEOUT_SECONDS):
    rc, info, err = _cmd_(command.split(), timeout)
    if rc:
        raise HostCommandException(rc, info, err, command)
    return info


def scli(cli_args, xml=False):
    command = 'sh /opt/QLogic_Corporation/QConvergeConsoleCLI/scli {}'.format(cli_args)
    if xml:
        if scli_version() == '2.1.0':
            command += ' -x2'
        else:
            command += ' -x'
    return host_command(command)


def scli_version():
    command = 'sh /opt/QLogic_Corporation/QConvergeConsoleCLI/scli -v'
    return re.search(r'(?P<version>(\d+\.)(\d+\.?){2})', host_command(command)).groupdict()['version']


def _multiple_values_for_key(data, key, value):
    if isinstance(data[key], list):
        return data[key] + [value]
    return [data[key], value]


def merge_section(section, other_section):
    if section:
        try:
            section = section.strip()[1:-1]
            other_section = other_section.strip()[1:-1]
            key, value = section.split('=')
            o_key, o_value = other_section.split('=')
            return '[' + '_'.join((key.strip(), o_key.strip())) + ' = ' + '_'.join((value.strip(),
                                                                                    o_value.strip())) + ']'
        except ValueError as e:
            raise Exception(e, 'section: ' + section, 'other_section: ' + other_section)
    return other_section.strip()


def hierarchize_sections(syscli_output):
    section_stack = [None]
    indent_stack = [0]
    new_lines = []
    for line in syscli_output.splitlines():
        indentation = len(line) - len(line.strip())
        if all(c in line for c in ('[', '=', ']')):
            if indentation > indent_stack[-1]:
                line = ' ' * indentation + merge_section(section_stack[-1], line)
                section_stack.append(line.strip())
                indent_stack.append(indentation)
            elif indentation == indent_stack[-1]:
                line = ' ' * indentation + merge_section(section_stack[-1], line)
            else:
                while indentation <= indent_stack[-1]:
                    section_stack.pop()
                    indent_stack.pop()
                line = ' ' * indentation + merge_section(section_stack[-1], line)
                section_stack.append(line.strip())
                indent_stack.append(indentation)
        new_lines.append(line)
    return '\n'.join((line.strip() for line in new_lines))


def encode_and_compress_for_http(obj):
    """
    Encode and compress object for passing as data to InfiniBox HTTP request.
    """
    return base64.b64encode(zlib.compress(json.dumps(obj).encode('utf-8'), 9)).decode('utf-8')


def multiple_indexes_from_iter(indexes, list_):
    return itemgetter(*indexes)(list_)


def fc_hosts_realpaths():
    return (host_command(f'readlink {host_path}') for host_path in glob('/sys/class/fc_host/host*'))


def host_to_pcibus_mapping():
    return {host: pcibus
            for host, pcibus in
            (multiple_indexes_from_iter((6, 5), path.split('/')) for path in fc_hosts_realpaths())}


def _re_search_single(pattern, string):
    match = re.search(pattern, string)
    if match:
        return match.groups()[0]


def max_speed(supported_speeds):
    supported_speeds = (speed.split() for speed in supported_speeds.split(','))
    max_speed = max((int(speed), quantifier)
                    for speed, quantifier
                    in supported_speeds
                    if quantifier == 'Gbit')
    speed, quantifier = max_speed
    return f'{speed} {quantifier}'


def sfp_supported_speeds(speed_byte):
    def _check_online_bit(bit):
        return (speed_byte >> bit) & 0x01

    SPEED_MAP = ['1', 'Unknown ', '2', 'Unknown ', '4', '16', '8', '32']
    supported_speeds = ""
    bits = 8
    for bit in range(bits):
        if _check_online_bit(bit):
            supported_speeds += SPEED_MAP[bit]
            if SPEED_MAP[bit] != 'Unknown ':
                supported_speeds += "Gb "
    return supported_speeds.rstrip()


def formatter(data, formatting_directives):
    formatted = {**data}
    for key_handler, value_handler in formatting_directives:
        if isinstance(key_handler, tuple):
            old_key, new_key, keep_old = key_handler
            formatted[new_key] = value_handler(formatted[old_key])
            if not keep_old:
                del formatted[old_key]
        else:
            formatted[key_handler] = value_handler(formatted[key_handler])
    return formatted


def count_active_paths(paths):
    return sum(1 if path.get_state() == 'up' else 0 for path in paths)


def get_ip_addresses():
    def flatten_list_of_lists(parent_list):
        return [item for sublist in parent_list for item in sublist]

    interfaces_configs = [netifaces.ifaddresses(interface).get(netifaces.AF_INET, [])
                          for interface
                          in netifaces.interfaces()]

    interfaces_configs = flatten_list_of_lists(interfaces_configs)
    return (interface_config['addr'] for interface_config in interfaces_configs)


def get_boot_volume_name():
    """
    Returns, for example, "dde1-BOOT"
    """

    def is_lun0(device):
        return any(path.get_hctl().get_lun() == 0 for path in device.get_paths())

    try:
        [boot_vol] = [device for device in get_infinidat_native_multipath_block_devices() if is_lun0(device)]
    except ValueError:
        raise BootVolumeResolvingException(f'Could not find boot volume')
    return boot_vol.get_vendor().get_volume_name()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


def snake_case_to_camel_case(snake_case_string):
    """
    Converts string_like_this to StringLikeThis
    """
    words = snake_case_string.split('_')
    return ''.join(word.title() for word in words)


# TODO: Use these functions directly from a shared repo (probably iba_install)
@cached_function
def get_local_node_id():
    """
    This function uses /opt/dell/srvadmin/sbin/racadm, which can only run one instance at a time.
    Therefore, it will fail if several threads try to run it at the same time.
    """
    with threading_lock:
        local_node_id = _get_local_node_id()

    return local_node_id


@cached_function
def get_local_dde_node():
    return get_dde_node(get_local_node_id())


@cached_function
def get_local_dde_app_id():
    return get_local_dde_node().apprepr.string_id


@cached_function
def get_local_dde_role():
    """
    Returns the number of the DDE App, extracting it from from the volume name.
    For App 'a', returns '1' (and not 'a').
    """
    from iba_api.local_app import get_local_dde_app
    dde_node = get_dde_app(get_local_dde_app())
    return str(dde_node.role)


@cached_function
def get_local_dde_node():
    return get_dde_node(get_local_node_id())


@cached_function
def get_local_dde_app_id():
    return get_local_dde_node().apprepr.string_id


def is_standby_app():
    """
    Returns True iff this infiniguard-health process is running on the standby app.
    """
    return get_local_dde_role() == '3'


def get_epoch_time_milliseconds():
    return time.time_ns() // 1000000


def get_current_ibox_time():
    client = ntplib.NTPClient()
    response = client.request(IBOX_NODE_1_ADDRESS, version=3)
    return arrow.get(response.tx_time)


def get_infiniguard_health_start_time():
    """
    Returns an Arrow object representing the time in which the current infiniguard-health process started
    """
    return Arrow.fromtimestamp(psutil.Process(os.getpid()).create_time())


def get_default_policy_types():
    from iba_api.server.models import OriginatedByType
    return OriginatedByType.SYSTEM_POLICY, OriginatedByType.USER_POLICY


def get_project_parent():
    """
    Returns the directory in which the project resides, e.g /opt/infinidat on the DDE.
    """
    return pathlib.Path(__file__).parents[3]


def load_iba_mgmt_path():
    project_parent = get_project_parent()
    if pathlib.Path(INFINIDAT_INSTALL_FOLDER) == project_parent:  # Running in production
        iba_mgmt_path = project_parent.joinpath('iba-mgmt/src')
    else:
        iba_mgmt_path = project_parent.joinpath('iba_mgmt/src')

    try:
        if not iba_mgmt_path.exists() or not iba_mgmt_path.is_dir():
            raise ImportError(f"iba_mgmt path {iba_mgmt_path} not found")

        sys.path.append(str(iba_mgmt_path))

        # Testing imports
        import iba_api.snapshot
        from iba_api.snapshot.capacity_reporter import CapacityReporter

    except ImportError:
        _logger.exception("Cannot import dde_snapshot from iba_mgmt project")
        raise


def get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))

    return all_subclasses


def are_dicts_equal(dict1, dict2, excluded_keys=None):
    if not excluded_keys:
        excluded_keys = []

    dict1_copy = deepcopy(dict1)
    dict2_copy = deepcopy(dict2)

    for exclude_key in excluded_keys:
        dict1_copy.pop(exclude_key, None)
        dict2_copy.pop(exclude_key, None)

    return dict1_copy == dict2_copy


def are_same_types(list_of_objects1, list_of_objects2):
    """
    Returns True iff the two lists contain objects of the same classes.
    """
    return ({type(obj) for obj in list_of_objects1} ==
            {type(obj) for obj in list_of_objects2})


def get_latest_time(*time_objects):
    """
    Receives time objects, and returns the latest.
    Ignores None objects
    """
    return max([time_object for time_object in time_objects if time_object is not None]) if time_objects else None


@cached_function
def is_system_in_lab():
    return get_lab_mode_from_iguard_sysconfig() == '1'
