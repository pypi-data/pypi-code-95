from itertools import chain
from path_finder.base import FinderBase
from pathlib import Path
from typing import List

import logging
import re


logger = logging.getLogger(__name__)


class FileFinder(FinderBase):
    """An interface for finding files. It combines best of both worlds glob/rglob (speed) and regex (flexibility):
    Mandatory arguments:
        'extension' (str)                       To filter files by extension.
        'single_start_dir' (pathlib.Path)       Either use single_start_dir or multi_start_dir. The search starts here.
        'multi_start_dir' (List[pathlib.Path])  Either use single_start_dir or multi_start_dir. The search starts
                                                from multiple start locations (one after another).
    Optional arguments:
        'limit_depth' (bool)                    To limit the recursive search depth.
        'depth' (int)                           To limit the recursive search depth.
        'filename_regex' (str)                  A regex to find filename e.g. "^[0-9]{8}_HistTags$"

    Example:
        single_start_dir    = pathlib.Path('this_is_my_start_dir')
        limit_depth         = True
        depth               = 0  # <-- 0 so do not search in possible subdirs
        filename_regex      = "^[0-9]{8}_HistTags$"
        extension           = '.csv'

        file_finder = FileFinder(
                            single_start_dir=single_start_dir,
                            extension=extension,
                            limit_depth=True,
                            depth=depth,
                            filename_regex=filename_regex
                            )

        paths = file_finder.paths
        paths_empty_files = file_finder.paths_empty_file

    """

    ALL_EXTENSIONS = "*"
    EXTENTION_CHOICES = (
        ".jpg",
        ".png",
        ".txt",
        ".xml",
        ".csv",
        ".xls",
        ".xlsx",
        ".pdf",
        ".h5",
        ".nc",
        ".zip",
        ".env",
        ".doc",
        ".docx",
        ".ods",
        ".ppt",
        ".pptx",
        ".rst",
        ".cfg",
        ".py",
    )

    def __init__(self, extension: str, filename_regex: str = None, *args, **kwargs):
        self.extension = extension if extension else ""
        self.filename_regex = filename_regex
        self.validate_filefinder_constructor()
        self._paths = None
        self._paths_empty_file = None
        super().__init__(*args, **kwargs)

    def validate_filefinder_constructor(self) -> None:
        if not isinstance(self.extension, str):
            raise AssertionError("extension must either be None or a str")
        if self.extension not in self.EXTENTION_CHOICES and self.extension != self.ALL_EXTENSIONS:
            raise AssertionError(f"extension {self.extension} must either be None or a str in {self.EXTENTION_CHOICES}")

        # filename_regex is optional!!
        if self.filename_regex and not isinstance(self.filename_regex, str):
            raise AssertionError("filename_regex must be a str")

    def _get_paths_from_single_dir(self, single_dir: Path) -> List[Path]:

        if self.limit_depth:
            file_paths_generator = chain()
            for _depth_n, glob_pattern in self.DEPTH_MAPPER.items():
                if _depth_n > self.depth:
                    break

                if self.filename_regex:
                    only_files_generator = (
                        _path
                        for _path in single_dir.glob(glob_pattern + self.extension)
                        if _path.is_file() and re.match(pattern=self.filename_regex, string=_path.stem)
                    )
                else:
                    only_files_generator = (
                        _path for _path in single_dir.glob(glob_pattern + self.extension) if _path.is_file()
                    )
                # merge generators into one
                file_paths_generator = chain(file_paths_generator, only_files_generator)
            logger.debug("convert generator to list, this may take a while")
            return [x for x in file_paths_generator]

        if not self.limit_depth:
            # note we use rglob (recursive search all subdirs)
            if self.filename_regex:
                file_paths_generator = (
                    _path
                    for _path in single_dir.rglob(f"*{self.extension}")
                    if _path.is_file() and re.match(pattern=self.filename_regex, string=_path.stem)
                )
            else:
                file_paths_generator = (_path for _path in single_dir.rglob(f"*{self.extension}") if _path.is_file())
            logger.debug("convert generator to list, this may take a while")
            return [x for x in file_paths_generator]

    def _get_paths_from_multi_dir(self) -> List[Path]:
        nested_lists_with_paths = [
            self._get_paths_from_single_dir(single_dir=_dir_path) for _dir_path in self.multi_start_dir
        ]
        paths_from_multi_dir = [item for sublist in nested_lists_with_paths for item in sublist]
        return paths_from_multi_dir if paths_from_multi_dir else []

    @property
    def paths(self) -> List[Path]:
        if self._paths or self._paths == []:
            return self._paths
        if self.single_start_dir:
            self._paths = self._get_paths_from_single_dir(single_dir=self.single_start_dir)
        elif self.multi_start_dir:
            self._paths = self._get_paths_from_multi_dir()
        return self._paths

    @property
    def paths_empty_file(self) -> List[Path]:
        """A selection of self.paths of files that are empty (filesize=0kb)."""
        if self._paths_empty_file or self._paths_empty_file == []:
            return self._paths_empty_file
        self._paths_empty_file = [_path for _path in self.paths if _path.stat().st_size == 0]
        return self._paths_empty_file
