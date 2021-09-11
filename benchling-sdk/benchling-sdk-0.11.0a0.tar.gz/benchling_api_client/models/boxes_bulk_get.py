from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.box import Box

T = TypeVar("T", bound="BoxesBulkGet")


@attr.s(auto_attribs=True, repr=False)
class BoxesBulkGet:
    """  """

    _boxes: List[Box]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("boxes={}".format(repr(self._boxes)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BoxesBulkGet({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        boxes = []
        for boxes_item_data in self._boxes:
            boxes_item = boxes_item_data.to_dict()

            boxes.append(boxes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "boxes": boxes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        boxes = []
        _boxes = d.pop("boxes")
        for boxes_item_data in _boxes:
            boxes_item = Box.from_dict(boxes_item_data)

            boxes.append(boxes_item)

        boxes_bulk_get = cls(
            boxes=boxes,
        )

        boxes_bulk_get.additional_properties = d
        return boxes_bulk_get

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
    def boxes(self) -> List[Box]:
        return self._boxes

    @boxes.setter
    def boxes(self, value: List[Box]) -> None:
        self._boxes = value
