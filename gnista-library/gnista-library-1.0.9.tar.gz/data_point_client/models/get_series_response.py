from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..models.get_series_response_curve import GetSeriesResponseCurve
from ..types import UNSET, Unset

T = TypeVar("T", bound="GetSeriesResponse")


@attr.s(auto_attribs=True)
class GetSeriesResponse:
    """ """

    discriminator: str
    curve: Union[Unset, None, GetSeriesResponseCurve] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        curve: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.curve, Unset):
            curve = self.curve.to_dict() if self.curve else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if curve is not UNSET:
            field_dict["curve"] = curve

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        _curve = d.pop("curve", UNSET)
        curve: Union[Unset, None, GetSeriesResponseCurve]
        if _curve is None:
            curve = None
        elif isinstance(_curve, Unset):
            curve = UNSET
        else:
            curve = GetSeriesResponseCurve.from_dict(_curve)

        get_series_response = cls(
            discriminator=discriminator,
            curve=curve,
        )

        get_series_response.additional_properties = d
        return get_series_response

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
