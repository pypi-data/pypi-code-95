from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class ModuleOrPackageNotFound(ValueError):

    pass


class Module:
    def __init__(
        self,
        name: str,
        directory: str = ".",
        packages: Optional[List[Dict[str, Any]]] = None,
        includes: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        from poetry.core.utils.helpers import module_name

        from .include import Include
        from .package_include import PackageInclude

        self._name = module_name(name)
        self._in_src = False
        self._is_package = False
        self._path = Path(directory)
        self._includes = []
        packages = packages or []
        includes = includes or []

        if not packages:
            # It must exist either as a .py file or a directory, but not both
            pkg_dir = Path(directory, self._name)
            py_file = Path(directory, self._name + ".py")
            if pkg_dir.is_dir() and py_file.is_file():
                raise ValueError("Both {} and {} exist".format(pkg_dir, py_file))
            elif pkg_dir.is_dir():
                packages = [{"include": str(pkg_dir.relative_to(self._path))}]
            elif py_file.is_file():
                packages = [{"include": str(py_file.relative_to(self._path))}]
            else:
                # Searching for a src module
                src = Path(directory, "src")
                src_pkg_dir = src / self._name
                src_py_file = src / (self._name + ".py")

                if src_pkg_dir.is_dir() and src_py_file.is_file():
                    raise ValueError("Both {} and {} exist".format(pkg_dir, py_file))
                elif src_pkg_dir.is_dir():
                    packages = [
                        {
                            "include": str(src_pkg_dir.relative_to(src)),
                            "from": str(src.relative_to(self._path)),
                        }
                    ]
                elif src_py_file.is_file():
                    packages = [
                        {
                            "include": str(src_py_file.relative_to(src)),
                            "from": str(src.relative_to(self._path)),
                        }
                    ]
                else:
                    raise ModuleOrPackageNotFound(
                        "No file/folder found for package {}".format(name)
                    )

        for package in packages:
            formats = package.get("format")
            if formats and not isinstance(formats, list):
                formats = [formats]

            self._includes.append(
                PackageInclude(
                    self._path,
                    package["include"],
                    formats=formats,
                    source=package.get("from"),
                )
            )

        for include in includes:
            self._includes.append(
                Include(self._path, include["path"], formats=include["format"])
            )

    @property
    def name(self) -> str:
        return self._name

    @property
    def path(self) -> Path:
        return self._path

    @property
    def file(self) -> Path:
        if self._is_package:
            return self._path / "__init__.py"
        else:
            return self._path

    @property
    def includes(self) -> List:
        return self._includes

    def is_package(self) -> bool:
        return self._is_package

    def is_in_src(self) -> bool:
        return self._in_src
