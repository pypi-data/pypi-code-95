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
from ramodels.mo import Employee
from ramodels.mo import MOBase
from ramodels.mo import OrganisationUnit
from ramodels.mo.details import Address
from ramodels.mo.details import Engagement
from ramodels.mo.details import EngagementAssociation
from ramodels.mo.details import Manager

from ra_flatfile_importer.semantic_version_type import SemanticVersion
from ra_flatfile_importer.util import FrozenBaseModel

__mo_fileformat_version__: SemanticVersion = SemanticVersion("0.1.0")
__supported_mo_fileformat_versions__: List[SemanticVersion] = list(
    map(SemanticVersion, ["0.1.0"])
)
assert (
    __mo_fileformat_version__ in __supported_mo_fileformat_versions__
), "Generated MO version not supported"


class MOFlatFileFormatChunk(FrozenBaseModel):
    """Flatfile chunk for OS2mo.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is {}.
    """

    org_units: Optional[List[OrganisationUnit]]
    employees: Optional[List[Employee]]
    engagements: Optional[List[Engagement]]
    address: Optional[List[Address]]
    manager: Optional[List[Manager]]
    engagement_associations: Optional[List[EngagementAssociation]]


class MOFlatFileFormatImport(FrozenBaseModel):
    """Flatfile format for OS2mo.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is [].
    """

    chunks: List[MOFlatFileFormatChunk]
    version: SemanticVersion

    @validator("version", pre=True, always=True)
    def check_version(cls, v: Any) -> Any:
        if v not in __supported_mo_fileformat_versions__:
            raise ValueError("fileformat version not supported")
        return v

    def __len__(self) -> int:
        return len(self.chunks)

    def __iter__(self) -> Iterator[MOFlatFileFormatChunk]:  # type: ignore
        return iter(self.chunks)

    def __getitem__(self, item: int) -> MOFlatFileFormatChunk:
        return self.chunks[item]


class MOFlatFileFormat(MOFlatFileFormatImport):
    """Flatfile format for OS2mo.

    Each chunk in the list is send as bulk / in parallel, and as such entries
    within a single chunk should not depend on other entries within the same chunk.

    Minimal valid example is [].
    """

    version: SemanticVersion = __mo_fileformat_version__


def concat_chunk(chunk: MOFlatFileFormatChunk) -> Iterator[MOBase]:
    """Convert a chunk to an iterator of objects."""
    return chain(
        chunk.org_units or [],
        chunk.employees or [],
        chunk.engagements or [],
        chunk.address or [],
        chunk.manager or [],
        chunk.engagement_associations or [],
    )
