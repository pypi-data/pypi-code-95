from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="Player")


@attr.s(auto_attribs=True)
class Player:
    """This represents the data the bot stores about a player in the cache and database"""

    charid: Union[Unset, int] = UNSET
    first_name: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    last_name: Union[Unset, str] = UNSET
    level: Union[Unset, None, int] = UNSET
    breed: Union[Unset, str] = UNSET
    gender: Union[Unset, str] = UNSET
    faction: Union[Unset, str] = UNSET
    profession: Union[Unset, None, str] = UNSET
    prof_title: Union[Unset, str] = UNSET
    ai_rank: Union[Unset, str] = UNSET
    ai_level: Union[Unset, None, int] = UNSET
    org_id: Union[Unset, None, int] = UNSET
    org: Union[Unset, None, str] = UNSET
    org_rank: Union[Unset, None, str] = UNSET
    org_rank_id: Union[Unset, None, int] = UNSET
    dimension: Union[Unset, None, int] = UNSET
    head_id: Union[Unset, None, int] = UNSET
    pvp_rating: Union[Unset, None, int] = UNSET
    pvp_title: Union[Unset, None, str] = UNSET
    last_update: Union[Unset, None, int] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        charid = self.charid
        first_name = self.first_name
        name = self.name
        last_name = self.last_name
        level = self.level
        breed = self.breed
        gender = self.gender
        faction = self.faction
        profession = self.profession
        prof_title = self.prof_title
        ai_rank = self.ai_rank
        ai_level = self.ai_level
        org_id = self.org_id
        org = self.org
        org_rank = self.org_rank
        org_rank_id = self.org_rank_id
        dimension = self.dimension
        head_id = self.head_id
        pvp_rating = self.pvp_rating
        pvp_title = self.pvp_title
        last_update = self.last_update

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if charid is not UNSET:
            field_dict["charid"] = charid
        if first_name is not UNSET:
            field_dict["first_name"] = first_name
        if name is not UNSET:
            field_dict["name"] = name
        if last_name is not UNSET:
            field_dict["last_name"] = last_name
        if level is not UNSET:
            field_dict["level"] = level
        if breed is not UNSET:
            field_dict["breed"] = breed
        if gender is not UNSET:
            field_dict["gender"] = gender
        if faction is not UNSET:
            field_dict["faction"] = faction
        if profession is not UNSET:
            field_dict["profession"] = profession
        if prof_title is not UNSET:
            field_dict["prof_title"] = prof_title
        if ai_rank is not UNSET:
            field_dict["ai_rank"] = ai_rank
        if ai_level is not UNSET:
            field_dict["ai_level"] = ai_level
        if org_id is not UNSET:
            field_dict["org_id"] = org_id
        if org is not UNSET:
            field_dict["org"] = org
        if org_rank is not UNSET:
            field_dict["org_rank"] = org_rank
        if org_rank_id is not UNSET:
            field_dict["org_rank_id"] = org_rank_id
        if dimension is not UNSET:
            field_dict["dimension"] = dimension
        if head_id is not UNSET:
            field_dict["head_id"] = head_id
        if pvp_rating is not UNSET:
            field_dict["pvp_rating"] = pvp_rating
        if pvp_title is not UNSET:
            field_dict["pvp_title"] = pvp_title
        if last_update is not UNSET:
            field_dict["last_update"] = last_update

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        charid = d.pop("charid", UNSET)

        first_name = d.pop("first_name", UNSET)

        name = d.pop("name", UNSET)

        last_name = d.pop("last_name", UNSET)

        level = d.pop("level", UNSET)

        breed = d.pop("breed", UNSET)

        gender = d.pop("gender", UNSET)

        faction = d.pop("faction", UNSET)

        profession = d.pop("profession", UNSET)

        prof_title = d.pop("prof_title", UNSET)

        ai_rank = d.pop("ai_rank", UNSET)

        ai_level = d.pop("ai_level", UNSET)

        org_id = d.pop("org_id", UNSET)

        org = d.pop("org", UNSET)

        org_rank = d.pop("org_rank", UNSET)

        org_rank_id = d.pop("org_rank_id", UNSET)

        dimension = d.pop("dimension", UNSET)

        head_id = d.pop("head_id", UNSET)

        pvp_rating = d.pop("pvp_rating", UNSET)

        pvp_title = d.pop("pvp_title", UNSET)

        last_update = d.pop("last_update", UNSET)

        player = cls(
            charid=charid,
            first_name=first_name,
            name=name,
            last_name=last_name,
            level=level,
            breed=breed,
            gender=gender,
            faction=faction,
            profession=profession,
            prof_title=prof_title,
            ai_rank=ai_rank,
            ai_level=ai_level,
            org_id=org_id,
            org=org,
            org_rank=org_rank,
            org_rank_id=org_rank_id,
            dimension=dimension,
            head_id=head_id,
            pvp_rating=pvp_rating,
            pvp_title=pvp_title,
            last_update=last_update,
        )

        player.additional_properties = d
        return player

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
