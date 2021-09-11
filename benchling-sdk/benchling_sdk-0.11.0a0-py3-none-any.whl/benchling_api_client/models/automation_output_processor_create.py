from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="AutomationOutputProcessorCreate")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorCreate:
    """  """

    _assay_run_id: str
    _automation_file_config_name: str
    _file_id: str

    def __repr__(self):
        fields = []
        fields.append("assay_run_id={}".format(repr(self._assay_run_id)))
        fields.append("automation_file_config_name={}".format(repr(self._automation_file_config_name)))
        fields.append("file_id={}".format(repr(self._file_id)))
        return "AutomationOutputProcessorCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        assay_run_id = self._assay_run_id
        automation_file_config_name = self._automation_file_config_name
        file_id = self._file_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "assayRunId": assay_run_id,
                "automationFileConfigName": automation_file_config_name,
                "fileId": file_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        assay_run_id = d.pop("assayRunId")

        automation_file_config_name = d.pop("automationFileConfigName")

        file_id = d.pop("fileId")

        automation_output_processor_create = cls(
            assay_run_id=assay_run_id,
            automation_file_config_name=automation_file_config_name,
            file_id=file_id,
        )

        return automation_output_processor_create

    @property
    def assay_run_id(self) -> str:
        return self._assay_run_id

    @assay_run_id.setter
    def assay_run_id(self, value: str) -> None:
        self._assay_run_id = value

    @property
    def automation_file_config_name(self) -> str:
        return self._automation_file_config_name

    @automation_file_config_name.setter
    def automation_file_config_name(self, value: str) -> None:
        self._automation_file_config_name = value

    @property
    def file_id(self) -> str:
        return self._file_id

    @file_id.setter
    def file_id(self, value: str) -> None:
        self._file_id = value
