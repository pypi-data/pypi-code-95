import yaml
from typing import Dict, Union, List

from swimlane_platform.lib import ExpectedException
from swimlane_platform.lib.debug_decorators import debug_function_args, debug_function_return
from swimlane_platform.lib.logger import SplitStreamLogger
from swimlane_platform.lib.functions import merge_dictionaries


class DockerComposeFileManager:

    def __init__(self, logger, docker_compose_file):
        # type: (SplitStreamLogger, str) -> None
        self.logger = logger
        self.docker_compose_file = docker_compose_file
        with open(docker_compose_file) as f:
            self._dict = yaml.safe_load(f)
            f.close()

    @debug_function_return
    @debug_function_args
    def get(self, *attrs):
        # type: (str) -> Union[Dict[str,Union[str, List[str]]], str, None]
        pointer = self._dict
        for attr in attrs:
            if attr not in pointer:
                return None
            pointer = pointer[attr]
        return pointer

    @debug_function_return
    @debug_function_args
    def get_or_create_dict(self, *attrs):
        # type: (str) -> Dict[str, Union[str, List[str]]]
        pointer = self._dict
        for attr in attrs:
            if attr not in pointer or type(pointer[attr]) is not dict:
                pointer[attr] = dict()
            pointer = pointer[attr]
        return pointer

    @debug_function_args
    def append_or_create_list(self, value, *attr):
        # type: (str, str) -> None
        """
        Appends to the list at the end of property values or creates a new list at indicated location.
        :param value: Value to add.
        :param attr: Properties to add it to.
        """
        pointer = self.get_or_create_dict(*attr[:-1])
        last_attr = attr[-1]
        if last_attr not in pointer:
            pointer[last_attr] = [value]
        elif isinstance(pointer[last_attr], list):
            if value not in pointer[last_attr]:
                pointer[last_attr].append(value)
        else:
            raise LookupError('Wrong type found.')

    @debug_function_args
    def subtract_from_list(self, value, *attr):
        # type: (str, str) -> None
        """
        Removes from the list at the end of property chain or ignores if property chain doesn't exists.
        :param value: Value to add.
        :param attr: Properties to add it to.
        """
        pointer = self.get(*attr[:-1])
        if not pointer:
            return
        last_attr = attr[-1]
        if last_attr not in pointer:
            return
        elif isinstance(pointer[last_attr], list):
            if value in pointer[last_attr]:
                pointer[last_attr].remove(value)
        else:
            raise LookupError('Wrong type found.')

    def save(self):
        self.save_as(self.docker_compose_file)

    @debug_function_args
    def save_as(self, file_path):
        with open(file_path, 'w') as fs:
            yaml.safe_dump(self._dict, fs, default_flow_style=False)

    @debug_function_args
    def set(self, value, *attr):
        pointer = self.get_or_create_dict(*attr[:-1])
        last_attr = attr[-1]
        pointer[last_attr] = value

    @debug_function_return
    def get_image_tags(self):
        # type: () -> List[str]
        if not self._dict:
            raise ExpectedException("The {file} failed to load correctly.".format(file=self.docker_compose_file))
        services = self._dict.get('services').items()
        if not services:
            self.logger.debug("No services were found in {file}.".format(file=self.docker_compose_file))
        return [service.get('image') for name, service in services if service]

    @debug_function_return
    @debug_function_args
    def replace_in_file_and_reload(self, old_value, new_value):
        # type: (str, str) -> None
        """Replaces tags to values
        :param old_value: Tag
        :param new_value: New value
        """
        assert old_value, 'old_value was not supplied'
        assert new_value or new_value == '', 'new_value was not supplied'
        with open(self.docker_compose_file) as f:
            content = f.read()
        with open(self.docker_compose_file, 'w') as f:
            new_content = content.replace(old_value, new_value)
            f.write(new_content)
            message = "{file} was replaced with {content}.".format(file=self.docker_compose_file, content=new_content)
            self.logger.verbose(message)
        with open(self.docker_compose_file) as f:
            self._dict = yaml.safe_load(f)

    def override(self, docker_compose_file_manager):
        # type: (DockerComposeFileManager) -> None
        """Merges content of two docker-compose files similar to docker-compose override functionality
        :param docker_compose_file_manager: Additional docker-compose file
        """
        # noinspection PyProtectedMember
        self._dict = merge_dictionaries(self._dict, docker_compose_file_manager._dict)
