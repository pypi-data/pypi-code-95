from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="BlobPartCreate")


@attr.s(auto_attribs=True, repr=False)
class BlobPartCreate:
    """  """

    _data64: str
    _md5: str
    _part_number: int

    def __repr__(self):
        fields = []
        fields.append("data64={}".format(repr(self._data64)))
        fields.append("md5={}".format(repr(self._md5)))
        fields.append("part_number={}".format(repr(self._part_number)))
        return "BlobPartCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        data64 = self._data64
        md5 = self._md5
        part_number = self._part_number

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "data64": data64,
                "md5": md5,
                "partNumber": part_number,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data64 = d.pop("data64")

        md5 = d.pop("md5")

        part_number = d.pop("partNumber")

        blob_part_create = cls(
            data64=data64,
            md5=md5,
            part_number=part_number,
        )

        return blob_part_create

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
    def part_number(self) -> int:
        return self._part_number

    @part_number.setter
    def part_number(self, value: int) -> None:
        self._part_number = value
