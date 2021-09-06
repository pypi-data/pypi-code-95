from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="BasicSystemInformation")


@attr.s(auto_attribs=True)
class BasicSystemInformation:
    """ """

    bot_name: Union[Unset, str] = UNSET
    superadmin: Union[Unset, None, str] = UNSET
    org: Union[Unset, None, str] = UNSET
    org_id: Union[Unset, None, int] = UNSET
    bot_version: Union[Unset, str] = UNSET
    php_version: Union[Unset, str] = UNSET
    os: Union[Unset, str] = UNSET
    db_type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        bot_name = self.bot_name
        superadmin = self.superadmin
        org = self.org
        org_id = self.org_id
        bot_version = self.bot_version
        php_version = self.php_version
        os = self.os
        db_type = self.db_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if bot_name is not UNSET:
            field_dict["bot_name"] = bot_name
        if superadmin is not UNSET:
            field_dict["superadmin"] = superadmin
        if org is not UNSET:
            field_dict["org"] = org
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if bot_version is not UNSET:
            field_dict["bot_version"] = bot_version
        if php_version is not UNSET:
            field_dict["php_version"] = php_version
        if os is not UNSET:
            field_dict["os"] = os
        if db_type is not UNSET:
            field_dict["db_type"] = db_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        bot_name = d.pop("bot_name", UNSET)

        superadmin = d.pop("superadmin", UNSET)

        org = d.pop("org", UNSET)

        org_id = d.pop("org_id", UNSET)

        bot_version = d.pop("bot_version", UNSET)

        php_version = d.pop("php_version", UNSET)

        os = d.pop("os", UNSET)

        db_type = d.pop("db_type", UNSET)

        basic_system_information = cls(
            bot_name=bot_name,
            superadmin=superadmin,
            org=org,
            org_id=org_id,
            bot_version=bot_version,
            php_version=php_version,
            os=os,
            db_type=db_type,
        )

        basic_system_information.additional_properties = d
        return basic_system_information

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
