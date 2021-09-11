from typing import Any, Dict, List, Optional, Type, TypeVar

import attr

from ..models.folder import Folder

T = TypeVar("T", bound="FoldersPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class FoldersPaginatedList:
    """  """

    _folders: List[Folder]
    _next_token: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("folders={}".format(repr(self._folders)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FoldersPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folders = []
        for folders_item_data in self._folders:
            folders_item = folders_item_data.to_dict()

            folders.append(folders_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "folders": folders,
                "nextToken": next_token,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        folders = []
        _folders = d.pop("folders")
        for folders_item_data in _folders:
            folders_item = Folder.from_dict(folders_item_data)

            folders.append(folders_item)

        next_token = d.pop("nextToken")

        folders_paginated_list = cls(
            folders=folders,
            next_token=next_token,
        )

        folders_paginated_list.additional_properties = d
        return folders_paginated_list

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
    def folders(self) -> List[Folder]:
        return self._folders

    @folders.setter
    def folders(self, value: List[Folder]) -> None:
        self._folders = value

    @property
    def next_token(self) -> str:
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value
