import json

import re


class JSONSerializable:
    def to_json(self) -> str:
        return underscore_to_camel(json.dumps(
            self,
            default=lambda obj: obj.__dict__,
            ensure_ascii=True,
            indent=4,
        ))



camel_pattern = re.compile(r'([A-Z])')
under_pattern = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pattern.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pattern.sub(lambda x: x.group(1).upper(), name)
