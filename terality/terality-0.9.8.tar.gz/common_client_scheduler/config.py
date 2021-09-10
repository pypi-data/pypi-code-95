from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from terality_serde import SerdeMixin


@dataclass
class TransferConfigLocal(SerdeMixin):
    path: Path


@dataclass
class SessionInfoLocal(SerdeMixin):
    id: str  # pylint: disable=invalid-name
    upload_config: TransferConfigLocal
    download_config: TransferConfigLocal


@dataclass
class TransferConfig(SerdeMixin):
    default_aws_region: str
    bucket: str
    key_prefix: str

    def bucket_region(self, aws_region: Optional[str] = None) -> str:
        """Return the name of the upload bucket in the given region."""
        return f"{self.bucket}-{self.default_aws_region if aws_region is None else aws_region}"


@dataclass
class SessionInfo(SerdeMixin):
    id: str  # pylint: disable=invalid-name
    upload_config: Union[TransferConfig, TransferConfigLocal]
    download_config: Union[TransferConfig, TransferConfigLocal]
