# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import json
from pathlib import Path


class InvalidTuxMakeBuild(Exception):
    pass


class TuxMakeBuild:
    Invalid = InvalidTuxMakeBuild

    def __init__(self, directory):
        self.location = Path(directory).resolve()
        metadata_file = self.location / "metadata.json"
        if not self.location.is_dir():
            raise self.Invalid(f"{directory} is not a directory")
        if not metadata_file.exists():
            raise self.Invalid(
                f"{directory} is not a valid TuxMake artifacts directory: missing metadata.json"
            )

        try:
            metadata = json.load(metadata_file.open())
        except json.JSONDecodeError as e:
            raise self.Invalid(f"Invalid metadata.json: {e}")

        try:
            self.kernel = self.location / metadata["results"]["artifacts"]["kernel"][0]
        except KeyError:
            self.kernel = None
        try:
            self.modules = (
                self.location / metadata["results"]["artifacts"]["modules"][0]
            )
        except KeyError:
            self.modules = None
        self.target_arch = metadata["build"]["target_arch"]
