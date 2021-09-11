from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..models.aa_sequence import AaSequence
from ..models.batch import Batch
from ..models.custom_entity import CustomEntity
from ..models.dna_sequence import DnaSequence
from ..models.measurement import Measurement
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerContent")


@attr.s(auto_attribs=True, repr=False)
class ContainerContent:
    """  """

    _concentration: Measurement
    _batch: Optional[Batch]
    _entity: Union[None, DnaSequence, AaSequence, CustomEntity]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("concentration={}".format(repr(self._concentration)))
        fields.append("batch={}".format(repr(self._batch)))
        fields.append("entity={}".format(repr(self._entity)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerContent({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        concentration = self._concentration.to_dict()

        batch = self._batch.to_dict() if self._batch else None

        entity: Union[None, Dict[str, Any]]
        if isinstance(self._entity, Unset):
            entity = UNSET
        if self._entity is None:
            entity = None
        elif isinstance(self._entity, DnaSequence):
            entity = self._entity.to_dict()

        elif isinstance(self._entity, AaSequence):
            entity = self._entity.to_dict()

        else:
            entity = self._entity.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "concentration": concentration,
                "batch": batch,
                "entity": entity,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        concentration = Measurement.from_dict(d.pop("concentration"))

        batch = None
        _batch = d.pop("batch")
        if _batch is not None:
            batch = Batch.from_dict(_batch)

        def _parse_entity(
            data: Union[None, Dict[str, Any]]
        ) -> Union[None, DnaSequence, AaSequence, CustomEntity]:
            entity: Union[None, DnaSequence, AaSequence, CustomEntity]
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                entity = DnaSequence.from_dict(data)

                return entity
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                entity = AaSequence.from_dict(data)

                return entity
            except:  # noqa: E722
                pass
            if not isinstance(data, dict):
                raise TypeError()
            entity = CustomEntity.from_dict(data)

            return entity

        entity = _parse_entity(d.pop("entity"))

        container_content = cls(
            concentration=concentration,
            batch=batch,
            entity=entity,
        )

        container_content.additional_properties = d
        return container_content

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
    def concentration(self) -> Measurement:
        return self._concentration

    @concentration.setter
    def concentration(self, value: Measurement) -> None:
        self._concentration = value

    @property
    def batch(self) -> Optional[Batch]:
        return self._batch

    @batch.setter
    def batch(self, value: Optional[Batch]) -> None:
        self._batch = value

    @property
    def entity(self) -> Optional[Union[DnaSequence, AaSequence, CustomEntity]]:
        return self._entity

    @entity.setter
    def entity(self, value: Optional[Union[DnaSequence, AaSequence, CustomEntity]]) -> None:
        self._entity = value
