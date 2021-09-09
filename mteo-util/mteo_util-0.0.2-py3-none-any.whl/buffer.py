#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# mteo-util.git:/src/mteo_util/buffer.py
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

from . import (
  tlv,
  typing,
)

## {{{ class Buffer

class Buffer:

  """Base class for ByteBuffer and StringBuffer"""

  _buf = None
  _len = None

  ## {{{ Buffer.__init__()
  def __init__(self, buf=None):
    if buf is None:
      self._buf = []
      self._len = 0
      return

    tlv.assert_types(buf, ['bytes', 'str'], arg='buf')

    self._buf = [buf]
    self._len = len(buf)
  ## }}}

  ## {{{ Buffer.clear()
  def clear(self):
    self._buf = []
    self._len = 0
  ## }}}

  ## {{{ Buffer.length()
  def length(self):
    return self._len
  ## }}}

## class Buffer }}}

## {{{ class ByteBuffer

class ByteBuffer(Buffer):

  ## {{{ ByteBuffer.__init()
  def __init__(self, buf=None):
    if buf is not None:
      tlv.assert_type(buf, 'bytes', arg='buf')

    super().__init__(buf)
  ## }}}

  ## {{{ ByteBuffer.append()
  def append(self, buf):
    tlv.assert_type(buf, 'bytes', arg='buf')

    self._buf.append(buf)
    self._len += len(buf)
  ## }}}

  ## {{{ ByteBuffer.value()
  def value(self):
    return b''.join(self._buf)
  ## }}}

  ## {{{ ByteBuffer.to_str()
  def to_str(self, encoding='utf-8'):
    tlv.assert_type(encoding, 'str', arg='encoding')

    return typing.to_str(self.value(), encoding)
  ## }}}

## class ByteBuffer }}}

## {{{ class StringBuffer

class StringBuffer(Buffer):

  ## {{{ StringBuffer.__init__()
  def __init__(self, buf=None):
    if buf is not None:
      tlv.assert_type(buf, 'str', arg='buf')

    super().__init__(buf)
  ## }}}

  ## {{{ StringBuffer.append()
  def append(self, buf):
    tlv.assert_type(buf, 'str', arg='buf')

    self._buf.append(buf)
    self._len += len(buf)
  ## }}}

  ## {{{ StringBuffer.value()
  def value(self):
    return ''.join(self._buf)
  ## }}}

  ## {{{ StringBuffer.to_bytes()
  def to_bytes(self, encoding='utf-8'):
    tlv.assert_type(encoding, 'str', arg='encoding')

    return typing.to_bytes(self.value(), encoding)
  ## }}}

## class StringBuffer }}}

##
# vim: ts=2 sw=2 tw=100 et fdm=marker :
##
