from dataclasses import dataclass, field

from typing import List, Mapping, Union
from annotell.input_api.model.input.lidars_sequence.frame import Frame


@dataclass
class LidarsSequence:
    external_id: str
    frames: List[Frame]
    metadata: Mapping[str, Union[int, float, str]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return dict(frames=[frame.to_dict() for frame in self.frames],
                    externalId=self.external_id,
                    metadata=self.metadata)
