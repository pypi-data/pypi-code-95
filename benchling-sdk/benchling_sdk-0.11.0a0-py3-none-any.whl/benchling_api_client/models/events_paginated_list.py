from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.event import Event

T = TypeVar("T", bound="EventsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class EventsPaginatedList:
    """  """

    _events: List[Event]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("events={}".format(repr(self._events)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EventsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        events = []
        for events_item_data in self._events:
            events_item = events_item_data.to_dict()

            events.append(events_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "events": events,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        events = []
        _events = d.pop("events")
        for events_item_data in _events:
            events_item = Event.from_dict(events_item_data)

            events.append(events_item)

        next_token = d.pop("nextToken")

        events_paginated_list = cls(
            events=events,
            next_token=next_token,
        )

        events_paginated_list.additional_properties = d
        return events_paginated_list

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def events(self) -> List[Event]:
        return self._events

    @events.setter
    def events(self, value: List[Event]) -> None:
        self._events = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
