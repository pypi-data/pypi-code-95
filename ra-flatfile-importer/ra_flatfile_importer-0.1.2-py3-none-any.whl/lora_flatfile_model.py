#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2021 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from itertools import chain
from typing import Any
from typing import Iterator
from typing import List
from typing import Optional

from pydantic import validator
from ramodels.lora import Facet
from ramodels.lora import Klasse
from ramodels.lora import LoraBase
from ramodels.lora import Organisation

from ra_flatfile_importer.semantic_version_type import SemanticVersion
from ra_flatfile_importer.util import FrozenBaseModel


__lora_fileformat_version__: SemanticVersion = SemanticVersion("0.1.0")
__supported_lora_fileformat_versions__: List[SemanticVersion] = list(
    map(SemanticVersion, ["0.1.0"])
)
assert (
    __lora_fileformat_version__ in __supported_lora_fileformat_versions__
), "Generated Lora version not supported"


class LoraFlatFileFormatChunk(FrozenBaseModel):
    """Flatfile chunk for LoRa.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is {}.
    """

    facetter: Optional[List[Facet]]
    klasser: Optional[List[Klasse]]
    organisation: Optional[Organisation]


class LoraFlatFileFormatImport(FrozenBaseModel):
    """Flatfile format for LoRa.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is [].
    """

    chunks: List[LoraFlatFileFormatChunk]
    version: SemanticVersion

    @validator("version", pre=True, always=True)
    def check_version(cls, v: Any) -> Any:
        if v not in __supported_lora_fileformat_versions__:
            raise ValueError("fileformat version not supported")
        return v

    def __len__(self) -> int:
        return len(self.chunks)

    def __iter__(self) -> Iterator[LoraFlatFileFormatChunk]:  # type: ignore
        return iter(self.chunks)

    def __getitem__(self, item: int) -> LoraFlatFileFormatChunk:
        return self.chunks[item]


class LoraFlatFileFormat(LoraFlatFileFormatImport):
    """Flatfile format for LoRa.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is [].
    """

    version: SemanticVersion = __lora_fileformat_version__


def concat_chunk(chunk: LoraFlatFileFormatChunk) -> Iterator[LoraBase]:
    """Convert a chunk to an iterator of objects."""
    return chain(
        [chunk.organisation] if chunk.organisation else [],
        chunk.facetter or [],
        chunk.klasser or [],
    )
