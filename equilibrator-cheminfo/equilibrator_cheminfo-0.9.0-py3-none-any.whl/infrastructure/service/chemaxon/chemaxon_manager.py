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


"""Provide a singleton class that manages the JVM and access to ChemAxon."""


from __future__ import annotations

import os
from pathlib import Path

import jpype

from ..singleton import Singleton


class ChemAxonManager(metaclass=Singleton):
    """
    Define a class that manages the Java virtual machine and access to ChemAxon.

    JPype attaches one JVM instance per Python process. Thus a per process Python
    singleton seems ideal to manage that resource.

    """

    def __init__(self, *args, **kwargs) -> None:
        """
        Initialize the manager by starting the JVM.

        Modifies the Java class path by adding all ChemAxon jar archives. Then starts
        the JVM passing all received arguments to that method.

        Raises
        ------
        RuntimeError
            If the CHEMAXON_HOME environment variable is not set.
        OSError
            If the JVM fails to start.

        """
        assert (
            not jpype.isJVMStarted()
        ), "There is already a JVM running in this process."
        super().__init__()
        # We add all ChemAxon jar files to the JVM class path.
        if "CHEMAXON_HOME" not in os.environ:
            raise RuntimeError(
                "The environment variable CHEMAXON_HOME *must* be defined."
            )
        path = Path(os.environ["CHEMAXON_HOME"]) / "marvinsuite" / "lib" / "*"
        jpype.addClassPath(str(path))
        jpype.startJVM(*args, **kwargs)
        self._chemaxon = jpype.JPackage("chemaxon")

    @property
    def chemaxon(self) -> jpype.JPackage:
        """Return the ChemAxon Java package."""
        return self._chemaxon
