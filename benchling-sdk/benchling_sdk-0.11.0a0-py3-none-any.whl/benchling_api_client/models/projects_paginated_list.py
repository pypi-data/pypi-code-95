from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.project import Project

T = TypeVar("T", bound="ProjectsPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class ProjectsPaginatedList:
    """  """

    _next_token: str
    _projects: List[Project]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("projects={}".format(repr(self._projects)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ProjectsPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        projects = []
        for projects_item_data in self._projects:
            projects_item = projects_item_data.to_dict()

            projects.append(projects_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nextToken": next_token,
                "projects": projects,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        next_token = d.pop("nextToken")

        projects = []
        _projects = d.pop("projects")
        for projects_item_data in _projects:
            projects_item = Project.from_dict(projects_item_data)

            projects.append(projects_item)

        projects_paginated_list = cls(
            next_token=next_token,
            projects=projects,
        )

        projects_paginated_list.additional_properties = d
        return projects_paginated_list

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
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @property
    def projects(self) -> List[Project]:
        return self._projects

    @projects.setter
    def projects(self, value: List[Project]) -> None:
        self._projects = value
