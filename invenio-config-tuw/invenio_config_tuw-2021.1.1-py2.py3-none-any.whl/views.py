# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 - 2021 TU Wien.
#
# Invenio-Config-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

from flask import Blueprint

blueprint = Blueprint(
    "invenio_config_tuw",
    __name__,
    template_folder="templates",
)
