from argparse import Namespace, ArgumentParser, SUPPRESS
from typing import Dict, List, Any
from PyInquirer import prompt, Validator, ValidationError
from swimlane_platform.lib.models import Automation
from swimlane_platform.lib.version_manager import semver_parse
from os import path
from validators.domain import domain
from validators.ip_address import ipv4, ipv6
import json


class AnswerRequiredValidator(Validator):
    def validate(self, document):
        if not document or not document.text:
            raise ValidationError(
                message='Entry required.',
                cursor_position=len(document.text))  # Move cursor to end


class VersionValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(VersionValidator, self).validate(document)
        if document.text in ['dev', 'develop', 'latest']:
            return
        version = semver_parse(document.text)
        if not version:
            raise ValidationError(message='Version provided is invalid semver and cannot be parsed.',
                                  cursor_position=len(document.text))


class DnsValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(DnsValidator, self).validate(document)
        if ' ' in document.text:
            raise ValidationError(message='DNS should be comma-separated and cannot contain spaces.',
                                  cursor_position=len(document.text))
        for dns in document.text.split(","):
            if domain(dns) or ipv4(dns) or ipv6(dns):
                continue
            elif dns[0] == "*" and domain(dns.lstrip("*.")):
                continue
            raise ValidationError(message='DNS should be valid urls or ip addresses.',
                                  cursor_position=len(document.text))


class PathExistsValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(PathExistsValidator, self).validate(document)
        if not path.exists(document.text):
            raise ValidationError(
                message='Path doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class ContainingDirectoryExistsValidator(AnswerRequiredValidator):
    def validate(self, document):
        super(ContainingDirectoryExistsValidator, self).validate(document)
        if not path.exists(path.dirname(document.text)):
            raise ValidationError(
                message='Path doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class LogFileOptional(Validator):
    def validate(self, document):
        if not document or not document.text:
            return
        if not path.exists(path.dirname(document.text)):
            raise ValidationError(
                message='Directory doesn\'t exist.',
                cursor_position=len(document.text))  # Move cursor to end


class Arguments(Namespace):

    def __init__(self, **kwargs):
        super(Arguments, self).__init__(**kwargs)

    def __getattr__(self, item):
        return None


class Configuration(dict):

    def __init__(self, action=Automation.Normal, file_path=None):
        # type: (str, str) -> None
        super(Configuration, self).__init__()
        self.action = action
        self.file_path = file_path

    def add_other_source(self, other_config, overwrite=False):
        # type: (Dict[str, Any], bool) -> None
        """
        Ability to add other configurations, from environment variables for instance.
        :param other_config: Other configurations. Dictionary.
        :param overwrite: Whether to add it to existing or overwrite them.
        """
        for key, value in other_config.items():
            if key not in self or overwrite:
                self[key] = value

    def collect(self, questions):
        # type: (List[Dict[str, str]]) -> None
        self._add_question_lookup_in_args(questions)
        self._load_config_file()
        remaining_questions = [q for q in questions if not q.get('name') in self]
        self.update(prompt(remaining_questions, answers=self))
        self._save_config_file()

    def _save_config_file(self):
        # type: () -> None
        """
        If user requested to record session, saves answers to the file.
        """
        if self.action == Automation.Save:
            assert self.file_path
            if not path.exists(self.file_path):
                self._write_dict(self.file_path, self)
            else:
                existing = self._read_dict(self.file_path)
                for key, value in self.items():
                    existing[key] = value
                self._write_dict(self.file_path, existing)

    def _load_config_file(self):
        # type: () -> None
        """
        If users request to load the file, then it reads it and updates inner dictionary.
        """
        if self.action == Automation.Load:
            assert self.file_path
            config = self._read_dict(self.file_path)
            self.update(config)

    @property
    def args(self):
        # type: () -> Arguments
        """
        Answers in the type of Arguments. Values can be found by key or attribute.
        Returns new object each time. Do not assign it to a variable and expect it being updated.
        :return: Answers as Arguments.
        """
        return Arguments(**self)

    def _add_question_lookup_in_args(self, questions):
        # type: (List[Dict[str, str]]) -> None
        """
        Checks if the questions has been answered in cli arguments.
        :param questions: Questions to check.
        """
        parser = ArgumentParser()

        def get_argument_type(question_type):
            if question_type == 'input' or question_type == 'password' or question_type == 'list':
                return 'store'
            elif question_type == 'confirm':
                return 'store_true'
            else:
                raise Exception("The question type is not mapped.")

        for question in questions:
            parser.add_argument('--{name}'.format(name=question.get('name')),
                                help=question.get('message'),
                                default=SUPPRESS,
                                action=get_argument_type(question.get('type')))
        args, _ = parser.parse_known_args()
        self.update(dict(args.__dict__))

    @staticmethod
    def _write_dict(file_path, _dict):
        # type: (str, Dict[str, Any]) -> None
        """
        Writes dictionary as a json file.
        :param file_path: File path to save json to.
        :param _dict: Dictionary to save.
        """
        assert file_path
        assert _dict
        with open(file_path, 'w') as fp:
            json.dump(_dict, fp, indent=2, separators=(',', ': '))

    @staticmethod
    def _read_dict(file_path):
        # type: (str) -> Dict[str: Any]
        """
        Reads dictionary from json file
        :param file_path: File path to read json from.
        """
        assert file_path
        with open(file_path, 'r') as fp:
            return json.load(fp)
