#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/<FILE>
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

## {{{ class Bitmask

class Bitmask:

  _mask = None

  ## {{{ Bitmask.__init__()
  def __init__(self):
    self.reset()
  ## }}}

  ## {{{ Bitmask.reset()
  def reset(self):
    self._mask = 0
  ## }}}

  ## {{{ Bitmask.set()
  def set(self, bit):
    self._mask |= bit
  ## }}}

  ## {{{ Bitmask.clear()
  def clear(self, bit):
    self._mask &= ~bit
  ## }}}

  ## {{{ Bitmask.test()
  def test(self, bit):
    return self._mask & bit
  ## }}}

## class Bitmask }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
