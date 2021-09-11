from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

T = TypeVar("T", bound="BarcodeValidationResult")


@attr.s(auto_attribs=True, repr=False)
class BarcodeValidationResult:
    """  """

    _barcode: str
    _is_valid: bool
    _message: Optional[str]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("barcode={}".format(repr(self._barcode)))
        fields.append("is_valid={}".format(repr(self._is_valid)))
        fields.append("message={}".format(repr(self._message)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "BarcodeValidationResult({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        barcode = self._barcode
        is_valid = self._is_valid
        message = self._message

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "barcode": barcode,
                "isValid": is_valid,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        barcode = d.pop("barcode")

        is_valid = d.pop("isValid")

        message = d.pop("message")

        barcode_validation_result = cls(
            barcode=barcode,
            is_valid=is_valid,
            message=message,
        )

        barcode_validation_result.additional_properties = d
        return barcode_validation_result

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
    def barcode(self) -> str:
        return self._barcode

    @barcode.setter
    def barcode(self, value: str) -> None:
        self._barcode = value

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool) -> None:
        self._is_valid = value

    @property
    def message(self) -> Optional[str]:
        return self._message

    @message.setter
    def message(self, value: Optional[str]) -> None:
        self._message = value
