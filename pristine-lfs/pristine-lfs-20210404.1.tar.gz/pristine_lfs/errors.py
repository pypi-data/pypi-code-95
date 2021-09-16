# pristine-lfs
#
# errors for pristine-lfs
#
# Copyright (C) 2021 Collabora Ltd
# Copyright (C) 2021 Andrej Shadura <andrew.shadura@collabora.co.uk>
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

from gettext import gettext as _

from sh import ErrorReturnCode as CommandFailed  # noqa: F401


class DifferentFilesExist(Exception):
    files: list[str]

    def __init__(self, files: list[str]):
        self.files = files

    def __str__(self):
        return _("would overwrite files: {files}").format(files=', '.join(self.files))


class UnsupportedHashAlgorithm(Exception):
    algo: str

    def __init__(self, algo: str):
        self.algo = algo

    def __str__(self):
        return _("unsupported hash algorithm {algo}").format(
            algo=self.algo,
        )


class GitError(Exception):
    pass


class GitFileNotFound(GitError):
    filename: str
    branch: str

    def __init__(self, filename: str, branch: str):
        self.filename = filename
        self.branch = branch

    def __str__(self):
        return _('{filename} not found on branch {branch}').format(
            filename=self.filename,
            branch=self.branch,
        )


class GitBranchNotFound(GitError):
    branch: str

    def __init__(self, branch: str):
        self.branch = branch

    def __str__(self):
        return _('No branch {branch} found, not even among remote branches').format(
            branch=self.branch,
        )
