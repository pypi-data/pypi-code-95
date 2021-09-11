from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="ExportItemRequest")


@attr.s(auto_attribs=True, repr=False)
class ExportItemRequest:
    """  """

    _id: str

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        return "ExportItemRequest({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "id": id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        export_item_request = cls(
            id=id,
        )

        return export_item_request

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value
