from typing import Any, Dict, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.blob_create_type import BlobCreateType
from ..types import UNSET, Unset

T = TypeVar("T", bound="BlobCreate")


@attr.s(auto_attribs=True, repr=False)
class BlobCreate:
    """  """

    _data64: str
    _md5: str
    _name: str
    _type: BlobCreateType
    _mime_type: Union[Unset, str] = "application/octet-stream"

    def __repr__(self):
        fields = []
        fields.append("data64={}".format(repr(self._data64)))
        fields.append("md5={}".format(repr(self._md5)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("mime_type={}".format(repr(self._mime_type)))
        return "BlobCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        data64 = self._data64
        md5 = self._md5
        name = self._name
        type = self._type.value

        mime_type = self._mime_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data64": data64,
                "md5": md5,
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
        data64 = d.pop("data64")

        md5 = d.pop("md5")

        name = d.pop("name")

        type = BlobCreateType(d.pop("type"))

        mime_type = d.pop("mimeType", UNSET)

        blob_create = cls(
            data64=data64,
            md5=md5,
            name=name,
            type=type,
            mime_type=mime_type,
        )

        return blob_create

    @property
    def data64(self) -> str:
        return self._data64

    @data64.setter
    def data64(self, value: str) -> None:
        self._data64 = value

    @property
    def md5(self) -> str:
        return self._md5

    @md5.setter
    def md5(self, value: str) -> None:
        self._md5 = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def type(self) -> BlobCreateType:
        return self._type

    @type.setter
    def type(self, value: BlobCreateType) -> None:
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
