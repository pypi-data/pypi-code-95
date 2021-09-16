import base64
import enum
import io
from typing import Union, List, Optional

import pydantic
from PIL import Image
from classiq_interface.generator.generation_metadata import GenerationMetadata


class QuantumFormat(str, enum.Enum):
    QASM = "qasm"
    QSHARP = "qs"
    IONQ = "ionq"


class GenerationStatus(str, enum.Enum):
    NONE = "none"
    SUCCESS = "success"
    UNSAT = "unsat"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


class GeneratedCircuit(pydantic.BaseModel):
    qasm: Optional[str]
    qsharp: Optional[str]
    ionq: Optional[str]
    output_format: List[QuantumFormat]
    image: str
    metadata: GenerationMetadata

    def show(self) -> None:
        image = Image.open(io.BytesIO(base64.b64decode(self.image)))
        image.show()


class GenerationResult(pydantic.BaseModel):
    status: GenerationStatus
    details: Union[GeneratedCircuit, str]
