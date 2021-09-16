"""
Module where you can get paths used in your project or configure paths to be able other modules here
in mypythontools with PROJECT_PATHS. You can also use `find_path()` to find some path efficiently in
some folder, excluding some other inner folders (like venv, node_modules etc.).There is also function
to get desktop path in posix way.
"""
from pathlib import Path
import sys
import builtins
from typing import Union, List

import mylogging


class _ProjectPaths:
    """You can find paths, that are lazy evaluated only after you ask for them. They are inferred automatically,
    but if you have alternative structure, you can also set it. Getters return path objects, so it's posix.

    Note:
        If you use paths in `sys.path.insert` or as subprocess main parameter, do not forget to convert it
        to string with `.as_posix()`."""

    def __init__(self) -> None:
        self._root_path: Union[None, Path] = None
        self._app_path = None
        self._init_path = None
        self._test_path = None
        self._docs_path = None
        self._readme_path = None

    def add_ROOT_PATH_to_sys_path(self) -> None:
        if self.ROOT_PATH.as_posix() not in sys.path:
            sys.path.insert(0, self.ROOT_PATH.as_posix())

    @property
    def ROOT_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Path where all project is (docs, tests...). Root is usually current working directory."""

        # If not value yet, set it first
        if not self._root_path:
            self.ROOT_PATH = "infer"

        return self._root_path

    @ROOT_PATH.setter
    def ROOT_PATH(self, new_path: Union[str, Path]) -> None:

        if new_path == "infer":
            new_root_path = Path.cwd()

            # If using jupyter notebook from tests - very specific use case
            if new_root_path.name == "tests" and hasattr(builtins, "__IPYTHON__"):
                new_root_path = new_root_path.parent

        else:
            new_root_path = new_path

        self._root_path = validate_path(new_root_path)

    @property
    def INIT_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Path to __init__.py."""

        if not self._init_path:
            self.INIT_PATH = "infer"

        return self._init_path

    @INIT_PATH.setter
    def INIT_PATH(self, new_path: Union[str, Path]) -> None:
        if new_path == "infer":
            exclude = []
            for i in ["DOCS_PATH", "TEST_PATH"]:
                try:
                    exclude.append(getattr(self, i))
                except Exception:
                    pass

            self._init_path = validate_path(
                find_path(
                    "__init__.py",
                    self.ROOT_PATH,
                    exclude_paths=exclude,
                )
            )
        else:
            self._init_path = validate_path(new_path)

    @property
    def APP_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Folder where python scripts are (and __init__.py)."""

        if not self._app_path:
            self.APP_PATH = "infer"

        return self._app_path

    @APP_PATH.setter
    def APP_PATH(self, new_path: Union[str, Path]) -> None:
        if new_path == "infer":
            self._app_path = self.INIT_PATH.parent
        else:
            self._app_path = validate_path(new_path)

    @property
    def TEST_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Folder where tests are stored. Usually ROOT_PATH / tests."""

        if not self._test_path:
            self.TEST_PATH = "infer"

        return self._test_path

    @TEST_PATH.setter
    def TEST_PATH(self, new_path: Union[str, Path]) -> None:
        if new_path == "infer":
            root_pathlib = Path(self.ROOT_PATH)

            for i in ["tests", "test", "Test", "Tests", "TEST", "TESTS"]:
                if (root_pathlib / i).exists():
                    new_path = root_pathlib / i
                    break

        self._test_path = validate_path(new_path)

    @property
    def DOCS_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Where documentation is stored. Usually ROOT_PATH / docs."""

        if not self._docs_path:
            self.DOCS_PATH = "infer"

        return self._docs_path

    @DOCS_PATH.setter
    def DOCS_PATH(self, new_path: Union[str, Path]) -> None:
        if new_path == "infer":
            for i in ["doc", "docs", "Doc", "Docs", "DOC", "DOCS"]:
                if (self.ROOT_PATH / i).exists():
                    new_path = self.ROOT_PATH / i
                    break

        self._docs_path = validate_path(new_path)

    @property
    def README_PATH(self) -> Path:
        """
        Type:
            str

        Default:
            None

        Where README is stored and whether it's capitalized or not."""

        if not self._readme_path:
            self.README_PATH = "infer"

        return self._readme_path

    @README_PATH.setter
    def README_PATH(self, new_path: Union[str, Path]) -> None:
        if new_path == "infer":
            if (self.ROOT_PATH / "README.md").exists():
                new_readme_path = self.ROOT_PATH / "README.md"

            elif (self.ROOT_PATH / "Readme.md").exists():
                new_readme_path = self.ROOT_PATH / "Readme.md"

            elif (self.ROOT_PATH / "readme.md").exists():
                new_readme_path = self.ROOT_PATH / "readme.md"

        else:
            new_readme_path = new_path

        self._readme_path = validate_path(new_readme_path)

    def reset_paths(self):
        self._root_path = None
        self._app_path = None
        self._init_path = None
        self._test_path = None
        self._docs_path = None
        self._readme_path = None


PROJECT_PATHS = _ProjectPaths()


def find_path(
    file: str,
    folder: Union[str, Path] = None,
    exclude_names: List[str] = ["node_modules", "build", "dist"],
    exclude_paths: List[Union[str, Path]] = [],
    levels: int = 5,
):
    """Search for file in defined folder (cwd() by default) and return it's path.

    Args:
        file (str): Name with extension e.g. "app.py".
        folder (str, optional): Where to search. If None, then ROOT_PATH is used (cwd by default). Defaults to None.
        exclude_names ((str, Path), optional): List of ignored names. If this name is whenever in path, it will be ignored.
            Defaults to ['node_modules', 'build', 'dist'].
        exclude_paths (List[Union[str, Path]], optional): List of ignored paths. If defined path is subpath of found file,
            it will be ignored. If relative, it has to be from cwd. Defaults to [].
        levels (str, optional): Recursive number of analyzed folders. Defaults to 5.

    Returns:
        Path: Path of file.

    Raises:
        FileNotFoundError: If file is not found.
    """

    folder = PROJECT_PATHS.ROOT_PATH if not folder else validate_path(folder)

    for lev in range(levels):
        glob_file_str = f"{'*/' * lev}{file}"

        for i in folder.glob(glob_file_str):
            isthatfile = True
            for j in exclude_names:
                if j in i.parts:
                    isthatfile = False
                    break

            if isthatfile:
                for j in exclude_paths:
                    excluded_name = Path(j).resolve()
                    if i.as_posix().startswith(excluded_name.as_posix()):
                        isthatfile = False
                        break

            if isthatfile:
                return i

    # If not returned - not found
    raise FileNotFoundError(mylogging.return_str(f"File `{file}` not found"))


def get_desktop_path():
    """Get desktop path.

    Returns:
        Path: Return pathlib Path object. If you want string, use `.as_posix()`

    Example:
        >>> desktop_path = get_desktop_path()
        >>> desktop_path.exists() and "Desktop" in desktop_path.as_posix()
        True
    """
    return Path.home() / "Desktop"


def validate_path(path: Union[str, Path]):
    """Convert to pathlib path, resolve to full path and check if exists.

    Args:
        path ((str, Path)): Validated path.

    Raises:
        FileNotFoundError: If file do not exists.

    Returns:
        Path: Pathlib Path object.

    Example:
        >>> from pathlib import Path
        >>> existing_path = validate_path(Path.cwd())
        >>> non_existing_path = validate_path("not_existing")
        Traceback (most recent call last):
        FileNotFoundError: ...
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(mylogging.return_str(f"File nor folder found on defined path {path}"))
    return path
