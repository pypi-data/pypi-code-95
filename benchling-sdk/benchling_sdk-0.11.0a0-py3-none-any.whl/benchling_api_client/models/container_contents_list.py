from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.container_content import ContainerContent

T = TypeVar("T", bound="ContainerContentsList")


@attr.s(auto_attribs=True, repr=False)
class ContainerContentsList:
    """  """

    _contents: List[ContainerContent]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("contents={}".format(repr(self._contents)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerContentsList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        contents = []
        for contents_item_data in self._contents:
            contents_item = contents_item_data.to_dict()

            contents.append(contents_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "contents": contents,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        contents = []
        _contents = d.pop("contents")
        for contents_item_data in _contents:
            contents_item = ContainerContent.from_dict(contents_item_data)

            contents.append(contents_item)

        container_contents_list = cls(
            contents=contents,
        )

        container_contents_list.additional_properties = d
        return container_contents_list

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
    def contents(self) -> List[ContainerContent]:
        return self._contents

    @contents.setter
    def contents(self, value: List[ContainerContent]) -> None:
        self._contents = value
