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

import fnmatch
import os
from pathlib import Path
import re
import subprocess

from typing import Iterable, Optional, Union

from . import contents_dict


tree_pattern = "{release}/{component}/Contents-{arch}.gz"


class contents_file:
    """ abstraction of a Contents file """

    def __init__(
        self,
        base: Union[str, Path],
        release: str,
        archs: Union[Iterable[str], str],
        sections: Optional[Union[Iterable[str], str]] = None,
        maxhits: Optional[int] = None,
    ):
        self.base = Path(base)
        self.release = release
        self.archs = archs if isinstance(archs, (list, tuple, set)) else [archs]

        if sections is None:
            sections = ["main"]
        if isinstance(sections, (list, tuple, set)):
            self.sections = sections
        else:
            self.sections = [sections]
        self.maxhits = maxhits

    def search(self, regexp: str) -> contents_dict.contents_dict:
        packages = contents_dict.contents_dict()
        errors = []
        for s in self.sections:
            for a in self.archs:
                filename = tree_pattern.format(
                    release=self.release,
                    component=s,
                    arch=a,
                )
                filepath = self.base / filename
                try:
                    packages.update(self._search_file(filepath, regexp))
                except IOError as e:
                    errors.append(str(e))
                except ContentsError as e:
                    errors.append(str(e))
        if len(errors) == len(self.sections) * len(self.archs):
            raise ContentsError(
                "Errors occurred trying to process request "
                "[%d]: %s" % (len(errors), "|".join(errors))
            )
        return packages

    def _search_file(self, filepath: Path, regexp: str) -> contents_dict.contents_dict:
        """
        Find the packages that provide files matching a particular regexp.
        """

        # validate that the regexp is OK before using
        try:
            re.compile(regexp, re.I)
        except re.error as e:
            raise ContentsError("Error in regexp: %s" % e, e) from e

        if not os.path.isfile(filepath):
            raise IOError("File %s not found." % filepath)

        try:
            # print("Trying: zgrep -iE -e '%s' '%s'" % (regexp, filepath))
            outbytes = subprocess.Popen(
                ["zgrep", "-iE", "-e", regexp, filepath],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=True,
                universal_newlines=False,
            ).communicate()[0]
            output = outbytes.decode("UTF-8")
        except TypeError as e:
            raise ContentsError("Could not look up file list") from e

        packages = contents_dict.contents_dict()
        try:
            lines = output.splitlines()
            if self.maxhits and len(lines) > self.maxhits:
                packages.results_truncated = True
            idx = 0
            for line in lines:
                try:
                    (filename, pkg_list) = line.split()
                    if filename == "FILE":
                        # This is the last line before the actual files.
                        continue
                except ValueError:  # Unpack list of wrong size.
                    continue  # We've not gotten to the files yet.
                packages.add(filename, pkg_list.split(","))
                idx += 1
                if self.maxhits and idx > self.maxhits:
                    break
        finally:
            pass
        return packages


class ContentsError(LookupError):
    pass


def glob2re(glob: str) -> str:
    anchored = glob.startswith("/")
    if anchored:
        glob = glob[1:]
    regexp = fnmatch.translate(glob)

    # zgrep doesn't like the (?s: ... ) construction so get rid of the ?s: part
    if regexp.startswith("(?s:"):
        regexp = "(" + regexp[4:]

    # and then tidy up the regexp to match the file format
    if anchored:
        regexp = "^" + regexp

    # Contents file has more data on the line, so munge EOL declarations
    # fnmatch in different versions of python does produces different regexps
    # so there is a need to try various different cases here
    if regexp.endswith(r"$"):
        regexp = regexp[:-1] + r"\s"
    elif regexp.endswith(r"\Z"):
        regexp = regexp[:-2] + r"\s"
    elif regexp.endswith(r"\Z(?ms)"):
        regexp = regexp[:-7] + r"\s"
    return regexp


def re2re(regexp: str) -> str:
    # tidy up the regexp to match the file format
    if regexp.startswith(r"^/"):
        regexp = "^" + regexp[2:]
    elif regexp.startswith(r"/"):
        regexp = "^" + regexp[1:]
    else:
        # unanchored pattern?
        regexp = "^[^ ]*" + regexp
    if regexp.endswith(r"$"):
        regexp = regexp[:-1] + r"\s"
    return regexp


def fixed2re(pattern: str) -> str:
    # turn a fixed string into a regexp that matches the file format
    regexp = r"^%s\s" % re.escape(pattern.lstrip(r"/"))
    return regexp


def pattern2re(pattern: str, mode: str) -> str:
    if mode == "glob":
        regexp = glob2re(pattern)
    elif mode in ("regex", "regexp"):
        regexp = re2re(pattern)
    elif mode in ("fixed", "exact"):
        regexp = fixed2re(pattern)
    else:
        ValueError("Unknown value of pattern match mode %s" % mode)

    return regexp
