import glob
import logging
import os
import platform
import shutil
import subprocess
import tempfile
from typing import List

import pydelica.exception as pde
from pydelica.options import LibrarySetup


class Compiler:
    """Performs compilation of Modelica using the OMC compiler"""
    def __init__(self, open_modelica_library_path: str = None) -> None:
        """Initialise a compiler object

        Parameters
        ----------
        open_modelica_library_path : str, optional
            location of the OM libraries, else use defaults for system

        Raises
        ------
        pde.BinaryNotFoundError
            if an OMC compiler binary could not be found
        """
        self._logger = logging.getLogger("PyDelica.Compiler")
        self._environment = os.environ.copy()
        self._library = LibrarySetup(open_modelica_library_path)
        if "OPENMODELICAHOME" in os.environ:
            _omc_cmd = "omc.exe" if platform.system() == "Windows" else "omc"
            self._omc_binary = os.path.join(
                os.environ["OPENMODELICAHOME"], "bin", _omc_cmd
            )
        elif shutil.which("omc"):
            self._omc_binary = shutil.which("omc")
        else:
            raise pde.BinaryNotFoundError("Failed to find OMC binary")

        if platform.system() == "Windows":
            _mod_tool_bin = os.path.join(
                os.environ["OPENMODELICAHOME"],
                "tools",
                "msys",
                "mingw64",
                "bin",
            )
            self._environment["PATH"] = (
                f"{_mod_tool_bin}" + os.pathsep + self._environment["PATH"]
            )
            self._environment["PATH"] = (
                f"{os.path.dirname(self._omc_binary)}"
                + os.pathsep
                + self._environment["PATH"]
            )
        self._logger.debug(f"Using Compiler: {self._omc_binary}")

    def compile(
        self,
        modelica_source_file: str,
        model_addr: str = None,
        extra_models: List[str] = None
    ) -> str:
        """Compile Modelica source file

        Parameters
        ----------
        modelica_source_file : str
            Modelica source file to compile
        model_addr : str, optional
            Model within source file to compile, default is first found
        extra_models: List[str], optional
            Additional other model dependencies

        Returns
        -------
        str
            location of output binary
        """

        _temp_dir = tempfile.mkdtemp()

        _current_wd = os.getcwd()

        modelica_source_file = os.path.abspath(modelica_source_file)

        if not os.path.exists(modelica_source_file):
            raise FileNotFoundError(
                f"Could not compile Modelica file '{modelica_source_file}',"
                " file does not exist"
            )

        _args = [self._omc_binary, "-s", modelica_source_file]

        if extra_models:
            for model in extra_models:
                model = os.path.join(os.path.dirname(modelica_source_file), model)
                if not os.path.exists(model):
                    raise FileNotFoundError(
                        f"Could not compile supplementary Modelica file '{model}',"
                        " file does not exist"
                    )
                _args.append(model)

        _args.append("Modelica")

        if self._logger.getEffectiveLevel() == logging.DEBUG:
            _args.append("-d")

        if model_addr:
            _args.append(f"+i={model_addr}")

        _cmd_str = " ".join(_args)

        self._logger.debug(f"Executing Command: {_cmd_str}")

        os.chdir(_temp_dir)

        _gen = None

        # Disable environment setting on Windows as it does not work at present
        if platform.system() == "Windows":
            _environ = None
        else:
            _environ = os.environ.copy()
            _environ["OPENMODELICALIBRARY"] = self._library.get_library()

        try:
            _gen = subprocess.run(
                _args,
                shell=False,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                env=_environ,
            )

            pde.parse_error_string_compiler(_gen.stdout, _gen.stderr)
        except FileNotFoundError as e:
            self._logger.error("Failed to run command '%s'", _cmd_str)
            self._logger.debug("PATH: %s", self._environment["PATH"])
            if _gen:
                self._logger.error("Traceback: %s", _gen.stdout)
            raise e
        except pde.OMExecutionError as e:
            self._logger.error("Failed to run command '%s'", _cmd_str)
            if _gen:
                self._logger.error("Traceback: %s", _gen.stdout)
            raise e
        except pde.OMBuildError as e:
            if "lexer failed" in e.args[0]:
                self._logger.warning(e.args[0])
            else:
                if _gen:
                    self._logger.error("Traceback: %s", _gen.stdout)
                raise e

        self._logger.debug(_gen.stdout)

        if _gen and _gen.stderr:
            self._logger.error(_gen.stderr)

        _make_file = glob.glob(os.path.join(_temp_dir, "*.makefile"))

        if not _make_file:
            self._logger.error(
                "Output directory contents [%s]: %s",
                _temp_dir,
                os.listdir(_temp_dir),
            )
            raise pde.ModelicaFileGenerationError(
                f"Failed to find a Makefile in the directory: {_temp_dir}, "
                "Modelica failed to generated required files."
            )

        _make_file = _make_file[0]

        if platform.system() == "Windows":
            _make_cmd = os.path.join(
                os.environ["OPENMODELICAHOME"],
                "share",
                "omc",
                "scripts",
                "Compile.bat",
            )
            _make_file = os.path.basename(_make_file)
            _build_cmd = [
                _make_cmd,
                os.path.splitext(_make_file)[0],
                "gcc",
                "mingw64",
                "parallel",
                "4",
                "0",
            ]

        elif not shutil.which("make"):
            raise pde.BinaryNotFoundError(
                f"Could not find GNU-Make on this system"
            )
        else:
            _make_cmd = shutil.which("make")
            _build_cmd = [_make_cmd, "-f", _make_file]

        self._logger.debug(f"Build Command: {' '.join(_build_cmd)}")

        _build = subprocess.run(
            _build_cmd,
            shell=False,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            env=self._environment,
        )

        try:
            pde.parse_error_string_compiler(_build.stdout, _build.stderr)
        except pde.OMBuildError as e:
            self._logger.error(_build.stderr)
            raise e

        if _build.stdout:
            self._logger.debug(_build.stdout)

        if _gen.stderr:
            self._logger.error(_build.stderr)

        os.chdir(_current_wd)

        return _temp_dir
