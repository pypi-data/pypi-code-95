from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="Printer")


@attr.s(auto_attribs=True, repr=False)
class Printer:
    """  """

    _address: str
    _id: str
    _name: str
    _registry_id: str
    _description: Optional[str]
    _port: Optional[int]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("address={}".format(repr(self._address)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("description={}".format(repr(self._description)))
        fields.append("port={}".format(repr(self._port)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Printer({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        address = self._address
        id = self._id
        name = self._name
        registry_id = self._registry_id
        description = self._description
        port = self._port

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "address": address,
                "id": id,
                "name": name,
                "registryId": registry_id,
                "description": description,
                "port": port,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        address = d.pop("address")

        id = d.pop("id")

        name = d.pop("name")

        registry_id = d.pop("registryId")

        description = d.pop("description")

        port = d.pop("port")

        printer = cls(
            address=address,
            id=id,
            name=name,
            registry_id=registry_id,
            description=description,
            port=port,
        )

        printer.additional_properties = d
        return printer

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
    def address(self) -> str:
        return self._address

    @address.setter
    def address(self, value: str) -> None:
        self._address = value

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
    def registry_id(self) -> str:
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @property
    def description(self) -> Optional[str]:
        return self._description

    @description.setter
    def description(self, value: Optional[str]) -> None:
        self._description = value

    @property
    def port(self) -> Optional[int]:
        return self._port

    @port.setter
    def port(self, value: Optional[int]) -> None:
        self._port = value
