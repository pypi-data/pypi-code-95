import re
import xmltodict
from collections import defaultdict
from configparser import ConfigParser

from infiniguard_health.utils import reformat_key, _multiple_values_for_key, hierarchize_sections, _re_search_single, \
    dict_data_extractor, parent_dir, dict_traversal, count_active_paths


def lshw_parser(data):
    lshw_classes = ('network', 'memory', 'power')
    result = {}
    for lshw_class in lshw_classes:
        paths_of_class = (parent_dir(path) for path in dict_traversal(data, 'class', lshw_class))
        result[f'{lshw_class}_info'] = [dict_data_extractor(data, path) for path in paths_of_class]
    return result


def omreport_parser(data):
    def _format_omr_key(key):
        return re.sub(r'_{2,}', '', key.lower().replace(' ', '_'))

    parsed_info = {}
    parsed_listed_info = []
    keys = []
    for line in data.splitlines():
        if ';' in line and '' not in line.split(';'):
            delimeter_count = line.count(';')
            if delimeter_count == 1:
                key, value = line.split(';')
                parsed_info[_format_omr_key(key)] = value
            elif delimeter_count > 1:
                if not keys:
                    keys = line.split(';')
                else:
                    values = line.split(';')
                    parsed_listed_info.append({_format_omr_key(key): val for key, val in zip(keys, values)})
        else:
            keys = []
    return parsed_listed_info if parsed_listed_info else parsed_info


def ethtool_parser(data):
    def _format_ethtool_key(key):
        return reformat_key(key, {c: '_' for c in (' ', '(', ')', '-', ',', '/')}).lower()

    parsed_ethtool_data = {}
    for prop in data.splitlines():
        if ':' in prop:
            key, value = [part.strip() for part in prop.split(':', 1)]
            key = _format_ethtool_key(key)
            if key in parsed_ethtool_data:
                parsed_ethtool_data[key] = _multiple_values_for_key(parsed_ethtool_data, key, value)
            else:
                parsed_ethtool_data[key] = value
        else:
            value = prop.strip()
            parsed_ethtool_data[key] = _multiple_values_for_key(parsed_ethtool_data, key, value)
    return parsed_ethtool_data


def syscli_parser(data):
    filtered_output = '[total]\n' + '\n'.join((line for line in data.splitlines() if '=' in line))
    hierarchized = hierarchize_sections(filtered_output)

    config = ConfigParser(allow_no_value=True, strict=False)
    config.read_string(hierarchized)
    config.remove_section('total')

    return [{k.lower().replace(' ', '_'): v
             for k, v in config.items(section)}
            for section in config if config.items(section)]


def syscli_map_interfaces_to_devices(data):
    identified_devices = {device['device_name']: device for device in data if 'device_name' in device}
    interface_to_device_mapping = defaultdict(list)
    for interface in data:
        if 'interface_name' in interface:
            device_name_match = re.match(r'(.*?[^\:|\.]+)', interface['interface_name'])
            if device_name_match:
                device_name = device_name_match.group()
                interface_to_device_mapping[device_name].append(interface)

    for key, dev in identified_devices.items():
        dev['interfaces_count'] = dev.get('total_count', 0)
        dev['interfaces'] = interface_to_device_mapping[key]
    return identified_devices


def lspci_fc_parser(data):
    patterns = (
        ('model', r'Fibre Channel: (.*)'),
        ('hba_info', r'Subsystem: (.*)'),
        ('driver', r'Kernel driver in use: (.*)'),
        ('part_num', r'\[PN\] Part number: (.*)'),
        ('serial_num', r'\[SN\] Serial number: (.*)'),
        ('engineering_changes', r'\[EC\] Engineering changes: (.*)'),
    )
    return {key: _re_search_single(pattern, data) for key, pattern in patterns}


def gc_fcports_parser(data):
    gc_fcports_dict = xmltodict.parse(data)
    ports_data_list = gc_fcports_dict['root']['FCPORTS']['FCPORT']
    ports_data_list = [{key.lower(): value for key, value in port.items()} for port in ports_data_list]
    ports_data_dict = {port['alias']: port for port in ports_data_list}
    return ports_data_dict


def omr_system_versions_parser(data):
    omreport_info = data.splitlines()
    key_version_list = ((name_line, version_line) for name_line, version_line in zip(omreport_info, omreport_info[1:])
                        if 'Name' in name_line)

    key_version_list = ((key.split(';', 1)[1].strip(), version.split(';', 1)[1].strip())
                        for key, version in key_version_list)

    return {key.lower().replace(' ', '_'): version for key, version in key_version_list}


def volumes_parser(data):
    return [{'device_name': block_device.get_display_name(),
             'volume_name': block_device.get_vendor().get_volume_name(),
             'wwid': block_device.get_wwid(),
             'number_of_active_paths': count_active_paths(block_device.get_paths())}
            for block_device in data]


def bond_parser(data):
    def _dictify(data):
        data_as_dict = {}
        for line in data.splitlines():
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().replace(' (', '_').replace(' ', '_').replace(')', '').lower()
                data_as_dict[key] = value.strip()
        return data_as_dict

    data_splitted_by_empty_line = data.split('\n\n')
    parsed_data = {}
    slaves_data = []
    for data_section in data_splitted_by_empty_line:
        if data_section.startswith('Slave Interface'):
            slave_dict = _dictify(data_section)
            slaves_data.append(slave_dict)
        else:
            parsed_data.update(_dictify(data_section))

        parsed_data['slaves'] = slaves_data
    return parsed_data
