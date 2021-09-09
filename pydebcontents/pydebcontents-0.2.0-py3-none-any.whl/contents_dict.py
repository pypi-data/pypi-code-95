###
# Copyright (c) 2010-2021  Stuart Prescott
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

""" Contents file results parsing """

from collections import defaultdict
import collections.abc
from typing import Any, Callable, Iterable, List, Mapping, Tuple, Union, overload


class contents_dict(defaultdict[str, List[str]]):
    """
    Manage a mapping of filenames to packages that contain them

    Stores data as a dictionary
        packagename: [filename1, filename2, ...]

    Note that this is inverted compared to the Contents file
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.separator = "; "
        self.results_truncated = False
        super().__init__(list, *args, **kwargs)

    def add(self, filename: str, packagelist: List[str]) -> None:
        """ Add a file and set of packages containing that file"""
        for pack in packagelist:
            self[pack].append(filename)

    # Messy set of overloads to handle all different variations

    @overload
    def update(self, __m: Mapping[str, List[str]], **kwargs: List[str]) -> None:
        ...

    @overload
    def update(self, __m: Iterable[Tuple[str, List[str]]], **kwargs: List[str]) -> None:
        ...

    @overload
    def update(self, **kwargs: List[str]) -> None:
        ...

    def update(
        self,
        *args: Union[Iterable[Tuple[str, List[str]]], Mapping[str, List[str]]],
        **kwargs: List[str]
    ) -> None:
        def _extend(source: Iterable[Tuple[str, List[str]]]) -> None:
            for pack, files in source:
                self[pack].extend(files)

        for source in args:
            # import metadata
            if isinstance(source, contents_dict):
                self.results_truncated |= source.results_truncated

            # import data
            if isinstance(source, collections.abc.Mapping):
                _extend(source.items())
            elif isinstance(source, collections.abc.Sequence):
                _extend(source)

        _extend(kwargs.items())

    def to_string(self, boldfn: Callable[[str], str]) -> str:
        """ Turn the list into a condensed one-line string output """
        sbuild = []
        # sort the packages so that packages that contain the shortest paths
        # (by number of path elements, /) come first.
        pprio = sorted(self.keys(), key=lambda p: min([f.count("/") for f in self[p]]))
        for pack in pprio:
            name = pack.rpartition("/")[-1]
            sbuild.append("%s: %s" % (boldfn(name), ", ".join(self[pack])))
        return self.separator.join(sbuild)

    def __str__(self) -> str:
        """ Turn the list into a condensed one-line string (simple) """
        sbuild = []
        for pack in self.keys():
            # either section/package (shells/bash) or
            # component/section/package (non-free/editors/axe)
            name = pack.rpartition("/")[-1]
            sbuild.append("%s: %s" % (name, ", ".join(self[pack])))
        return self.separator.join(sbuild)
