from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob_multipart_create_type import BlobMultipartCreateType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobMultipartCreate")


@attr.s(auto_attribs=True, repr=False)
class BlobMultipartCreate:
    """  """

    _name: str
    _type: BlobMultipartCreateType
    _mime_type: Union[Unset, str] = "application/octet-stream"

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("mime_type={}".format(repr(self._mime_type)))
        return "BlobMultipartCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        type = self._type.value

        mime_type = self._mime_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "type": type,
            }
        )
        if mime_type is not UNSET:
            field_dict["mimeType"] = mime_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        type = BlobMultipartCreateType(d.pop("type"))

        mime_type = d.pop("mimeType", UNSET)

        blob_multipart_create = cls(
            name=name,
            type=type,
            mime_type=mime_type,
        )

        return blob_multipart_create

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> BlobMultipartCreateType:
        return self._type

    @type.setter
    def type(self, value: BlobMultipartCreateType) -> None:
        self._type = value

    @property
    def mime_type(self) -> str:
        if isinstance(self._mime_type, Unset):
            raise NotPresentError(self, "mime_type")
        return self._mime_type

    @mime_type.setter
    def mime_type(self, value: str) -> None:
        self._mime_type = value

    @mime_type.deleter
    def mime_type(self) -> None:
        self._mime_type = UNSET
