import os
from typing import Dict, List, Set, Tuple, Union

import yaml

_FIELD_DICT = '_inner_dict'
_FIELD_KEY_PATH_SEPARATOR = '_key_path_separator'
_EXCLUDE_FIELDS_ = [_FIELD_DICT, _FIELD_KEY_PATH_SEPARATOR, '__len__']


class ConfigDict(object):

    def __init__(self, value_dict: Dict = None, key_path_separator='.'):
        self._key_path_separator = key_path_separator
        self._inner_dict = dict()
        if value_dict:
            self._inner_dict = self._init_config_dict(value_dict)

    def _init_config_dict(self, value_dict: Dict) -> Dict:
        config_dict = dict()
        for (k, v) in value_dict.items():
            if isinstance(v, Dict):
                config_dict[k] = ConfigDict(v, self._key_path_separator)
            elif isinstance(v, (List, Tuple, Set)):
                config_dict[k] = self._init_config_iterable(v)
            else:
                config_dict[k] = v
        return config_dict

    def _init_config_iterable(self, v: Union[List, Set, Tuple]) -> List:
        config_iterable = list()
        for sub_v in v:
            if isinstance(sub_v, Dict):
                config_iterable.append(ConfigDict(sub_v, self._key_path_separator))
            elif isinstance(sub_v, (List, Tuple, Set)):
                config_iterable.append(self._init_config_iterable(sub_v))
            else:
                config_iterable.append(sub_v)
        return config_iterable

    def __getattr__(self, key):
        if key in _EXCLUDE_FIELDS_:
            return self.__dict__[key]
        return self.__dict__[_FIELD_DICT].setdefault(key, ConfigDict(key_path_separator=self._key_path_separator))

    def __setattr__(self, key, value):
        if key in _EXCLUDE_FIELDS_:
            self.__dict__[key] = value
        else:
            if isinstance(value, Dict):
                self.__dict__[_FIELD_DICT][key] = ConfigDict(value, self._key_path_separator)
            elif isinstance(value, (List, Tuple, Set)):
                self.__dict__[_FIELD_DICT][key] = self._init_config_iterable(value)
            else:
                self.__dict__[_FIELD_DICT][key] = value

    def __bool__(self):
        return bool(self._inner_dict)

    def merge(self, another):
        from mergedeep import merge
        assert isinstance(another, ConfigDict), 'cannot merge with non-ConfigDict object'
        merged_dict = self.to_dict()
        merge(merged_dict, another.to_dict())
        return ConfigDict(merged_dict)

    def to_dict(self) -> Dict:
        value_dict = dict()
        for (k, v) in self._inner_dict.items():
            if isinstance(v, ConfigDict):
                value_dict[k] = v.to_dict()
            elif isinstance(v, (List, Tuple, Set)):
                value_dict[k] = self._to_data_list(v)
            else:
                value_dict[k] = v
        return value_dict

    def _to_data_list(self, v: Union[List, Set, Tuple]) -> List:
        data_list = list()
        for sub_v in v:
            if isinstance(sub_v, ConfigDict):
                data_list.append(sub_v.to_dict())
            elif isinstance(sub_v, (List, Tuple, Set)):
                data_list.append(self._to_data_list(sub_v))
            else:
                data_list.append(sub_v)
        return data_list

    def __getitem__(self, key: str):
        if self._key_path_separator in key:
            key_path = [t for t in key.split(self._key_path_separator) if t and t.strip()]
            config_obj = self._inner_dict
            for key_token in key_path:
                config_obj = self._getitem_ext_(config_obj, key_token)
            return config_obj

        return self._getitem_ext_(self._inner_dict, key)

    def _getitem_ext_(self, config_obj: Dict, key: str):
        key_idx = None
        if '[' in key and key[-1] == ']':
            key, key_idx = key[:-1].split('[')
        config_obj = config_obj[key]
        if key_idx and isinstance(config_obj, (List, Tuple, Set)):
            config_obj = config_obj[int(key_idx)]
        return config_obj


def load_config_local(boostrap: ConfigDict, env: str, workdir: str) -> ConfigDict:
    from mergedeep import merge
    app_name = boostrap.application.name

    config_files = ['application', 'application-' + env, app_name + '-' + env, app_name]
    config_exts = ['yaml', 'yml']

    config_dict = dict()
    config_dict.update(boostrap.to_dict())
    for config_file in config_files:
        for config_ext in config_exts:
            config_file_path = os.path.join(workdir, 'configs', config_file + '.' + config_ext)
            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as cf:
                    merge(config_dict, yaml.load(cf, Loader=yaml.SafeLoader))
                break

    return ConfigDict(config_dict)


if __name__ == '__main__':
    raw_dict = {
        'a': {
            'x': [
                {
                    'name': 'baihe',
                    'age': 38
                },
                {
                    'name': 'wyq',
                    'age': 38
                }
            ],
            'y': 4
        }
    }

    c = ConfigDict(raw_dict, key_path_separator='/')
    c.z = dict(fuck=3)
    print(c.a.x[0].to_dict())
    print(c['z'].fuck)
    print(c['a']['x'][0]['name'])
    print(c.a['x[0]'].name)
