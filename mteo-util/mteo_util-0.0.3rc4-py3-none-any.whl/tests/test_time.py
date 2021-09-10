#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/tests/test_time.py
##

## {{{ ---- [ Header ] -----------------------------------------------------------------------------

##
# Copyright (c) 2021 Francis M <francism@destinatech.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2.0 as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to:
#
#   Free Software Foundation
#   51 Franklin Street, Fifth Floor
#   Boston, MA 02110
#   USA
##

## }}} ---- [ Header ] -----------------------------------------------------------------------------

import unittest

import time

from .. import (
  time_now,
  time_diff,
)

class TestTime(unittest.TestCase):

  ## {{{ TestTime.test_time_now()
  def test_time_now(self):
    self.assertTrue(type(time_now()) == type(int()))
    self.assertTrue(time_now() > 0)

    t1 = int(time.time())
    t2 = time_now()
    self.assertTrue(t1 == t2 or t1 + 1 == t2)
  ## }}}

  ## {{{ TestTime.test_time_diff()
  def test_time_diff(self):
    now = time_now()
    self.assertTrue(time_diff(now, now) == 0)
    then = now - 5
    self.assertTrue(time_diff(now, then) == 5)
  ## }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
