from typing import Any, Dict, Type, TypeVar

import attr

T = TypeVar("T", bound="AutomationOutputProcessorUpdate")


@attr.s(auto_attribs=True, repr=False)
class AutomationOutputProcessorUpdate:
    """  """

    _file_id: str

    def __repr__(self):
        fields = []
        fields.append("file_id={}".format(repr(self._file_id)))
        return "AutomationOutputProcessorUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        file_id = self._file_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "fileId": file_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        file_id = d.pop("fileId")

        automation_output_processor_update = cls(
            file_id=file_id,
        )

        return automation_output_processor_update

    @property
    def file_id(self) -> str:
        return self._file_id

    @file_id.setter
    def file_id(self, value: str) -> None:
        self._file_id = value
