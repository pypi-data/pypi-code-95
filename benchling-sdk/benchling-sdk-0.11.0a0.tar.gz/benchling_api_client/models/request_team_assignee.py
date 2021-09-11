from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.team_summary import TeamSummary

T = TypeVar("T", bound="RequestTeamAssignee")


@attr.s(auto_attribs=True, repr=False)
class RequestTeamAssignee:
    """  """

    _team: TeamSummary
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("team={}".format(repr(self._team)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTeamAssignee({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        team = self._team.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "team": team,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        team = TeamSummary.from_dict(d.pop("team"))

        request_team_assignee = cls(
            team=team,
        )

        request_team_assignee.additional_properties = d
        return request_team_assignee

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
    def team(self) -> TeamSummary:
        return self._team

    @team.setter
    def team(self, value: TeamSummary) -> None:
        self._team = value
