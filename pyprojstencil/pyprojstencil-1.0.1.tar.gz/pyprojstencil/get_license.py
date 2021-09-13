#!/usr/bin/env python3
# -*- coding:utf-8; mode:python; -*-
#
# Copyright 2021 Pradyumna Paranjape
# This file is part of pyprojstencil.
#
# pyprojstencil is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyprojstencil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pyprojstencil.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Define <LICENSE> <LICENSE_HEADER>
"""

from pathlib import Path
from typing import Tuple

from pyprojstencil import INFO_BASE
from pyprojstencil.errors import LicenseNotKnownError


def get_license(l_name: str = 'LGPLv3',
                return_blank: bool = False) -> Tuple[Path, str]:
    """
    Fetch License text and license header from name

    Args:
        l_name: license name {GPLv3,LGPLv3,MIT}
        return_blank: if license is not found, return Blank

    Returns:
        license path handle
        license header text (without modifications from template)

    Raises:
        LicenseNotKnownError: Provided license is not found

    """
    for license_h in INFO_BASE.templates.joinpath("licenses").glob("*"):
        if not license_h.is_file():
            continue
        if license_h.name == l_name:
            # found license text file
            header_h = license_h.with_stem(license_h.stem + "_header")
            if header_h.is_file():
                return license_h, header_h.read_text()
            return (license_h,
                    INFO_BASE.templates.joinpath(
                        "licenses/custom_header").read_text())
        elif license_h.name == l_name + "_header":
            # found header file
            text_h = license_h.with_stem(license_h.stem.replace("_header", ""))
            if text_h.is_file():
                return text_h, license_h.read_text()
            return (INFO_BASE.templates.joinpath("licenses/custom"),
                    license_h.read_text())
    if return_blank:
        return (
            INFO_BASE.templates.joinpath("licenses/custom"),
            INFO_BASE.templates.joinpath("licenses/custom_header").read_text())
    raise LicenseNotKnownError(l_name)
