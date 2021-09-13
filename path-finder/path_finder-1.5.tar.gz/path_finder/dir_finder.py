from itertools import chain
from path_finder.base import FinderBase
from pathlib import Path
from typing import List

import logging
import re


logger = logging.getLogger(__name__)


class DirFinder(FinderBase):
    def __init__(
        self, dirname_regex: str = None, exclude_empty_dirs: bool = False, *args, **kwargs,
    ):
        self.dirname_regex = dirname_regex
        self.exclude_empty_dirs = exclude_empty_dirs
        self._paths = None
        self._paths_empty_dir = None
        self.validate_dirfinder_constructor()
        super().__init__(*args, **kwargs)

    def validate_dirfinder_constructor(self):
        # filename_regex is optional!!
        if self.dirname_regex and not isinstance(self.dirname_regex, str):
            raise AssertionError("dirname_regex must be a str")

    def _is_dir_path_regex_match(self, _path: Path) -> bool:
        return _path.is_dir() and re.match(pattern=self.dirname_regex, string=_path.stem)

    def _get_paths_from_single_dir(self, single_dir: Path) -> List[Path]:
        if self.limit_depth:
            # When we get all recursive paths with rglob('*') and then evaluate them may result in
            # potentially a lot of unnecessary work. Solution below is 'do it depth-by-depth': if e.g.
            # self.depth=2, then we get first all paths of depth=0, then depth=1, and then depth=2.
            # First, create an empty generator in which we will merge one generator per depth
            dir_paths_generator = chain()
            for _depth_n, glob_pattern in self.DEPTH_MAPPER.items():
                if _depth_n > self.depth:
                    break
                if self.dirname_regex:
                    only_dirs_generator = (
                        _path
                        for _path in single_dir.glob(glob_pattern)
                        if _path.is_dir() and re.match(pattern=self.dirname_regex, string=_path.stem)
                    )
                else:
                    only_dirs_generator = (_path for _path in single_dir.glob(glob_pattern) if _path.is_dir())
                # merge generators into one
                dir_paths_generator = chain(dir_paths_generator, only_dirs_generator)
            logger.debug("convert generator to list, this may take a while")
            return [x for x in dir_paths_generator]

        if not self.limit_depth:
            # note we use rglob (recursive search all subdirs)
            if self.dirname_regex:
                dir_paths_generator = (
                    _path
                    for _path in single_dir.rglob("*")
                    if _path.is_dir() and re.match(pattern=self.dirname_regex, string=_path.stem)
                )

            else:
                dir_paths_generator = (_path for _path in single_dir.rglob("*") if _path.is_dir())
            logger.debug("convert generator to list, this may take a while")
            return [x for x in dir_paths_generator]

    def _get_paths_from_multi_dir(self) -> List[Path]:
        nested_lists_with_paths = [
            self._get_paths_from_single_dir(single_dir=_dir_path) for _dir_path in self.multi_start_dir
        ]
        paths_from_multi_dir = [item for sublist in nested_lists_with_paths for item in sublist]
        return list(set(paths_from_multi_dir)) if paths_from_multi_dir else []

    @property
    def paths(self) -> List[Path]:
        if self._paths or self._paths == []:
            return self._paths

        # single dir
        if self.single_start_dir:
            self._paths = self._get_paths_from_single_dir(single_dir=self.single_start_dir)
            if self.exclude_empty_dirs:
                self._paths = [_path for _path in self._paths if any(_path.iterdir())]
            return self._paths

        # multi dir
        self._paths = self._get_paths_from_multi_dir()
        if self.exclude_empty_dirs:
            self._paths = [_path for _path in self._paths if any(_path.iterdir())]
        return self._paths

    @property
    def paths_empty_dir(self) -> List[Path]:
        """A selection of self.paths of dirs that hold no files."""
        if self._paths_empty_dir or self._paths_empty_dir == []:
            return self._paths_empty_dir
        elif self.exclude_empty_dirs:
            logger.info("paths_empty_dir is [] as search was done with exclude_empty_dirs=True")
            self._paths_empty_dir = []
            return self._paths_empty_dir
        self._paths_empty_dir = [_path for _path in self.paths if not any(_path.iterdir())]
        return self._paths_empty_dir
