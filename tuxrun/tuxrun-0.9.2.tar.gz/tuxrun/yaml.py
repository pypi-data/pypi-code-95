# -*- coding: utf-8 -*-
# vim: set ts=4
#
# Copyright 2021-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import yaml


try:
    from yaml import CFullLoader as FullLoader  # type: ignore
except ImportError:  # pragma: no cover
    try:
        from yaml import FullLoader
    except ImportError:
        from yaml import Loader as FullLoader

    print("Warning: using python yaml loader")


def yaml_load(data):
    return yaml.load(data, Loader=FullLoader)
