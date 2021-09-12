from .file import File
from .list import normalize_list
import json


def all_params_present(json_array: list, required_params: list) -> bool:
    required_params = normalize_list(required_params)
    json_array = normalize_list(json_array)

    for json_segment in json_array:
        if not isinstance(json_segment, dict):
            return False

        for required_value in required_params:
            if required_value not in json_segment:
                return False
    return True


def get_or_default(json_data, key, default):
    return default if key not in json_data else json_data[key]


def get_or_none(json_data, key):
    return get_or_default(json_data, key, None)


class JsonFile(File):
    def __init__(self, file_path: str, create_if_not_exists: bool = False):
        super().__init__(file_path, create_if_not_exists)

        if create_if_not_exists and not self.is_valid():
            self.set_json({})

    def is_valid(self):
        if not self.is_file_type('json'):
            return False

        try:
            json.loads(self.file_contents())
            return True
        except:
            return False

    def set_empty_json(self):
        self.set_json({})

    def set_json(self, json_data: dict):
        if not self.is_valid():
            self.get_or_create()
        json.dump(json_data, open(str(self.file_path), 'w'))

    def set_key(self, key: str, value):
        raw_data = self.data()
        raw_data[key] = value
        self.set_json(raw_data)

    def data(self):
        if self.is_valid():
            try:
                return json.load(self.read())
            except json.decoder.JSONDecodeError:
                self.set_json({})
                return self.data()
        else:
            raise ValueError("Invalid json file")


class RequiredJsonFile(JsonFile):
    def __init__(self, file_path):
        super().__init__(file_path)

        if not self.is_valid():
            raise ValueError("Invalid required json file")
