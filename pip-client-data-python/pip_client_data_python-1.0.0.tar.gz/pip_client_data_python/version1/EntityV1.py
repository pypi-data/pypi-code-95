# -*- coding: utf-8 -*-
from typing import Dict

from pip_services3_commons.data import IStringIdentifiable


class EntityV1(IStringIdentifiable):
    def __init__(self, id: str = None, site_id: str = None, type: str = None, name: str = None, content: str = None):
        self.id = id
        self.type = type
        self.site_id = site_id
        self.name = name
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {
            'id': self.id,
            'type': self.type,
            'site_id': self.site_id,
            'name': self.name,
            'content': self.content
        }
