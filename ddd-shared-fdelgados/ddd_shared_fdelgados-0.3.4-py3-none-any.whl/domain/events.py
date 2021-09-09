from datetime import datetime
from typing import Dict, Optional, Any
import json
import abc


class DomainEvent(metaclass=abc.ABCMeta):
    def __init__(self, aggregate_id: Optional[Any] = None):
        self._occurred_on = datetime.now()
        self._aggregate_id = aggregate_id

    @abc.abstractmethod
    def event_name(self) -> str:
        raise NotImplementedError

    @property
    def occurred_on(self):
        return self._occurred_on

    @property
    def aggregate_id(self) -> Optional[Any]:
        return self._aggregate_id

    def serialize(self) -> str:
        def json_converter(o):
            if isinstance(o, datetime):
                return o.__str__()

        properties = self.__sanitize_property_names()

        return json.dumps(properties, ensure_ascii=False, default=json_converter)

    def __sanitize_property_names(self) -> Dict:
        properties = {}
        for property_name, value in self.__dict__.items():
            properties[property_name.lstrip('_')] = value

        return properties

    def __str__(self) -> str:
        return self.serialize()

    def __repr__(self) -> str:
        return "DomainEvent <{}>".format(self.event_name())
