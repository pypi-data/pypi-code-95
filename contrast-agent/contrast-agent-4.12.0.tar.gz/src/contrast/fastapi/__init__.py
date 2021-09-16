# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

if sys.version_info >= (3, 7):
    from .middleware import FastApiMiddleware as ContrastMiddleware  # noqa
else:
    raise ImportError("Contrast Agent supports FastAPI for Python 3.7+ only")
