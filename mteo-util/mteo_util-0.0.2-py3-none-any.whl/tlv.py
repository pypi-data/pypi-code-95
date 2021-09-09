#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/tlv.py
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

## {{{ assert_type()
def assert_type(obj, type_name, arg=None):
  obj_type = type(obj)
  if obj_type.__name__ == type_name:
    return

  message = f'invalid type (expecting {type_name}, got {obj_type.__name__})'
  if arg:
    message = arg + ': ' + message

  raise TypeError(message)
## }}}

## {{{ assert_types()
def assert_types(obj, type_names, arg=None):
  for type_name in type_names:
    obj_type = type(obj)
    if obj_type.__name__ == type_name:
      return

  type_names_str = '/'.join(type_names)
  message = f'invalid type (expecting {type_names_str}, got {obj_type.__name__})'
  if arg:
    message = arg + ': ' + message

  raise TypeError(message)
## }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
