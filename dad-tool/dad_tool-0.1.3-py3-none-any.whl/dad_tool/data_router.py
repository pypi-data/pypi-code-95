import json
import random


def list_addresses(data):
    address_json = _open_json_file(data)

    return address_json


def random_address(data):
    address_json = _open_json_file(data)
    random_address = random.choice(address_json)

    return random_address


def list_iso_country_codes():
    raise NotImplementedError()


def _open_json_file(data):
    address_file = _variables(data)
    with open(address_file, 'r') as json_file:
        address_json = json.load(json_file)

    return address_json


def _variables(data):
    # DAD variables
    address_directory = 'dad/src/addresses'
    file_extension = '-addresses.min.json'
    australia_directory = 'australia'
    canada_directory = 'canada'
    china_directory = 'china'
    europe_directory = 'europe'
    mexico_directory = 'mexico'
    united_states_directory = 'united-states'

    # Country variables
    try:
        data_file_paths = {
            # Australia
            'AU_VT': f'{address_directory}/{australia_directory}/vt{file_extension}',
            # Canada
            'CA_BC': f'{address_directory}/{canada_directory}/bc{file_extension}',
            # China
            'CN_BJ': f'{address_directory}/{china_directory}/bj{file_extension}',
            'CN_HK': f'{address_directory}/{china_directory}/hk{file_extension}',
            # Europe
            'EU_DE': f'{address_directory}/{europe_directory}/de{file_extension}',
            'EU_ES': f'{address_directory}/{europe_directory}/es{file_extension}',
            'EU_UK': f'{address_directory}/{europe_directory}/uk{file_extension}',
            # Mexico
            'MX_MX': f'{address_directory}/{mexico_directory}/mx{file_extension}',
            # United States
            'US_AZ': f'{address_directory}/{united_states_directory}/az{file_extension}',
            'US_CA': f'{address_directory}/{united_states_directory}/ca{file_extension}',
            'US_ID': f'{address_directory}/{united_states_directory}/id{file_extension}',
            'US_KS': f'{address_directory}/{united_states_directory}/ks{file_extension}',
            'US_NV': f'{address_directory}/{united_states_directory}/nv{file_extension}',
            'US_NY': f'{address_directory}/{united_states_directory}/ny{file_extension}',
            'US_OR': f'{address_directory}/{united_states_directory}/or{file_extension}',
            'US_TX': f'{address_directory}/{united_states_directory}/tx{file_extension}',
            'US_UT': f'{address_directory}/{united_states_directory}/ut{file_extension}',
            'US_WA': f'{address_directory}/{united_states_directory}/wa{file_extension}',
        }

        data_file_path = data_file_paths[data.upper()]
    except KeyError:
        raise

    return data_file_path
