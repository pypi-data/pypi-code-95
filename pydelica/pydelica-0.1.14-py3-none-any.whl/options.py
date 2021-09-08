import collections.abc
import tempfile
import os
import enum
import logging
import glob
import platform
import defusedxml.ElementTree as ET

from pydelica.exception import UnknownOptionError, UnknownLibraryError

from typing import Any, Iterable, List


class Solver(enum.Enum):
    DASSL = "dassl"
    EULER = "euler"
    RUNGE_KUTTA = "rungekutta"


class LibrarySetup:
    """Object containing setup for a particular Modelica library version"""
    def __init__(self, library_folder: str = None) -> None:
        """Create a setup object

        Parameters
        ----------
        library_folder : str, optional
            specify location of the Modelica libraries, else use system defaults
        """
        self._logger = logging.getLogger("PyDelica.LibrarySetup")

        # Disable environment setting on Windows as it does not work at present
        if platform.system() != "Windows":
            self._libraries = self._get_library_folders(library_folder)
            self._session_library = tempfile.mkdtemp()
            self._copy_libraries()

    def _copy_libraries(self) -> None:
        for library in self._libraries:
            _dest = os.path.join(
                self._session_library, os.path.basename(library)
            )

            if not os.path.exists(_dest):
                os.symlink(library, _dest)

    def use_library(self, library_name: str, version: str) -> None:
        """Use a specific library version

        This function looks through all library directories (symlinks) and
        checks which match the requested library. The version number of the
        directory is then compared to requested version and us symlinked, other
        versions are unlinked.

        Parameters
        ----------
        library_name : str
            library to select
        version : str
            version requested

        Raises
        ------
        UnknownLibraryError
            if the library and version are not recognised
        """
        _test_str = f"{library_name} {version}"
        self._logger.debug(f"Selecting Library '{_test_str}'")

        if not any(_test_str in i for i in self._libraries):
            raise UnknownLibraryError(
                f"Cannot import library '{library_name}' version '{version}', "
                "library not found."
            )
        for library in self._libraries:
            # If library does not contain requested library name ignore
            # and continue
            if library_name.lower() not in library.lower():
                continue

            # Create the address for the symlink
            _new_lib = os.path.join(
                self._session_library, os.path.basename(library)
            )

            _split_name = os.path.basename(library).lower().split()

            # If the split name is length 1 this means there is no
            # version string anyway
            if len(_split_name) < 2:
                continue

            _name, _version = _split_name

            # Check that the name matches the requested library name
            if library_name.lower().strip() == _name.lower().strip():
                # Check the version matches the requested version
                # if it does ensure this is symlinked, if not unlink it
                if version.lower().strip() == _version.lower().strip():
                    if not os.path.exists(_new_lib):
                        self._logger.debug(f"Linking: {library} -> {_new_lib}")
                        os.symlink(library, _new_lib)
                else:
                    if os.path.exists(_new_lib):
                        self._logger.debug(
                            f"Unlinking: {_new_lib} -> {library}"
                        )
                        os.unlink(_new_lib)

    def get_library(self) -> str:
        return self._session_library

    def _get_library_folders(self, library_folder: str = None) -> List[str]:
        if library_folder:
            _library_dir = library_folder
        elif platform.system() == "Windows":
            _library_dir = os.environ["OPENMODELICALIBRARY"]
        else:
            _library_dir = "/usr/lib/omlibrary"
        return glob.glob(os.path.join(_library_dir, "*"))


class SimulationOptions(collections.abc.MutableMapping):
    """
    Simulation Options
    ------------------

    Object contains configuration settings for simulation within Modelica
    """
    def __init__(self, xml_model_file: str) -> None:
        """Create a configuration object from a given model XML file

        Parameters
        ----------
        xml_model_file : str
            file containing the parameters and configurations from a model
            after compilation

        Raises
        ------
        FileNotFoundError
            if the specified XML file does not exist
        """
        self._model_xml = xml_model_file

        if not os.path.exists(xml_model_file):
            raise FileNotFoundError(
                "Could not extract simulation options, "
                f"no such file '{xml_model_file}"
            )

        with open(xml_model_file) as f:
            _xml_obj = ET.parse(xml_model_file)

        self._opts = list(_xml_obj.iterfind("DefaultExperiment"))[0].attrib

    def _write_opts(self) -> None:
        _xml_obj = ET.parse(self._model_xml)

        for opt in _xml_obj.findall("DefaultExperiment")[0].attrib:
            _xml_obj.findall("DefaultExperiment")[0].attrib[opt] = str(
                self._opts[opt]
            )

        _xml_obj.write(self._model_xml)

    def __setitem__(self, key: str, value: Any) -> None:
        self._opts[key] = value
        self._write_opts()

    def __getitem__(self, key: str) -> Any:
        return self._opts[key]

    def __delitem__(self, key: str) -> None:
        del self._opts[key]

    def set_option(self, option_name: str, value: Any) -> None:
        """Set the value of an option

        Parameters
        ----------
        option_name : str
            name of option to update
        value : Any
            new value for option

        Raises
        ------
        UnknownOptionError
            if the option does not exist
        """
        if option_name not in self._opts:
            raise UnknownOptionError(option_name)
        _opt = [
            i for i in self._opts.keys() if i.lower() == option_name.lower()
        ][0]
        self._opts[_opt] = value
        self._write_opts()

    def __len__(self) -> int:
        return len(self._opts)

    def __iter__(self) -> Iterable:
        return iter(self._opts)
