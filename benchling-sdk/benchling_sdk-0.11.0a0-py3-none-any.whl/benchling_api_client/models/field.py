from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.field_type import FieldType
from ..models.field_value import FieldValue
from ..types import UNSET, Unset

T = TypeVar("T", bound="Field")


@attr.s(auto_attribs=True, repr=False)
class Field:
    """  """

    _value: Union[None, str, bool, float, FieldValue, List[str]]
    _display_value: Union[Unset, None, str] = UNSET
    _is_multi: Union[Unset, bool] = UNSET
    _text_value: Union[Unset, None, str] = UNSET
    _type: Union[Unset, FieldType] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("display_value={}".format(repr(self._display_value)))
        fields.append("is_multi={}".format(repr(self._is_multi)))
        fields.append("text_value={}".format(repr(self._text_value)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("value={}".format(repr(self._value)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "Field({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        display_value = self._display_value
        is_multi = self._is_multi
        text_value = self._text_value
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        value: Union[None, str, bool, float, Dict[str, Any], List[Any]]
        if isinstance(self._value, Unset):
            value = UNSET
        if self._value is None:
            value = None
        elif isinstance(self._value, FieldValue):
            value = self._value.to_dict()

        elif isinstance(self._value, list):
            value = self._value

        else:
            value = self._value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )
        if display_value is not UNSET:
            field_dict["displayValue"] = display_value
        if is_multi is not UNSET:
            field_dict["isMulti"] = is_multi
        if text_value is not UNSET:
            field_dict["textValue"] = text_value
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        display_value = d.pop("displayValue", UNSET)

        is_multi = d.pop("isMulti", UNSET)

        text_value = d.pop("textValue", UNSET)

        type = None
        _type = d.pop("type", UNSET)
        if _type is not None and _type is not UNSET:
            type = FieldType(_type)

        def _parse_value(
            data: Union[None, str, bool, float, Dict[str, Any], List[Any]]
        ) -> Union[None, str, bool, float, FieldValue, List[str]]:
            value: Union[None, str, bool, float, FieldValue, List[str]]
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                value = FieldValue.from_dict(data)

                return value
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value = cast(List[str], data)

                return value
            except:  # noqa: E722
                pass
            return cast(Union[None, str, bool, float, FieldValue, List[str]], data)

        value = _parse_value(d.pop("value"))

        field = cls(
            display_value=display_value,
            is_multi=is_multi,
            text_value=text_value,
            type=type,
            value=value,
        )

        field.additional_properties = d
        return field

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
    def display_value(self) -> Optional[str]:
        if isinstance(self._display_value, Unset):
            raise NotPresentError(self, "display_value")
        return self._display_value

    @display_value.setter
    def display_value(self, value: Optional[str]) -> None:
        self._display_value = value

    @display_value.deleter
    def display_value(self) -> None:
        self._display_value = UNSET

    @property
    def is_multi(self) -> bool:
        if isinstance(self._is_multi, Unset):
            raise NotPresentError(self, "is_multi")
        return self._is_multi

    @is_multi.setter
    def is_multi(self, value: bool) -> None:
        self._is_multi = value

    @is_multi.deleter
    def is_multi(self) -> None:
        self._is_multi = UNSET

    @property
    def text_value(self) -> Optional[str]:
        if isinstance(self._text_value, Unset):
            raise NotPresentError(self, "text_value")
        return self._text_value

    @text_value.setter
    def text_value(self, value: Optional[str]) -> None:
        self._text_value = value

    @text_value.deleter
    def text_value(self) -> None:
        self._text_value = UNSET

    @property
    def type(self) -> FieldType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: FieldType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def value(self) -> Optional[Union[str, bool, float, FieldValue, List[str]]]:
        return self._value

    @value.setter
    def value(self, value: Optional[Union[str, bool, float, FieldValue, List[str]]]) -> None:
        self._value = value
