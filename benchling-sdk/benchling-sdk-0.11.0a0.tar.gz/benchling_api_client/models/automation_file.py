from typing import Any, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.automation_file_automation_file_config import AutomationFileAutomationFileConfig
from ..models.automation_file_status import AutomationFileStatus
from ..models.blob import Blob
from ..types import UNSET, Unset

T = TypeVar("T", bound="AutomationFile")


@attr.s(auto_attribs=True, repr=False)
class AutomationFile:
    """  """

    _id: str
    _assay_run_id: Union[Unset, str] = UNSET
    _automation_file_config: Union[Unset, AutomationFileAutomationFileConfig] = UNSET
    _file: Union[Unset, None, Blob] = UNSET
    _status: Union[Unset, AutomationFileStatus] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("assay_run_id={}".format(repr(self._assay_run_id)))
        fields.append("automation_file_config={}".format(repr(self._automation_file_config)))
        fields.append("file={}".format(repr(self._file)))
        fields.append("status={}".format(repr(self._status)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AutomationFile({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        assay_run_id = self._assay_run_id
        automation_file_config: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._automation_file_config, Unset):
            automation_file_config = self._automation_file_config.to_dict()

        file: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._file, Unset):
            file = self._file.to_dict() if self._file else None

        status: Union[Unset, int] = UNSET
        if not isinstance(self._status, Unset):
            status = self._status.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if assay_run_id is not UNSET:
            field_dict["assayRunId"] = assay_run_id
        if automation_file_config is not UNSET:
            field_dict["automationFileConfig"] = automation_file_config
        if file is not UNSET:
            field_dict["file"] = file
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        assay_run_id = d.pop("assayRunId", UNSET)

        automation_file_config: Union[Unset, AutomationFileAutomationFileConfig] = UNSET
        _automation_file_config = d.pop("automationFileConfig", UNSET)
        if not isinstance(_automation_file_config, Unset):
            automation_file_config = AutomationFileAutomationFileConfig.from_dict(_automation_file_config)

        file = None
        _file = d.pop("file", UNSET)
        if _file is not None and not isinstance(_file, Unset):
            file = Blob.from_dict(_file)

        status = None
        _status = d.pop("status", UNSET)
        if _status is not None and _status is not UNSET:
            status = AutomationFileStatus(_status)

        automation_file = cls(
            id=id,
            assay_run_id=assay_run_id,
            automation_file_config=automation_file_config,
            file=file,
            status=status,
        )

        automation_file.additional_properties = d
        return automation_file

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
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def assay_run_id(self) -> str:
        if isinstance(self._assay_run_id, Unset):
            raise NotPresentError(self, "assay_run_id")
        return self._assay_run_id

    @assay_run_id.setter
    def assay_run_id(self, value: str) -> None:
        self._assay_run_id = value

    @assay_run_id.deleter
    def assay_run_id(self) -> None:
        self._assay_run_id = UNSET

    @property
    def automation_file_config(self) -> AutomationFileAutomationFileConfig:
        if isinstance(self._automation_file_config, Unset):
            raise NotPresentError(self, "automation_file_config")
        return self._automation_file_config

    @automation_file_config.setter
    def automation_file_config(self, value: AutomationFileAutomationFileConfig) -> None:
        self._automation_file_config = value

    @automation_file_config.deleter
    def automation_file_config(self) -> None:
        self._automation_file_config = UNSET

    @property
    def file(self) -> Optional[Blob]:
        if isinstance(self._file, Unset):
            raise NotPresentError(self, "file")
        return self._file

    @file.setter
    def file(self, value: Optional[Blob]) -> None:
        self._file = value

    @file.deleter
    def file(self) -> None:
        self._file = UNSET

    @property
    def status(self) -> AutomationFileStatus:
        if isinstance(self._status, Unset):
            raise NotPresentError(self, "status")
        return self._status

    @status.setter
    def status(self, value: AutomationFileStatus) -> None:
        self._status = value

    @status.deleter
    def status(self) -> None:
        self._status = UNSET
