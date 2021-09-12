# Copyright (c) 2021, Moritz E. Beber.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Define general helper functions."""


import re
from typing import Match

from depinfo import print_dependencies


charges_pattern = re.compile(r"[+-]{2,}")


def show_versions():
    """Print dependency information."""
    print_dependencies("equilibrator-cheminfo")


def shorten_string(string: str, width: int = 20) -> str:
    """Return a copy of the string shortened to the specified width (minimum 6)."""
    assert width > 6
    return string if len(string) <= width else f"{string[:(width - 6)]} [...]"


def _replace_charges(match: Match) -> str:
    """Replace the matched charge symbols with a numeric version."""
    charges = match.group()
    return f"{charges[0]}{len(charges)}"


def normalize_charges(string: str) -> str:
    """Replace multiple charge symbols in the string with a charge and number."""
    return charges_pattern.sub(
        lambda match: f"{match.group()[0]}{len(match.group())}", string
    )
