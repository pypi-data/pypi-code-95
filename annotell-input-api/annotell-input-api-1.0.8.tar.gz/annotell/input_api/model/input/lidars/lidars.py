from dataclasses import field, dataclass
from typing import Union, Mapping

from annotell.input_api.model.input.lidars_and_cameras.frame import Frame


@dataclass
class Lidars:
    external_id: str
    frame: Frame
    metadata: Mapping[str, Union[int, float, str, bool]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(frame=self.frame.to_dict(),
                    externalId=self.external_id,
                    metadata=self.metadata)
