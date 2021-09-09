#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
# Integrate with celery's SoftTimeLimitExceeded to avoid trapping that signal.
try:
    from billiard.exceptions import SoftTimeLimitExceeded
except ImportError:

    class SoftTimeLimitExceeded(Exception):  # noqa
        pass
