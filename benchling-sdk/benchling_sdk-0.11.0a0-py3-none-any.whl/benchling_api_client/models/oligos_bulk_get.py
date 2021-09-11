from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..models.dna_oligo import DnaOligo
from ..models.rna_oligo import RnaOligo

T = TypeVar("T", bound="OligosBulkGet")


@attr.s(auto_attribs=True, repr=False)
class OligosBulkGet:
    """  """

    _oligos: List[Union[DnaOligo, RnaOligo]]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("oligos={}".format(repr(self._oligos)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "OligosBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        oligos = []
        for oligos_item_data in self._oligos:
            if isinstance(oligos_item_data, DnaOligo):
                oligos_item = oligos_item_data.to_dict()

            else:
                oligos_item = oligos_item_data.to_dict()

            oligos.append(oligos_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "oligos": oligos,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        oligos = []
        _oligos = d.pop("oligos")
        for oligos_item_data in _oligos:

            def _parse_oligos_item(data: Union[Dict[str, Any]]) -> Union[DnaOligo, RnaOligo]:
                oligos_item: Union[DnaOligo, RnaOligo]
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    oligos_item = DnaOligo.from_dict(data)

                    return oligos_item
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                oligos_item = RnaOligo.from_dict(data)

                return oligos_item

            oligos_item = _parse_oligos_item(oligos_item_data)

            oligos.append(oligos_item)

        oligos_bulk_get = cls(
            oligos=oligos,
        )

        oligos_bulk_get.additional_properties = d
        return oligos_bulk_get

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
    def oligos(self) -> List[Union[DnaOligo, RnaOligo]]:
        return self._oligos

    @oligos.setter
    def oligos(self, value: List[Union[DnaOligo, RnaOligo]]) -> None:
        self._oligos = value
