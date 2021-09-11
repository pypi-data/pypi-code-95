from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="LabelTemplate")


@attr.s(auto_attribs=True, repr=False)
class LabelTemplate:
    """  """

    _id: str
    _name: str
    _zpl_template: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("zpl_template={}".format(repr(self._zpl_template)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "LabelTemplate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        name = self._name
        zpl_template = self._zpl_template

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "zplTemplate": zpl_template,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        zpl_template = d.pop("zplTemplate")

        label_template = cls(
            id=id,
            name=name,
            zpl_template=zpl_template,
        )

        label_template.additional_properties = d
        return label_template

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
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def zpl_template(self) -> str:
        return self._zpl_template

    @zpl_template.setter
    def zpl_template(self, value: str) -> None:
        self._zpl_template = value
