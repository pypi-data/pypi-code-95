#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/tests/test_os.py
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
  OsUser,
  OsGroup,
)

class TestOsUser(unittest.TestCase):

  ## {{{ TestOsUser.test_init_name_kwarg()
  def test_init_name_kwarg(self):
    user = OsUser(name='root')
    self.assertTrue(user.name == 'root')
    self.assertTrue(user.passwd == 'x')
    self.assertTrue(user.uid == 0)
    self.assertTrue(user.gid == 0)
  ## }}}

  ## {{{ TestOsGroup.test_init_uid_kwarg()
  def test_init_uid_kwarg(self):
    user = OsUser(uid=0)
    self.assertTrue(user.name == 'root')
    self.assertTrue(user.passwd == 'x')
    self.assertTrue(user.uid == 0)
    self.assertTrue(user.gid == 0)
  ## }}}

class TestOsGroup(unittest.TestCase):

  ## {{{ TestOsGroup.test_init_name_kwarg()
  def test_init_name_kwarg(self):
    group = OsGroup(name='root')
    self.assertTrue(group.name == 'root')
    self.assertTrue(group.passwd == 'x')
    self.assertTrue(group.gid == 0)
  ## }}}

  ## {{{ TestOsGroup.test_init_uid_kwarg()
  def test_init_uid_kwarg(self):
    group = OsGroup(gid=0)
    self.assertTrue(group.name == 'root')
    self.assertTrue(group.passwd == 'x')
    self.assertTrue(group.gid == 0)
  ## }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
