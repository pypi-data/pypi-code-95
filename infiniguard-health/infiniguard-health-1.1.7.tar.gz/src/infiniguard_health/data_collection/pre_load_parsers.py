import re
from copy import deepcopy

from infiniguard_health.utils import parent_dir, dict_traversal, dict_data_extractor


def pre_load_parser_omr_psus(data):
    for psu in data:
        psu['location_id'] = int(psu['location'][2])
    return data


def pre_load_parser_omr_fans(data):
    for fan in data:
        fan['fan_id'] = int(fan['probe_name'][-1])
    return data


@deepcopy
def pre_load_parser_volumes(data):
    for volume in data:
        volume['volume_id'] = re.sub(r'dde\d-', '', volume['volume_name'])
    return data


def pre_load_parser_lshw_dimms(data):
    data = data['memory_info']
    dimm_paths = (parent_dir(p)
                  for p in dict_traversal(data, 'slot')
                  if 'children' not in p and dict_data_extractor(data, p) != 'System board or motherboard')
    return (dict_data_extractor(data, path) for path in dimm_paths)


def pre_load_parser_lshw_eth(data):
    data = data['network_info']
    for port in data:
        for key, value in port['configuration'].items():
            port[key] = value
    return data


def pre_load_parser_lshw_psu(data):
    return data['power_info']


def pre_load_parser_snapshots(data):
    for snapshot in data:
        snapshot['origin']['policy_type'] = snapshot['originated_by']
        snapshot['origin']['id'] = snapshot['originated_by']

    return data
