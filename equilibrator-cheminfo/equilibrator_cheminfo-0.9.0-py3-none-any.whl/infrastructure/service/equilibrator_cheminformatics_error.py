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


"""Provide exception classes for the entire package."""


from typing import Iterable


class EquilibratorCheminformaticsError(Exception):
    """Define the base exception type for any error in the entire package."""

    def __init__(
        self, *, errors: Iterable[str] = (), warnings: Iterable[str] = (), **kwargs
    ) -> None:
        """Initialize the exception instance with multiple messages."""
        super().__init__(**kwargs)
        self.errors = list(errors)
        self.warnings = list(warnings)

    def __repr__(self) -> str:
        """Return a string representation of the exception."""
        return "\n".join([f"{idx}. {msg}" for idx, msg in enumerate(self.errors, 1)])
