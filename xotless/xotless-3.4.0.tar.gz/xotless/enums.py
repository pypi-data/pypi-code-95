#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.tools.objects import FinalSubclassEnumeration


def DynamicClassEnumeration(superclass):  # pragma: no cover
    return FinalSubclassEnumeration(superclass, dynamic=True)
