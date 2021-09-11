from typing import Any, cast, Dict, List, Type, TypeVar

import attr

from ..models.naming_strategy import NamingStrategy

T = TypeVar("T", bound="RegisterEntities")


@attr.s(auto_attribs=True, repr=False)
class RegisterEntities:
    """  """

    _entity_ids: List[str]
    _naming_strategy: NamingStrategy

    def __repr__(self):
        fields = []
        fields.append("entity_ids={}".format(repr(self._entity_ids)))
        fields.append("naming_strategy={}".format(repr(self._naming_strategy)))
        return "RegisterEntities({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        entity_ids = self._entity_ids

        naming_strategy = self._naming_strategy.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "entityIds": entity_ids,
                "namingStrategy": naming_strategy,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        entity_ids = cast(List[str], d.pop("entityIds"))

        naming_strategy = NamingStrategy(d.pop("namingStrategy"))

        register_entities = cls(
            entity_ids=entity_ids,
            naming_strategy=naming_strategy,
        )

        return register_entities

    @property
    def entity_ids(self) -> List[str]:
        return self._entity_ids

    @entity_ids.setter
    def entity_ids(self, value: List[str]) -> None:
        self._entity_ids = value

    @property
    def naming_strategy(self) -> NamingStrategy:
        return self._naming_strategy

    @naming_strategy.setter
    def naming_strategy(self, value: NamingStrategy) -> None:
        self._naming_strategy = value
