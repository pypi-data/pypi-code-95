#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/tests/test_typing.py
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

from .. import (
  to_bytes,
  to_str,
)

class TestTyping(unittest.TestCase):

  ## {{{ TestTyping.test_to_bytes()
  def test_to_bytes(self):
    self.assertTrue(to_bytes('foo') == b'foo')
  ## }}}

  ## {{{ TestTyping.test_to_str()
  def test_to_str(self):
    self.assertTrue(to_str(b'foo') == 'foo')
  ## }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
